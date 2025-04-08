# -*- coding: utf-8 -*-
"""
Created on Tue Apr  1 13:31:48 2025

@author: TEM
"""

from pylablib.devices import Andor
import matplotlib.pyplot as plt
import numpy as np


class Cam:
    def __init__(self, temp = -80):
        '''
        Parameters
        ----------
        temp : int
            This is the temperature the camera will be set to in the start up process
            
            (normally -80C)

        '''
        
        self.cam = Andor.AndorSDK2Camera(temperature=temp, fan_mode="on")
        self.temp = temp
        self.exposure = 0
        
    def get_available_properties(self):
        self.prop = self.cam.get_property_list()
        print('Available Properties:')
        
        for p in self.prop:
            print(p)
            print(r'\n')

    def get_current_vals(self):
        print("\nCurrent property values:")
        
        for p in self.prop:
            value = self.cam.get_property(p)
            print(f"{p}: {value}")

    def get_temp(self):
        t = self.cam.get_property("temperature")
        print(f"Current temperature: {t} °C")

    def set_exposure(self, exposure):
        self.cam.set_property("exposure", exposure)
        
    def set_em_gain(self, em_gain):
        self.cam.set_property("em_gain", em_gain)
    
    def set_roi(self, roi = (0,512,0,512)):
        self.cam.set_roi(roi)
       
    def acquire_single(self, **kwargs):
        im = self.cam.snap()
        self.single_im = im 
        plt.imshow(self.single_im, **kwargs)
        plt.colorbar()
        plt.title("Single Image")
        plt.show()
        
    def plot_single(self, **kwargs):
        plt.imshow(self.single_im, **kwargs)
        plt.colorbar()
        plt.title("Single Image")
        plt.show()
    
    def acquire_and_plot_images(self, num_frames=10, **kwargs):
            """
            Acquires multiple images using the current camera settings and plots them in a grid.
    
            Parameters
            ----------
            num_frames : int
                The number of images to acquire and plot.
            **kwargs : dict
                Additional keyword arguments to pass to plt.imshow for image display.
            """
    
            self.cam.setup_acquisition(mode="sequence", nframes=num_frames)
            self.cam.start_acquisition()
    
            images = []
    
            for _ in range(num_frames):
                self.cam.wait_for_frame()
                image = self.cam.read_newest_image()
                images.append(image)
    
            self.cam.stop_acquisition()
    
            cols = int(np.ceil(np.sqrt(num_frames)))
            rows = int(np.ceil(num_frames / cols))
    
            fig, axes = plt.subplots(rows, cols, figsize=(15, 15))
            axes = axes.flatten()
    
            for i, ax in enumerate(axes):
                if i < num_frames:
                    ax.imshow(images[i], **kwargs)
                    ax.set_title(f"Image {i+1}")
                    ax.axis('off')
                else:
                    ax.axis('off')  
    
            plt.tight_layout()
            plt.show()
            
    
    def close_camera(self):
        self.cam.close()
        print("Camera connection closed.")
