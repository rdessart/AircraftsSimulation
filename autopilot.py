"""Autopilot"""
from performance import Performance


class Autopilot():
    """Autopilot description"""
    def __init__(self, aircraft: Performance):
        """Initalise the Autopilot.
        Args:
            aircraft (Performance): aircraft bound the autopilot
        """
        self.aircraft = aircraft

    def SpeedHold(self, target_speed: float, target_alt: float = None) -> None:
        """
        Adjust the pitch to keep current speed
        Args:
            target_speed ([float]): required speed, in meter/seconds
            target_alt (float): the target altitude in meters [default=None]
        """
        raise NotImplementedError

    def VerticalSpeedHold(self, target_vs: float,
                          target_alt: float = None) -> None:
        """
        Adjust the pitch to hold the target vertical speed
        Args:
            target_vs (float): the target vertical speed in m/s
            target_alt (float): the target altitude in meters [default=None]
        """
        raise NotImplementedError

    def AltitudeHold(self, altitude_target: float) -> None:
        """[summary]
        Adjust the pitch to hold the current altitude
        Args:
            altitude_target (float): altitude to hold in meters
        """
        raise NotImplementedError

    def AltitudeAquire(self, altitude_target: float) -> None:
        """[summary]
        Adjust the pitch to interecpt the target altitude
        Args:
            altitude_target (float): altitude to hold in meters
        """
        raise NotImplementedError
