import json
import math

from openap import aero, prop, Thrust, FuelFlow

from .lift_drag import LiftDrag


def interpolate(x, x1, x2, y1, y2):
    return y1 + (((x - x1) / (x2 - x1)) * (y2 - y1))


def local_gravity(latitude: float, height: float) -> float:
    """Calculate local gravity

    Args:
        latitude (float): latitude
        height (float): Height above mean sea level (meter)

    Returns:
        float: the local gravity
    """
    sinLat = math.sin(math.radians(latitude))
    g = 9.780327 * (1 + 0.0053024 * (sinLat ** 2)
                    - 0.0000058 * (sinLat ** 2))\
        - (3.086 * (10 ** -6) * height)
    return g


class Performance():
    """Calulate Instantaneous performance of one object"""

    def __init__(self, aircraft_name, write_output: bool = False):
        self.write = write_output
        # General Variables
        self.aircraft_data = prop.aircraft(aircraft_name)
        self.dt = 1.0 / 60.0  # simulation timestep 60 per seconds
        aircraft_txt = open(f"./data/{aircraft_name}.json", 'r').read()
        self.aircraft = json.loads(aircraft_txt)
        eng_name = self.aircraft_data["engine"]["default"]
        self.ac_thrust = Thrust(ac=self.aircraft["Name"],
                                eng=eng_name)
        # self.ac_thrust = Thrust(f"./data/{aircraft_name}_thrust.csv")
        # Performance Variables (all unit in SI except stated otherwise)
        self.lift_drag = LiftDrag(f"./data/{aircraft_name}_ld.csv")
        self.g = 9.81
        self.mass = self.aircraft_data["limits"]["MTOW"]
        self.thrust_lever = 1.0
        self.altitude = 0.0
        self.pressure = 0.0
        self.density = 0.0
        self.temp = 0.0
        self.cas = 0.0
        self.tas = 0.0
        self.v_y = 0.0  # vertical Speed
        self.vs = 0.0  # Vertical Speed [fpm]
        self.drag = 0.0
        self.thrust = 0.0
        self.lift = 0.0
        self.weight = 0.0
        self.t_d = 0.0  # thrust minus drag aka exceed thrust
        self.l_w = 0.0  # lift minus weight aka exceed lift
        self.pitch = 0.0
        self.fpa = 0.0
        self.aoa = 0.0
        self.Q = 0.0  # tas² * density
        self.acc_x = 0.0
        self.acc_y = 0.0
        self.distance_x = 0.0  # total distance[m]
        self.d_x = 0.0  # instantaneous X distance[m]
        self.d_y = 0.0  # instantaneous Y distance[m]
        self.phase = 0  # Current phase
        self.cd = 0.0
        self.cl = 0.0
        self.drag0 = self.aircraft["Drag0"]
        self.lift0 = self.aircraft["Lift0"]
        self.gear = False
        self.flaps = 0
        self.pitch_target = 0.0
        self.pitch_rate_of_change = 3.0  # rate of change of the pitch [°/sec]
        self.ac_fuelflow = FuelFlow(ac=self.aircraft["Name"], eng=eng_name)
        if self.write:
            self.output = open("output.csv", 'w+')
            self.output.write(self.__get_header())
            self.output.flush()

    def __get_Q(self):
        self.pressure, self.density, self.temp = aero.atmos(self.altitude)
        self.Q = self.density * (self.tas ** 2)

    def __calculate_FPA(self):
        self.fpa = math.degrees(math.atan2(self.d_y, self.d_x))
        self.aoa = self.pitch - self.fpa

    def __calculate_lift(self):
        if self.gear:
            self.cl += self.aircraft["Gear"]["Lift"]
        if self.flaps > 0:
            self.cl += self.aircraft["Flaps"][self.flaps-1]["Lift"]

        self.lift = self.lift0\
            + (0.5 * self.Q * self.aircraft["WingSpan"] * self.cl)
        self.lift *= 1.5

    def __calculate_drag(self, new: bool = True):
        if self.gear:
            self.cd += self.aircraft["Gear"]["Drag"]
        if self.flaps > 0:
            self.cd += self.aircraft["Flaps"][self.flaps-1]["Drag"]
        self.drag = self.drag0\
            + (0.5 * self.Q * self.aircraft["WingSpan"] * self.cd)

    def __change_pitch(self) -> None:
        """
        Change pitch in relation of pitch target change of pitch occure with
        a 3 degrees per seconds change.
        """
        if self.pitch == self.pitch_target:
            return
        if self.pitch > self.pitch_target:
            self.pitch -= self.pitch_rate_of_change * self.dt
        elif self.pitch < self.pitch_target:
            self.pitch += self.pitch_rate_of_change * self.dt

    def run(self) -> bool:
        """Calculate aircraft performance till thrust reduction altitude

        Args:
            target_alt (float, optional):
                The thrust reduction altitude in meters.
                Defaults to 457.2m (1500.0 feets)

        Returns:
            bool: True if the phase is still valid, else False
        """
        if self.distance_x == 0:
            self.aoa = self.pitch
        self.cl, self.cd = self.lift_drag.get_data(self.aoa)
        self.__get_Q()
        self.__change_pitch()
        self.__calculate_drag()
        self.__calculate_lift()
        self.g = local_gravity(50.0, self.altitude)
        self.weight = self.mass * self.g
        max_thrust = self.ac_thrust.takeoff(alt=self.altitude / aero.ft,
                                             tas=self.tas / aero.kts)
        idle_thrust = self.ac_thrust.descent_idle(tas=self.tas / aero.kts, 
                                                  alt=self.altitude / aero.ft)
        self.thrust = interpolate(self.thrust_lever, 0.0, 1.0,
                                  idle_thrust, max_thrust)
        fuelflow = self.ac_fuelflow.at_thrust(acthr=self.thrust / 2.0,
                                              alt=self.altitude / aero.ft)
        self.mass -= fuelflow * self.dt * 2
        self.t_d = self.thrust - self.drag\
            - (self.weight * math.sin(math.radians(self.pitch)))
        self.l_w = self.lift\
            - (self.weight * math.cos(math.radians(self.pitch)))\
            + (self.thrust * math.sin(math.radians(self.pitch)))
        acc = self.t_d / self.mass
        self.acc_x = acc * math.cos(math.radians(self.pitch))
        self.acc_y = acc * math.sin(math.radians(self.pitch))
        v_acc = self.l_w / self.mass
        self.acc_y += v_acc * math.cos(math.radians(self.pitch))
        self.acc_x += v_acc * math.sin(math.radians(self.pitch))
        self.d_x = (self.tas * self.dt) + 0.5 * self.acc_x * (self.dt ** 2)
        self.d_y = (self.v_y * self.dt) + 0.5 * self.acc_y * (self.dt ** 2)
        self.tas += self.acc_x * self.dt
        self.cas = aero.tas2cas(self.tas, self.altitude)
        self.v_y += self.acc_y * self.dt
        if self.altitude <= 0:
            self.altitude = 0
            if self.d_y < 0:
                self.d_y = 0
            if self.v_y < 0:
                self.v_y = 0
                self.vs = 0
        self.altitude += self.d_y
        self.distance_x += self.d_x
        self.vs = self.v_y / aero.fpm
        self. __calculate_FPA()
        if self.write:
            self.output.write(str(self))
            self.output.flush()

    def __str__(self):
        return f"{self.mass},{self.altitude},{self.pressure},{self.density},"\
               f"{self.temp},{self.cas},{self.tas},{self.v_y},{self.vs},"\
               f"{self.drag},{self.thrust},{self.t_d},{self.pitch},"\
               f"{self.fpa},{self.aoa},{self.Q},{self.acc_x},{self.acc_y},"\
               f"{self.distance_x},{self.d_x},{self.d_y},{self.phase},"\
               f"{self.cd},{self.drag0},{self.gear},{self.flaps},{self.cl},"\
               f"{self.lift},{self.weight},{self.l_w},{self.thrust_lever},"\
               f"{self.altitude / aero.ft},{self.g},{self.pitch_target}\n"

    def __get_header(self):
        return "Mass,Altitude,Pressure,Density,Temperature,Cas,Tas,Vy,VS,"\
               "Drag,Thrust,T-D,Pitch,FPA,AOA,Q,AccelerationX,AccelerationY,"\
               "DistanceX,Dx,Dy,Phase,Cd,Cd0,Gear,Flaps,Cl,Lift,Weight,L-W,"\
               "Thrust Limit,Altitude FT,Gravity,Target Pitch\n"


if __name__ == "__main__":
    from openap import WRAP

    a319 = Performance("A319")
    a319_wrp = WRAP(ac="A319")
    a319.cas = a319_wrp.takeoff_speed()["default"]
    a319.tas = aero.cas2tas(a319.cas, a319.altitude)
    a319.pitch = 15.0
    a319.v_y = 2000 * aero.fpm
    a319.gear = True
    a319.flaps = 2
    print(a319.v_y)
    print("Starting")
    for i in range(10):
        a319.run()
    print("Finished")
