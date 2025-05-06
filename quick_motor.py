# -*- coding: utf-8 -*-
"""
Created on Tue Apr 22 14:10:11 2025

@author: DELTA_LAB_1
"""

from motorController import StandaMotor, TwoAxisController
import threading
import time

motor_speed = 250
motor_accel = 1200
rotation_duration = 60
rotation_dir1 = "right"
rotation_dir2 = "right"

cfg_path = None
use_recent = input("Open or Close (o/c): ").strip().lower()

if use_recent == 'o':

    com1 = r"xi-com:\\.\COM4"
    com2 = r"xi-com:\\.\COM5"
    
    motor1 = StandaMotor(com1)
    motor2 = StandaMotor(com2)
    controller = TwoAxisController(motor1, motor2)
    controller.gth_both()
    controller.gtz_both()
    usr = input("Rotate? (y/n): ").strip().lower()
    if usr == 'y':
        controller.sync_speeds = lambda speed, accel: [
            motor1.set_speed(speed),
            motor1.set_acceleration(accel),
            motor2.set_speed(speed),
            motor2.set_acceleration(accel)
        ]
        controller.sync_speeds(motor_speed, motor_accel)

        def spin_motors():
            controller.rotate_both(rotation_dir1, rotation_dir2, duration=rotation_duration)

        motor_thread = threading.Thread(target=spin_motors)
        motor_thread.start()

        time.sleep(0.1)

        motor_thread.join()
    else:
        pass
        

if use_recent == 'c':
    if 'controller' in globals():
        try:
            controller.close()
            del controller
            print("✅ Controller closed and deleted.")
        except Exception as e:
            print(f"⚠️ Error closing controller: {e}")
    else:
        print("⚠️ 'controller' object not found in global scope.")
        