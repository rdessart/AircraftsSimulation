from openap import WRAP
from openap.extra import aero

from simulation.performance import Performance
from automation.auto_thrust import Autothrust
from automation.autopilot import Autopilot


class Aircraft:
    """Represent an aircraft"""
    def __init__(self, icao_type: str, callsign: str) -> None:
        self.performance = Performance(icao_type)
        self.autoThrust = Autothrust()
        self.autoPilot = Autopilot()
        self.latitude = 0.0
        self.longitude = 0.0
        self.ground_level = 0.0
        self.callsign = callsign
        self.takeoff = False
        self.wrap = WRAP(ac=icao_type)
        self.target_alt = 6_000 * aero.ft
        self.id = 0

    def get_ap_vert_mode(self) -> dict:
        return {
            "Altitude Aquire": Autopilot.alt_aquire,
            "Altitude Hold": Autopilot.alt_hold,
            "Speed Hold": Autopilot.speed_hold,
            "Mach Hold": Autopilot.mach_hold,
            "Vert Speed Hold": Autopilot.vs_hold
        }

    def set_ap_vert_mode(self, mode: int, target: float,
                         target_altitude: float) -> bool:
        if mode == Autopilot.alt_aquire:
            self.autoPilot.AltitudeAquire(target_altitude)
        elif mode == Autopilot.alt_hold:
            self.autoPilot.AltitudeHold(target_altitude)
        elif mode == Autopilot.speed_hold:
            self.autoPilot.SpeedHold(target, target_altitude)
        elif mode == Autopilot.mach_hold:
            self.autoPilot.MachHold(target, target_altitude)
        elif mode == Autopilot.vs_hold:
            self.autoPilot.VerticalSpeedHold(target, target_altitude)
        else:
            return False
        return True

    def run(self) -> int:
        self.performance.run()
        if self.takeoff:
            if self.performance.pitch < self.target_to_pitch and\
                    self.cas() >= self.wrap.takeoff_speed()["default"]:
                self.performance.pitch += 3.0 * self.performance.dt
            if self.performance.pitch >= self.target_to_pitch and\
                    self.cas() >= self.wrap.takeoff_speed()["default"]:
                self.takeoff = False
                self.autoPilot.SpeedHold(self.cas(), self.target_alt)

        if self.autoPilot.active_mode is not None:
            self.performance.pitch = self.autoPilot.run(self.cas(),
                                                        self.vertical_speed(),
                                                        self.altitude(),
                                                        self.pitch(),
                                                        self.mach())
        if self.autoThrust.active_mode is not None:
            self.performance.thrust_lever = self.autoThrust.run(self.cas())

    @property
    def pitch(self) -> float:
        return self.performance.pitch

    @property
    def altitude(self) -> float:
        return self.performance.altitude

    @property
    def tas(self) -> float:
        return self.performance.tas

    @property
    def cas(self) -> float:
        return self.performance.cas

    @property
    def mach(self) -> float:
        return aero.tas2mach(self.tas, self.altitude)

    @property
    def vertical_speed(self) -> float:
        return self.performance.v_y

    def angle_of_attack(self) -> float:
        return self.performance.aoa

    @property
    def mass(self) -> float:
        return self.performance.mass

    @mass.setter
    def mass(self, value: float) -> None:
        self.performance.mass = value

    def create(self, position: tuple, mass: float,
               ground_level: float = 0.0, altitude: float = 0.0,
               cas: float = 0.0, takeoff: bool = False,
               target_alt: float = None) -> bool:
        self.performance.mass = mass
        self.latitude, self.longitude = position
        self.ground_level = ground_level
        self.performance.altitude = altitude
        self.performance.cas = cas
        self.performance.tas = aero.cas2tas(cas, self.performance.altitude)
        self.mach = aero.cas2mach(self.performance.cas,
                                  self.performance.altitude)
        if target_alt is not None:
            self.target_alt = target_alt
        elif not takeoff and altitude > 0 and altitude > ground_level:
            self.target_alt = altitude
        elif not takeoff:
            takeoff = True
        if not takeoff:
            self.autoPilot.AltitudeHold(self.altitude)

    def set_target_alt(self, altitude: float) -> None:
        self.target_alt = altitude
