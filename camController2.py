# -*- coding: utf-8 -*-
"""
Created on Mon Apr 21 12:37:40 2025

@author: DELTA_LAB_1
"""

import ctypes
from ctypes import byref, c_int, c_float, c_char_p, c_uint16
import numpy as np

class AndorCamera:
    def __init__(self, dll_path=None):
        # Load the Andor SDK2 DLL (defaults to atmcd64d.dll for 64-bit, atmcd32d.dll for 32-bit Windows)
        if dll_path is None:
            try:
                self.dll = ctypes.WinDLL('atmcd64d.dll')
            except OSError:
                self.dll = ctypes.WinDLL('atmcd32d.dll')
        else:
            self.dll = ctypes.WinDLL(dll_path)
        # Initialize the camera (empty string uses current directory for config files, 
        # or provide path to Andor SDK data files as needed)
        ret = self.dll.Initialize(c_char_p(b""))
        if ret != 20002:  # 20002 = DRV_SUCCESS
            raise RuntimeError(f"Andor SDK Initialize failed (error code {ret})")
        # Get detector dimensions (sensor width and height in pixels)
        x = c_int()
        y = c_int()
        ret = self.dll.GetDetector(byref(x), byref(y))
        if ret != 20002:
            self.dll.ShutDown()
            raise RuntimeError(f"GetDetector failed (error code {ret})")
        self.width = x.value
        self.height = y.value
        # Set read mode to "Image" (full frame imaging)
        ret = self.dll.SetReadMode(c_int(4))  # 4 = Image mode (for 2D capture)
        if ret != 20002:
            self.dll.ShutDown()
            raise RuntimeError(f"SetReadMode failed (error {ret})")
        # Set acquisition mode to "Single Scan" by default (one image per acquisition)
        ret = self.dll.SetAcquisitionMode(c_int(1))  # 1 = Single Scan&#8203;:contentReference[oaicite:17]{index=17}
        if ret != 20002:
            self.dll.ShutDown()
            raise RuntimeError(f"SetAcquisitionMode failed (error {ret})")
        # Define the full image area as the readout region (no binning)
        ret = self.dll.SetImage(c_int(1), c_int(1), 
                                c_int(1), c_int(self.width), 
                                c_int(1), c_int(self.height))
        if ret != 20002:
            self.dll.ShutDown()
            raise RuntimeError(f"SetImage failed (error {ret})")
        # Cooler is off by default; user can turn it on via cooler_on()
        self.cooler_on_flag = False

    def set_exposure_time(self, exposure_sec):
        """Set the exposure time (seconds)."""
        ret = self.dll.SetExposureTime(c_float(exposure_sec))
        if ret != 20002:
            raise RuntimeError(f"SetExposureTime failed (error {ret})")

    def get_exposure_time(self):
        """Get the current exposure time (seconds) from camera settings."""
        exp = c_float();  acc = c_float();  kin = c_float()
        ret = self.dll.GetAcquisitionTimings(byref(exp), byref(acc), byref(kin))
        if ret != 20002:
            raise RuntimeError(f"GetAcquisitionTimings failed (error {ret})")
        return exp.value  # Return the exposure time (seconds)

    def set_EM_gain_mode(self, mode):
        """Enable/Set EM gain mode (0: 0-255, 1: 0-4095, 2: Linear, 3: Real EM gain)&#8203;:contentReference[oaicite:18]{index=18}."""
        ret = self.dll.SetEMGainMode(c_int(mode))
        if ret != 20002:
            raise RuntimeError(f"SetEMGainMode failed (error {ret})")

    def set_EM_gain(self, gain_value):
        """Set the EMCCD gain value (within range for the current EM gain mode)&#8203;:contentReference[oaicite:19]{index=19}."""
        ret = self.dll.SetEMCCDGain(c_int(gain_value))
        if ret != 20002:
            raise RuntimeError(f"SetEMCCDGain failed (error {ret})")

    def set_acquisition_mode(self, mode):
        """Set acquisition mode (1=Single, 2=Accumulate, 3=Kinetic, 4=Fast Kinetic, 5=Run-till-abort)&#8203;:contentReference[oaicite:20]{index=20}."""
        ret = self.dll.SetAcquisitionMode(c_int(mode))
        if ret != 20002:
            raise RuntimeError(f"SetAcquisitionMode failed (error {ret})")

    def set_shutter(self, typ, mode, closing_time=0, opening_time=0):
        """Configure shutter settings (internal or external). 
        - typ: 0 for TTL low = open, 1 for TTL high = open&#8203;:contentReference[oaicite:21]{index=21} 
        - mode: 0 = auto, 1 = permanently open, 2 = permanently closed, 4 = open for FVB, 5 = open for any series&#8203;:contentReference[oaicite:22]{index=22} 
        - closing_time, opening_time: shutter close/open times in ms."""
        ret = self.dll.SetShutter(c_int(typ), c_int(mode), c_int(closing_time), c_int(opening_time))
        if ret != 20002:
            raise RuntimeError(f"SetShutter failed (error {ret})")

    def set_trigger_mode(self, mode):
        """Set trigger mode (0 = internal, 1 = external, 10 = software, etc.)."""
        ret = self.dll.SetTriggerMode(c_int(mode))
        if ret != 20002:
            raise RuntimeError(f"SetTriggerMode failed (error {ret})")

    def set_temperature(self, temperature_C):
        """Set the desired CCD temperature (°C). Use cooler_on() to start cooling&#8203;:contentReference[oaicite:23]{index=23}."""
        ret = self.dll.SetTemperature(c_int(temperature_C))
        if ret != 20002:
            raise RuntimeError(f"SetTemperature failed (error {ret})")

    def cooler_on(self):
        """Turn on the cooler to begin cooling towards the set temperature&#8203;:contentReference[oaicite:24]{index=24}."""
        ret = self.dll.CoolerON()
        if ret != 20002:
            raise RuntimeError(f"CoolerON failed (error {ret})")
        self.cooler_on_flag = True

    def cooler_off(self):
        """Turn off the cooler (stop cooling)."""
        ret = self.dll.CoolerOFF()
        if ret != 20002:
            raise RuntimeError(f"CoolerOFF failed (error {ret})")
        self.cooler_on_flag = False

    def get_temperature(self):
        """Get the current temperature (°C) and cooling status."""
        temp = c_int()
        ret = self.dll.GetTemperature(byref(temp))
        # Interpret the status code returned by GetTemperature&#8203;:contentReference[oaicite:25]{index=25}
        if ret == 20034:      # DRV_TEMPERATURE_OFF
            status = "OFF"
        elif ret == 20036:    # DRV_TEMPERATURE_STABILIZED
            status = "STABILIZED"
        elif ret == 20035:    # DRV_TEMPERATURE_NOT_STABILIZED
            status = "NOT_STABILIZED"
        elif ret == 20037:    # DRV_TEMPERATURE_NOT_REACHED
            status = "NOT_REACHED"
        elif ret == 20040:    # DRV_TEMPERATURE_DRIFT
            status = "DRIFTING"
        elif ret == 20002:    # DRV_SUCCESS (treated as reached OK)
            status = "ACHIEVED"
        else:
            status = f"ERROR_{ret}"
        return temp.value, status

    def start_acquisition(self):
        """Start an acquisition (begin exposure/readout)."""
        ret = self.dll.StartAcquisition()
        if ret != 20002:
            raise RuntimeError(f"StartAcquisition failed (error {ret})")

    def wait_for_acquisition(self, timeout_ms=None):
        """Wait until the current acquisition completes (blocking wait). 
        Optionally specify a timeout (ms) to avoid infinite wait."""
        if timeout_ms is None:
            ret = self.dll.WaitForAcquisition()
        else:
            ret = self.dll.WaitForAcquisitionTimeOut(c_int(timeout_ms))
        if ret != 20002:
            raise RuntimeError(f"Acquisition did not complete (code {ret})")

    def get_image_data(self):
        """Retrieve the most recently acquired image as a 2D NumPy array."""
        size = self.width * self.height
        buffer = (c_uint16 * size)()  # allocate C-array for pixel data (16-bit unsigned)
        ret = self.dll.GetMostRecentImage16(buffer, c_int(size))
        if ret != 20002:
            raise RuntimeError(f"GetMostRecentImage16 failed (error {ret})")
        # Convert the C buffer to a NumPy array and reshape to (height, width)
        data = np.frombuffer(buffer, dtype=np.uint16).copy()
        image_array = data.reshape((self.height, self.width))
        return image_array

    def acquire_image(self):
        """Trigger an acquisition and return the captured image as a NumPy array."""
        self.start_acquisition()
        self.wait_for_acquisition()
        return self.get_image_data()

    def close(self):
        """Shut down the camera and release resources."""
        # (Optionally turn off cooler here if it was on, depending on desired behavior.)
        ret = self.dll.ShutDown()
        if ret != 20002:
            print(f"Warning: ShutDown returned error code {ret}")
