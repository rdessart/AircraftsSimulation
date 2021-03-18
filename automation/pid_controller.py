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

        self._integrator = 0.0
        self._differenciator = 0.0
        self._previousError = 0.0
        self._previousMeasurement = 0.0
        self._error = 0.0

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
        limitIntMax = 0.0
        limitIntMin = 0.0
        self._error = target - measurement
        proportional = self._error * self.kp
        self._integrator += 0.5 * self.ki * dt *\
            (self._error + self._previousError)
        if self.limitMax > proportional:
            limitIntMax = self.limitMax - proportional
        elif self.limitMin < proportional:
            limitIntMin = self.limitMin - proportional

        if self._integrator > limitIntMax:
            self._integrator = limitIntMax
        elif self._integrator < limitIntMin:
            self._integrator = limitIntMin

        if self.use_kick_avoidance:
            differenciator_delta = measurement - self._previousMeasurement
        else:
            differenciator_delta = self._error - self._previousError
        self._differenciator = (2.0 * self.kd * differenciator_delta)
        if self.use_low_pass_filter:
            self._differenciator += ((2.0 * self.tau * dt)
                                     * self._differenciator)\
                                 / (2.0 * self.tau * dt)
        output = proportional + self._integrator + self._differenciator
        if output > self.limitMax:
            output = self.limitMax
        elif output < self.limitMin:
            output = self.limitMin
        self._previousError = self._error
        self._previousMeasurement = measurement
        return output

    def get_kpe(self):
        return self.kp * self._error

    def get_kie(self):
        return self._integrator * self.ki

    def get_kde(self):
        return self._differenciator * self.kd

    # def get_kie(self):
    #     return self.ki * self._integrator
