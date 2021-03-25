"""Instanciation of a flight"""
import json

from openap.kinematic import WRAP
from openap.extra import aero

from simulation.performance import Performance


class Flight():
    """Instanciate a flight from Performance.py and run it asynchronously"""
    def __init__(self, id: int,  ac_type: str,
                 latitude: float, longitude: float, mass: int):
        self.id = id
        self.aircraft = Performance(ac_type, False)
        self.position = [latitude, longitude]
        self.ac_wrap = WRAP(ac="A319")
        self.mass = mass

    @property
    def serialize(self) -> str:
        data = {
            "Id": self.id,
            "Pitch": self.aircraft.pitch,
            "Yaw": self.aircraft.yaw,
            "Roll": self.aircraft.roll,
            "Altitude": self.aircraft.altitude / aero.ft,
            "Tas": self.aircraft.tas / aero.kts,
            "Cas": self.aircraft.cas / aero.kts,
        }
        return json.dumps(data)

    def run(self):
        self.aircraft.run()
        if self.aircraft.altitude / aero.ft > 100.0 and self.aircraft.v_y > 0:
            self.aircraft.gear = False

    def __takeoff(self, v_rot: float, pitch_target: float = 15.0) -> bool:
        if self.aircraft.speed >= v_rot and self.aircraft.altitude > 0 and\
                self.aircraft.pitch >= pitch_target:
            return False
        if self.aircraft.speed >= v_rot:
            self.aircraft.pitch_target = 15
        return True
