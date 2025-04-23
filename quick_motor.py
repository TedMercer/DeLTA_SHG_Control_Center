# -*- coding: utf-8 -*-
"""
Created on Tue Apr 22 14:10:11 2025

@author: DELTA_LAB_1
"""

from motorController import StandaMotor, TwoAxisController

cfg_path = None
use_recent = input("Open or Close (o/c): ").strip().lower()

if use_recent == 'o':

    com1 = r"xi-com:\\.\COM4"
    com2 = r"xi-com:\\.\COM5"
    
    motor1 = StandaMotor(com1)
    motor2 = StandaMotor(com2)
    controller = TwoAxisController(motor1, motor2)
    controller.home_both()
    controller.zero_both()

if use_recent == 'c':
    if 'controller' in globals():
        controller.close()
    else:
        print("controller object not found. Please open the contoller first.")