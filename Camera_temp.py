# -*- coding: utf-8 -*-
"""
Created on Tue Apr 22 13:51:13 2025

@author: TEM
"""

from camController import Cam
from pylablib.devices import Andor

use_recent = input("Open or Close (o/c): ").strip().lower()

if use_recent == 'o':
    name = "test_empty"
    data_path = r"C:\Users\DELTA_LAB_1\Desktop\shg_data\Test"
    temp_target = -70
    
    cam = Cam(name=name, data_path=data_path, temp=temp_target)
    
elif use_recent == 'c':
    if 'cam' in globals():
        cam.close_camera()
        Andor.AndorSDK2.shutdown()
    else:
        print("Camera object not found. Please open the camera first.")