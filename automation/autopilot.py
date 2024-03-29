"""Autopilot"""
from .pid_controller import PIDController

from openap.extra import aero


class Autopilot():
    """Autopilot description"""
    speed_hold = 1
    mach_hold = 2
    vs_hold = 3
    alt_aquire = 4
    alt_hold = 5

    def __init__(self):
        """Initalise the Autopilot.
        Args:
            aircraft (Performance): aircraft bound the autopilot
        """
        # self.aircraft = aircraft
        self.pid = None
        self.active_mode = None
        self.pitch_limit = {'MIN': -15, 'MAX': 15}
        self.ap_dt = 1.0 / 60.0
        self.target = 0
        self.target_alt = 0.0

    def SpeedHold(self, target_speed: float, target_alt: float = None) -> None:
        """
        Adjust the pitch to keep current speed
        Args:
            target_speed ([float]): required speed, in meter/seconds
            target_alt (float): the target altitude in meters [default=None]
        """
        if self.active_mode != Autopilot.speed_hold:
            self.active_mode = Autopilot.speed_hold
            Kp = -4.0  # AP 3
            Ki = -1.0
            Kd = -2.5
            self.pid = PIDController(Kp, Ki, Kd,
                                     self.pitch_limit['MIN'],
                                     self.pitch_limit['MAX'],
                                     0, 1.0/60.0)
        self.target = target_speed
        if target_alt is not None:
            self.target_alt = target_alt

    def MachHold(self, target_mach: float, target_alt: float = None) -> None:
        if self.active_mode != Autopilot.mach_hold:
            Kp = 2.0
            Ki = 1.0
            Kd = 0.0
            self.pid = PIDController(Kp, Ki, Kd,
                                     self.pitch_limit['MIN'],
                                     self.pitch_limit['MAX'],
                                     0, 1.0/60.0)
        self.target = target_mach
        if target_alt is not None:
            self.target_alt = target_alt

    def VerticalSpeedHold(self, target_vs: float,
                          target_alt: float = None) -> None:
        """
        Adjust the pitch to hold the target vertical speed
        Args:
            target_vs (float): the target vertical speed in m/s
            target_alt (float): the target altitude in meters [default=None]
        """
        if self.active_mode != Autopilot.vs_hold:
            self.active_mode = Autopilot.vs_hold
            Kp = 1.0
            Ki = 0.1
            Kd = 0.05
            self.pid = PIDController(Kp, Ki, Kd,
                                     self.pitch_limit['MIN'],
                                     self.pitch_limit['MAX'],
                                     0, 1.0/60.0)
        self.target = target_vs
        self.pid.compute(self.target, self.target)
        if target_alt is not None:
            self.target_alt = target_alt

    def AltitudeHold(self, altitude_target: float) -> None:
        """[summary]
        Adjust the pitch to hold the current altitude
        Args:
            altitude_target (float): altitude to hold in meters
        """
        if self.active_mode != Autopilot.alt_hold:
            self.active_mode = Autopilot.alt_hold
            Kp = 0.5
            Ki = 0.05
            Kd = 0.01
            self.pid = PIDController(Kp, Ki, Kd, self.pitch_limit['MIN'],
                                     self.pitch_limit['MAX'],
                                     0, dt=1/60)

        if altitude_target is not None:
            self.target_alt = altitude_target

    def AltitudeAquire(self, altitude_target: float) -> None:
        """[summary]
        Adjust the pitch to interecpt the target altitude
        Args:
            altitude_target (float): altitude to hold in meters
        """
        if self.active_mode != Autopilot.alt_aquire:
            self.active_mode = Autopilot.alt_aquire
            Kp = 1.0
            Ki = 0.1
            Kd = 0.025
            self.pid = PIDController(Kp, Ki, Kd, self.pitch_limit['MIN'],
                                     self.pitch_limit['MAX'], 0.0, dt=1/60)

    def run(self, cas: float, vert_speed: float,
            altitude: float, pitch: float, mach: float) -> float:
        if self.active_mode is None:
            return None
        self.pid.limitMax = 15.0
        self.pid.limitMin = -15.0
        target_pitch = None
        if self.active_mode not in [Autopilot.alt_aquire, Autopilot.alt_hold]:
            if altitude < self.target_alt and\
                    altitude + (vert_speed * 30) >= self.target_alt:
                self.AltitudeAquire(self.target_alt)
                return self.run(cas, vert_speed, altitude, pitch, mach)
            if altitude > self.target_alt and\
                    altitude + (vert_speed * 30) <= self.target_alt:
                self.AltitudeAquire(self.target_alt)
                return self.run(cas, vert_speed, altitude, pitch, mach)
        # if vert_speed > 0 and altitude + (vert_speed * 30) >= self.target_alt\
        #         and self.active_mode != Autopilot.alt_aquire\
        #         and self.active_mode != Autopilot.alt_hold:
        #     self.active_mode = Autopilot.alt_aquire
        #     return self.run(cas, vert_speed, altitude, pitch, mach)
        # if vert_speed < 0 and altitude + (vert_speed * 30) <= self.target_alt\
        #         and self.active_mode != Autopilot.alt_aquire\
        #         and self.active_mode != Autopilot.alt_hold:
        #     self.active_mode = Autopilot.alt_aquire
        #     return self.run(cas, vert_speed, altitude, pitch, mach)

        if self.active_mode == Autopilot.speed_hold:
            target_pitch = self.pid.compute(self.target, cas)

        elif self.active_mode == Autopilot.mach_hold:
            target_pitch = -1 * self.pid.compute(self.target, mach)

        elif self.active_mode == Autopilot.vs_hold:
            # target_pitch = self.pid.compute(self.target, vert_speed)
            out = self.pid.compute(self.target, vert_speed)
            target_pitch = (pitch + out) / 2.0

        elif self.active_mode == Autopilot.alt_aquire:
            target_vs = (self.target_alt - altitude) / 30.0
            target_pitch = self.pid.compute(target_vs, vert_speed)

        elif self.active_mode == Autopilot.alt_hold:
            min_alt = self.target_alt - 61  # target - 200ft
            max_alt = self.target_alt + 61  # target + 200ft
            # if we are below target - 200 or target + 200 we revert to vs_hold
            # with vs of +/- 1000.0 fpm
            if altitude < min_alt or altitude > max_alt:
                # self.VerticalSpeedHold(5.17, self.target_alt)
                self.VerticalSpeedHold(2.60, self.target_alt)
                return self.run(cas, vert_speed, altitude, pitch, mach)
            target_pitch = self.pid.compute(altitude, self.target_alt)
        return target_pitch


if __name__ == "__main__":
    pass
