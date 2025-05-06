# -*- coding: utf-8 -*-
"""
Created on Tue Apr  1 13:31:48 2025

@author: TEM
"""

from pylablib.devices import Andor
import matplotlib.pyplot as plt
import h5py
from datetime import datetime
import os
import pandas as pd

'''
0: Full Vertical Binning

1: Multi-Track

2: Random-Track

3: Single-Track

4: Image
'''

class Cam:
    def __init__(self, name, data_path, temp=-80, read_mode = 4):
        """
        Initialize the camera with specified parameters.

        Parameters
        ----------
        name : str
            Name identifier for the camera.
        data_path : str
            Directory path where data will be saved.
        temp : int, optional
            Target temperature for the camera in Celsius. Default is -80.
        """
        self.temp = temp
        self.cam = self.initalize_camera()
        self.set_temperature(temp)
        self.cam.set_read_mode(read_mode)
        if read_mode == 0:
            mode = "full vertical binning"
        if read_mode == 1:
            mode = "Multi-track"
        if read_mode == 2:
            mode = "random-track"
        if read_mode == 3:
            mode = "single-Track"
        if read_mode == 4:
            mode = "Image"
        print(f"read mode set to {mode}")
        
        self.name = name
        self.data_path = data_path
        if not os.path.exists(self.data_path):
            os.makedirs(self.data_path)
        self.logbook_path = os.path.join(data_path, "andor_logbook.ods")
    
    def initalize_camera(self):
        return Andor.AndorSDK2Camera(temperature=self.temp, fan_mode="full")
        pass

    def get_temp(self):
        """Return current sensor temperature in °C, or None if unreadable."""
        try:
            return self.cam.get_temperature()
        except Exception:
            return None

        
    def set_temperature(self, temperature, enable_cooler=True):
        """
        Set the camera's temperature setpoint.
    
        Parameters
        ----------
        temperature : float
            Desired temperature in degrees Celsius.
        enable_cooler : bool, optional
            Whether to enable the cooler (default is True).
        """
        self.cam.set_temperature(temperature, enable_cooler=enable_cooler)
        print(f"Temperature setpoint set to {temperature}°C. Cooler enabled: {enable_cooler}")

    def set_exposure(self, exposure):
        """
        Set the camera's exposure time.

        Parameters
        ----------
        exposure : float
            Exposure time in seconds.
        """
        self.cam.set_exposure(exposure)
        self.exposure = exposure

    def set_roi(self, roi=(0, 512, 0, 512)):
        """
        Set the Region of Interest (ROI) for the camera.

        Parameters
        ----------
        roi : tuple
            Tuple specifying (hstart, hend, vstart, vend).
        """
        hstart, hend, vstart, vend = roi
        self.cam.set_roi(hstart, hend, vstart, vend)

    def set_em_gain(self, em_gain):
        """
        Set the Electron Multiplying (EM) gain.

        Parameters
        ----------
        em_gain : int
            EM gain value.
        """
        self.cam.set_EMCCD_gain(em_gain)
        print(f"EM gain set to {em_gain}")

    def set_shutter(self, mode="auto", ttl_mode=0, open_time=None, close_time=None):
        """
        Configure the shutter settings.

        Parameters
        ----------
        mode : str
            Shutter mode: 'auto', 'open', or 'closed'.
        ttl_mode : int
            TTL logic level: 0 for low is open, 1 for high is open.
        open_time : float or None
            Shutter opening time in seconds.
        close_time : float or None
            Shutter closing time in seconds.
        """
        self.cam.setup_shutter(mode=mode, ttl_mode=ttl_mode, open_time=open_time, close_time=close_time)
        print(f"Shutter configured: mode={mode}, TTL mode={ttl_mode}, open_time={open_time}, close_time={close_time}")

    def get_shutter(self):
        """
        Retrieve the current shutter configuration.

        Returns
        -------
        dict
            Dictionary containing the current shutter settings.
        """
        mode, ttl_mode, open_time, close_time = self.cam.get_shutter_parameters()
        return {
            "mode": mode,
            "ttl_mode": ttl_mode,
            "open_time": open_time,
            "close_time": close_time
        }

    def acquire_single(self, save=True):
        """
        Acquire a single image.

        Parameters
        ----------
        save : bool, optional
            Whether to save the image. Default is True.

        Returns
        -------
        ndarray
            Acquired image as a 2D NumPy array.
        """
        image = self.cam.snap(timeout=self.exposure + 2)
        if save:
            self.save_to_h5(image, f"{self.name}")
        return image

    def acquire_and_plot(self, cmap='gray', vmin=None, vmax=None, save=True):
        """
        Acquire and plot a single image with matplotlib.

        Parameters
        ----------
        cmap : str, optional
            Colormap for the image. Default is 'gray'.
        vmin : float, optional
            Minimum data value that corresponds to colormap's lower limit.
        vmax : float, optional
            Maximum data value that corresponds to colormap's upper limit.
        save : bool, optional
            Whether to save the image. Default is True.

        Returns
        -------
        ndarray
            Acquired image as a 2D NumPy array.
        """
        image = self.acquire_single(save=False)
        plt.imshow(image, cmap=cmap, vmin=vmin, vmax=vmax)
        plt.title("Single Image")
        plt.colorbar(label="ADU")
        plt.xlabel("X Pixels")
        plt.ylabel("Y Pixels")
        plt.show()
        if save:
            self.save_to_h5(image, f"{self.name}")
        return image

    def save_to_h5(self, image, base_filename="andor_image", comment="NA"):
        """
        Save a single image and metadata to an HDF5 file.

        Parameters
        ----------
        image : ndarray
            2D NumPy array from `acquire_single()`.
        base_filename : str, optional
            Base name for the output .h5 file. Default is 'andor_image'.
        comment : str, optional
            Comment to include in the metadata. Default is 'NA'.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        iso_timestamp = datetime.now().isoformat()
        filename = f"{base_filename}_{timestamp}.h5"
        filename = os.path.join(self.data_path, filename)

        with h5py.File(filename, "w") as f:
            dset = f.create_dataset("image", data=image)
            dset.attrs["exposure_time_sec"] = self.cam.get_exposure()
            dset.attrs["em_gain"] = self.cam.get_EMCCD_gain()[0]
            dset.attrs["temperature_C"] = self.cam.get_temperature()
            dset.attrs["timestamp"] = iso_timestamp

            meta = f.create_group("metadata")
            meta.attrs["camera_model"] = self.cam.get_device_info()[1]
            meta.attrs["sensor_size"] = self.cam.get_detector_size()
            meta.attrs["readout_mode"] = self.cam.get_read_mode()
            meta.attrs["roi"] = self.cam.get_roi()
            meta.attrs["exposure_time_sec"] = self.cam.get_exposure()
            meta.attrs["em_gain"] = self.cam.get_EMCCD_gain()[0]
            meta.attrs["temperature_C"] = self.cam.get_temperature()
            meta.attrs["timestamp"] = iso_timestamp
            meta.attrs["comment"] = comment

        
        image_metadata = {
            "timestamp": iso_timestamp,
            "exposure_time_sec": self.cam.get_exposure(),
            "em_gain": self.cam.get_EMCCD_gain()[0],
            "temperature_C": self.cam.get_temperature(),
            "camera_model": self.cam.get_device_info()[1],
            "roi": self.cam.get_roi(),
            "comment": comment
        }
        self.log_to_ods(filename, image_metadata)
        print(f"Image and metadata saved to {filename}")

    def log_to_ods(self, filename, metadata_dict):
        """
        Append image metadata to a global .ods logbook.
        
        Parameters
        ----------
        filename : str
            Full path to saved HDF5 image
        metadata_dict : dict
            Metadata fields from image acquisition
        """
        log_entry = {
            "Timestamp": metadata_dict.get("timestamp"),
            "Filename": os.path.abspath(filename),
            "Exposure (s)": metadata_dict.get("exposure_time_sec"),
            "EM Gain": metadata_dict.get("em_gain"),
            "Temperature (°C)": metadata_dict.get("temperature_C"),
            "Camera Model": metadata_dict.get("camera_model"),
            "ROI": str(metadata_dict.get("roi")),
            "Comments": metadata_dict.get("comment")
        }
    
        if os.path.exists(self.logbook_path):
            df = pd.read_excel(self.logbook_path, engine="odf")
            df = pd.concat([df, pd.DataFrame([log_entry])], ignore_index=True)
        else:
            df = pd.DataFrame([log_entry])
    
        df.to_excel(self.logbook_path, index=False, engine="odf")
        print(f"✔️ Logged acquisition to: {self.logbook_path}")
    
    def close_camera(self):
        if self.cam is not None:
            self.cam.close()
            self.cam = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close_camera()
