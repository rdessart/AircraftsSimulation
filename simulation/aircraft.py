from openap.extra import aero

from .performance import Performance
from ..automation.auto_thrust import Autothrust
from ..automation.autopilot import Autopilot


class Aircraft:
    """Represent an aircraft"""
    def __init__(self, icao_type: str) -> None:
        self.performance =  Performance(icao_type)
        self.autoThrust = Autothrust()
        self.autoPilot = Autopilot()
        self.latitude = 0.0
        self.longitude = 0.0
        self.ground_level = 0.0

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
    
    @mass.setter()
    def mass(self, value: float) -> None:
        self.performance.mass = value
    

    def create(self, position: tuple, mass: float,
               ground_level: float, altitude: float, cas: float):
        self.performance.mass = mass
        self.latitude, self.longitude = position
        self.ground_level = ground_level
        self.performance.altitude = altitude
        self.performance.cas = cas
        self.performance.tas = aero.cas2tas(cas, self.performance.altitude)
        self.mach = aero.cas2mach(self.performance.cas,
                                  self.performance.altitude)