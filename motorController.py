"""
Created on Tue Apr  1 11:32:58 2025

@author: TEM
"""
import time
import threading
import libximc.highlevel as ximc

class StandaMotor:
    def __init__(self, device_uri):
        """
        Initialize a single motor via its device URI.
        Example URI: r"xi-com:\\.\COM29"
        """
        self.axis = ximc.Axis(device_uri)
        self.axis.open_device()
    
    def home(self):
        """Home the motor using soft stop homing."""
        self.axis.command_home()

    def zero(self):
        """Set current position to 0."""
        self.axis.command_zero()

    def move_relative(self, distance_units):
        """Move the motor by a relative distance (in units, e.g., degrees)."""
        self.axis.command_move(distance_units)

    def move_absolute(self, position_units):
        """Move the motor to an absolute position (in units, e.g., degrees)."""
        self.axis.command_move(position_units, relative=False)

    def rotate_continuous(self, direction="right", duration=None):
        """
        Start continuous rotation.
        direction: "right" or "left"
        dumorationration: if provided, rotate for a number of seconds then stop.
        """
        if direction.lower() == "right":
            self.axis.command_right()
        elif direction.lower() == "left":
            self.axis.command_left()
        else:
            raise ValueError("Direction must be 'right' or 'left'")
        
        if duration is not None:
            time.sleep(duration)
            self.stop()

    def set_speed(self, speed):
        """
        Set motor speed in degrees/sec and report frequency in Hz.
        """
        mvst = self.axis.get_move_settings()
        mvst.Speed = speed
        self.axis.set_move_settings(mvst)
    
        # Assuming speed is in degrees/sec, convert to Hz (revolutions/sec)
        frequency_hz = speed / 360
        print(f"[Set Speed] Speed set to {speed:.2f} deg/s ({frequency_hz:.3f} Hz)")
    
    def set_acceleration(self, accel):
        """
        Set motor acceleration in degrees/sec² and report how fast it would reach full speed (optional).
        """
        mvst = self.axis.get_move_settings()
        mvst.Accel = accel
        self.axis.set_move_settings(mvst)
    
        print(f"[Set Accel] Acceleration set to {accel:.2f} deg/s²")

    def stop(self, soft=False):
        """Stop the motor. Soft stop decelerates to a halt."""
        if soft:
            self.axis.command_sstp()
        else:
            self.axis.command_stop()

    def get_position(self):
        """Return the current position in user units (e.g., degrees)."""
        return self.axis.get_position().Position

    def close(self):
        """Clean up (optional with libximc)."""
        del self.axis


class TwoAxisController:
    def __init__(self, motor1, motor2):
        self.motor1 = motor1
        self.motor2 = motor2

    def home_both(self):
        t1 = threading.Thread(target=self.motor1.home)
        t2 = threading.Thread(target=self.motor2.home)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

    def zero_both(self):
        self.motor1.zero()
        self.motor2.zero()

    def move_relative_both(self, d1, d2):
        t1 = threading.Thread(target=self.motor1.move_relative, args=(d1,))
        t2 = threading.Thread(target=self.motor2.move_relative, args=(d2,))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

    def move_absolute_both(self, p1, p2):
        t1 = threading.Thread(target=self.motor1.move_absolute, args=(p1,))
        t2 = threading.Thread(target=self.motor2.move_absolute, args=(p2,))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

    def rotate_both(self, dir1, dir2, duration):
        t1 = threading.Thread(target=self.motor1.rotate_continuous, args=(dir1, duration))
        t2 = threading.Thread(target=self.motor2.rotate_continuous, args=(dir2, duration))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

    def stop_both(self, soft=False):
        self.motor1.stop(soft)
        self.motor2.stop(soft)

    def close(self):
        self.motor1.close()
        self.motor2.close()