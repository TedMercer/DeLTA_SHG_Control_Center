# -*- coding: utf-8 -*-
"""
Created on Tue Apr  1 13:41:32 2025

@author: TEM
"""

import os
import threading
import time
import libximc

class StandaMotor:
    def __init__(self, device_uri):
        """
        Initialize the Standa motor controller.

        Parameters
        ----------
        device_uri : str
            The URI of the device to connect to. For example:
            - Serial port: "xi-com:\\\\.\\COM1"
            - USB: "xi-usb:001:002"
        """
        self.device_uri = device_uri
        self.device_id = None
        self.open_device()

    def open_device(self):
        """
        Open the connection to the device.
        """
        self.device_id = libximc.lib.open_device(self.device_uri.encode())
        if self.device_id <= 0:
            raise Exception(f"Failed to open device at {self.device_uri}")

    def close_device(self):
        """
        Close the connection to the device.
        """
        if self.device_id is not None and self.device_id > 0:
            libximc.lib.close_device(self.device_id)
            self.device_id = None
        else:
            print("Device was not open or has already been closed.")


    def load_configuration(self, config_file_path):
        """
        Load settings from a configuration file into the controller.

        Parameters
        ----------
        config_file_path : str
            The path to the configuration (.cfg) file.
        """
        if not os.path.isfile(config_file_path):
            raise FileNotFoundError(f"Configuration file not found: {config_file_path}")

        if self.device_id:
            result = libximc.lib.command_upload_settings(self.device_id, config_file_path.encode())
            if result != 0:
                raise Exception(f"Failed to load configuration from {config_file_path}")
            print(f"Configuration loaded from {config_file_path}")

    def set_speed_acceleration(self, speed, acceleration):
        """
        Set the speed and acceleration parameters for the motor.

        Parameters
        ----------
        speed : int
            The desired speed in steps per second.
        acceleration : int
            The desired acceleration in steps per second squared.
        """
        move_settings = libximc.move_settings_t()
        libximc.lib.get_move_settings(self.device_id, move_settings)
        move_settings.Speed = speed
        move_settings.Accel = acceleration
        libximc.lib.set_move_settings(self.device_id, move_settings)

    def rotate_continuous(self, direction=1):
        """
        Rotate the motor continuously in the specified direction.

        Parameters
        ----------
        direction : int, optional
            The direction of rotation (1 for forward, -1 for backward). Default is 1.
        """
        if direction not in [-1, 1]:
            raise ValueError("Direction must be 1 (forward) or -1 (backward).")
        libximc.lib.command_left(self.device_id) if direction == 1 else libximc.lib.command_right(self.device_id)

    def stop(self):
        """
        Stop the motor's movement immediately.
        """
        if self.device_id:
            libximc.lib.command_stop(self.device_id)
            
    def home(self):
        """
        Perform the homing procedure to move the motor to its predefined home position.
        """
        if self.device_id:
            result = libximc.lib.command_home(self.device_id)
            if result != 0:
                raise Exception("Failed to execute HOME command.")
            self.wait_for_stop()
            print("Homing completed successfully.")

    def zero_position(self):
        """
        Set the current motor position as zero without moving the motor.
        """
        if self.device_id:
            result = libximc.lib.command_zero(self.device_id)
            if result != 0:
                raise Exception("Failed to execute ZERO command.")
            print("Current position set to zero.")

    def move_absolute(self, position):
        """
        Move the motor to an absolute position.

        Parameters
        ----------
        position : int
            The target position in steps or microsteps, depending on the controller's configuration.
        """
        if self.device_id:
            result = libximc.lib.command_move(self.device_id, position, 0)
            if result != 0:
                raise Exception(f"Failed to move to absolute position {position}.")
            self.wait_for_stop()
            print(f"Moved to absolute position {position}.")

    def move_relative(self, displacement):
        """
        Move the motor by a relative displacement.

        Parameters
        ----------
        displacement : int
            The displacement in steps or microsteps. Positive values move the motor forward; negative values move it backward.
        """
        if self.device_id:
            result = libximc.lib.command_movr(self.device_id, displacement, 0)
            if result != 0:
                raise Exception(f"Failed to move by relative displacement {displacement}.")
            self.wait_for_stop()
            print(f"Moved by relative displacement {displacement}.")

    def wait_for_stop(self, interval=0.1):
        """
        Wait until the motor stops moving.

        Parameters
        ----------
        interval : float
            The time interval (in seconds) to check the motor status.
        """
        if self.device_id:
            while True:
                status = libximc.status_t()
                libximc.lib.get_status(self.device_id, status)
                if status.MvCmdSts == 0:  # Movement command status: 0 means stopped
                    break
                time.sleep(interval)


# motor1 = StandaMotor("xi-com:\\\\.\\COM5")
# motor2 = StandaMotor("xi-com:\\\\.\\COM4")

# motor1.load_configuration(r"C:\Users\DELTA_LAB_1\Desktop\STANDA\8MRU-1-MEn1.cfg")
# motor2.load_configuration(r"C:\Users\DELTA_LAB_1\Desktop\STANDA\8MRU-1-MEn1.cfg")


def rotate_motor(motor, direction):
    motor.rotate_continuous(direction)

def rotate_to_collect(speed, acceleration, t, motor1, motor2, direction =1):
    
    motor1.set_speed_acceleration(speed, acceleration)
    motor2.set_speed_acceleration(speed, acceleration)
    print(f"Both have been set to {speed} speed and {acceleration} acceleration")
    
    thread1 = threading.Thread(target=rotate_motor, args=(motor1, 1))
    thread2 = threading.Thread(target=rotate_motor, args=(motor2, 1))
    
    thread1.start()
    thread2.start()
    
    time.sleep(t)
    
    motor1.stop()
    motor2.stop()
    
    thread1.join()
    thread2.join()