# -*- coding: utf-8 -*-
"""
Created on Tue Apr  1 11:32:58 2025

@author: TEM
"""

from camController import Cam
from motorController import StandaMotor, TwoAxisController
import time
import threading

# ---- User Configuration ----
Hold_temp = True
name = "test_empty"
data_path = r"C:\Users\DELTA_LAB_1\Desktop\shg_data\Test"

cfg_path = r"C:\Users\DELTA_LAB_1\Desktop\STANDA\8MRU-1-MEn1.cfg"
cfg_path = None

com1 = r"xi-com:\\.\COM4"
com2 = r"xi-com:\\.\COM5"

temp_target = -70
exposure_time = 1
em_gain = 0
motor_speed = 500
motor_accel = 1200
rotation_duration = 5
rotation_dir1 = "right"
rotation_dir2 = "right"
# ----------------------

def run_synchronized_measurement():
    with Cam(name=name, data_path=data_path, temp=temp_target) as cam:
        cam.set_exposure(exposure_time)
        cam.set_em_gain(em_gain)
        cam.cam.setup_shutter(mode="auto", ttl_mode=1, open_time=27, close_time=27)

        print(f"⏳ Waiting for camera to stabilize near {temp_target}°C...")
        for _ in range(60): 
            current_temp = cam.get_temp()
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
        
        motor1 = StandaMotor(com1)
        motor2 = StandaMotor(com2)
        controller = TwoAxisController(motor1, motor2)
        try:
            controller.gtz_both()
            controller.sync_speeds(motor_speed, motor_accel)

            def spin_motors():
                controller.rotate_both(rotation_dir1, rotation_dir2, duration=rotation_duration)

            motor_thread = threading.Thread(target=spin_motors)
            motor_thread.start()

            time.sleep(0.1)
            cam.acquire_and_plot(save=True)
            motor_thread.join()
        finally:
            controller.close()

    print("\n✅ Measurement complete and saved.")

if __name__ == "__main__":
    run_synchronized_measurement()