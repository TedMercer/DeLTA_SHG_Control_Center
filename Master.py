# -*- coding: utf-8 -*-
"""
Created on Thu May  1 15:39:27 2025

@author: TEM
"""
from motorController import TwoAxisController
import threading
import time

temp_target = -70
exposure_time = 10
em_gain = 0


motor_speed = 250
motor_accel = 1200
rotation_duration = 60
rotation_dir1 = "right"
rotation_dir2 = "right"

def DeLTA_Collect_SHG(C, M1, M2, t = exposure_time, em = em_gain):
    controller = TwoAxisController(M1, M2)
    print("###################################")
    print("DUAL MOTOR CREATED")
    print("###################################")
    controller.gtz_both()
    print("###################################")
    print("HOMED AND ZEROED")
    print("###################################")
    C.set_exposure(exposure = t)
    C.set_em_gain(em_gain = em)
    C.cam.setup_shutter(mode="auto", ttl_mode=1, open_time=27, close_time=27)
    print("###################################")
    print(f"CAM exposure {t} and em gain {em}")
    print("###################################")
    
    
    print(f"⏳ Waiting for camera to stabilize near {temp_target}°C...")
    for _ in range(60): 
        current_temp = C.get_temp()
        if current_temp is not None:
            print(f"Current temperature: {current_temp:.1f}°C")
            if abs(current_temp - temp_target) < 5:
                print("✅ Target temperature reached.")
                break
        else:
            print("⚠️ Temperature read returned None. Retrying...")
        time.sleep(2)
    else:
        print("⚠️ Temperature did not stabilize within timeout.")
        
    controller.sync_speeds = lambda speed, accel: [
        M1.set_speed(speed),
        M1.set_acceleration(accel),
        M2.set_speed(speed),
        M2.set_acceleration(accel)
    ]
    controller.sync_speeds(motor_speed, motor_accel)
    
    print("###################################")
    print(f"MOTOR Speed synched {motor_speed} and {motor_accel}")
    print("###################################")
    
    def spin_motors():
        controller.rotate_both(rotation_dir1, rotation_dir2, duration=t+5)

    def acquire_image():
        C.acquire_and_plot(save=True)

    motor_thread = threading.Thread(target=spin_motors)
    camera_thread = threading.Thread(target=acquire_image)

    motor_thread.start()
    camera_thread.start()

    motor_thread.join()
    camera_thread.join()

    print("✅ Collection complete")


def DeLTA_Spin(M1, M2, spin1 = True, spin2 = False, dur = rotation_duration, ms = motor_speed,
               ma = motor_accel, gtz = False):
    
    if gtz:
        M1.gtz()
        M2.gtz()
    
    if spin1 and spin2 == True:
        controller = TwoAxisController(M1, M2)
        controller.sync_speeds = lambda speed, accel: [
            M1.set_speed(speed),
            M1.set_acceleration(accel),
            M2.set_speed(speed),
            M2.set_acceleration(accel)
        ]
        controller.sync_speeds(motor_speed, motor_accel)
        
        def spin_motors():
            controller.rotate_both(rotation_dir1, rotation_dir2, duration = dur)
        
        motor_thread = threading.Thread(target=spin_motors)
        motor_thread.start()
        time.sleep(.1)
        motor_thread.join()
        
    if spin1 == True and spin2 == False: 
        M1.rotate_continuous(direction=rotation_dir1, duration=dur)
        M1.set_speed(ms),
        M1.set_acceleration(ma),
    
    if spin2 == True and spin1 == False:
        M2.rotate_continuous(direction=rotation_dir2, duration=dur)
        M2.set_speed(ms),
        M2.set_acceleration(ma)
        