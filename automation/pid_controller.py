class PIDController():
    """Updated version of PIDController"""
    def __init__(self, Kp: float = 0.0, Ki: float = 0.0, Kd: float = 0.0,
                 limitMin: float = 0.0, limitMax: float = 0.0,
                 tau: float = 0.0, dt: float = 0.0):
        """Version 2 of PIDController, with updated math
        Args:
            Kp (float, optional): gain for proportional. Defaults to 0.0.
            Ki (float, optional): gain for integrator. Defaults to 0.0.
            Kd (float, optional): gain for derivator. Defaults to 0.0.
            limitMin (float, optional): Max Output value. Defaults to 0.0.
            limitMax (float, optional): Min Output value. Defaults to 0.0.
            tau (float, optional): gain for low pass filter. Defaults to 0.0.
            dp (float, optional): timestep. Defaults to 0.0.
        """
        self.kp = Kp
        self.ki = Ki
        self.kd = Kd
        self.limitMax = limitMax
        self.limitMin = limitMin
        self.tau = tau
        self.dt = dt
        self.use_low_pass_filter = False
        self.use_kick_avoidance = False

        self._integral = 0.0
        self._derivative = 0.0
        self._previousError = 0.0
        self._previousMeasurement = 0.0
        self._error = 0.0

    def _clamp(self, value):
        lower = self.limitMin
        upper = self.limitMax
        if value is None:
            return None
        elif (upper is not None) and (value > upper):
            return upper
        elif (lower is not None) and (value < lower):
            return lower
        return value

    def compute(self, target: float,
                measurement: float, dt: float = None) -> float:
        """Calculate output through PID interface using gain value set via
        self.Kp, self.Ki, self.Kd

        Args:
            target (float): target value to be reached
            measurement (float): actual value
            dt (float, optional): Timestep since the las call. if default we
                                 uses self.dt. Defaults to None.

        Returns:
            float: The output of the PID clamped to
                   [self.limitMax, self.limitMax]
        """
        if dt is None:
            dt = self.dt
        self._error = target - measurement
        d_error = self._error - self._previousError
        proportional = self._error * self.kp
        self._integral += self.ki * self._error * dt
        self._integral = self._clamp(self._integral)
        self._derivative = self.kd * d_error / self.dt
        output = proportional + self._integral + self._derivative
        output = self._clamp(output)
        self._previousError = self._error
        self._previousMeasurement = measurement
        return output

    def get_kpe(self):
        return self.kp * self._error

    def get_kie(self):
        return self._integral * self.ki

    def get_kde(self):
        return self._derivative * self.kd

    # def get_kie(self):
    #     return self.ki * self._integrator
