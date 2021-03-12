class PIDController():
    """Emulate a PID controller"""
    def __init__(self, kp: float, ki: float,
                 kd: float, target: float, dt: float,
                 anti_windup: bool = True, max_val: float = 1.0):
        self.kp = kp,
        self.ki = ki,
        self.kd = kd,
        self.target = target
        self.error = 0.0
        self.error_last = 0.0
        self.dt = dt
        self.proportional_error = 0.0
        self.integral_error = 0.0
        self.derivative_error = 0.0
        self.anti_windup = anti_windup
        self.max_val = max_val
        self.reveverse = False

    def compute(self, pos):
        self.error = self.target - pos
        if self.reveverse:
            self.error = pos - self.target
        self.derivative_error = (self.error - self.error_last) / self.dt
        self.error_last = self.error
        self.output = self.kp[0] * self.error\
            + self.ki[0] * self.integral_error\
            + self.kd[0] * self.derivative_error

        if self.anti_windup and abs(self.output) >= self.max_val \
           and (((self.error >= 0) and (self.integral_error >= 0))
           or ((self.error < 0) and (self.integral_error < 0))):
            self.integral_error = self.integral_error
        else:
            # rectangular integration
            self.integral_error += self.error * self.dt
        if self.output >= self.max_val:
            self.output = self.max_val
        elif self.output <= -1 * self.max_val:
            self.output = -1 * self.max_val
        return self.output

    def get_kpe(self):
        return self.kp[0] * self.error

    def get_kde(self):
        return self.kd[0] * self.derivative_error

    def get_kie(self):
        return self.ki[0] * self.integral_error


class PIDController2():
    """Updated version of PIDController"""
    def __init__(self, Kp: float = 0.0, Ki: float = 0.0, Kd: float = 0.0,
                 limitMin: float = 0.0, limitMax: float = 0.0,
                 tau: float = 0.0, dp: float = 0.0):
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
        self.dp = dp
        self.use_low_pass_filter = False
        self.use_kick_avoidance = False

        self._integrator = 0.0
        self._differenciator = 0.0
        self._previousError = 0.0
        self._previousMeasurement = 0.0

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
        error = target - measurement
        proportional = error * self.kp
        self._integrator += 0.5 * self.ki * dt * (error + self._previousError)
        if self.limitMax > self._integrator:
            limitIntMax = self.limitMax - proportional
        elif self.limitMin < self._integrator:
            limitIntMin = self.limitMin - proportional
        
        if self._integrator > self.limitMax:
            self._integrator = self.limitMax
        elif self._integrator < self.limitMin:
            self._integrator = self.limitMin
        
        if self.use_kick_avoidance:
            differenciator_delta = measurement - self._previousMeasurement
        else:
            differenciator_delta = error - self._previousError
        self._differenciator = (2.0 * self.Kd * differenciator_delta)
        if self.use_low_pass_filter:
            self._differenciator += ((2.0 * self.tau * dt)
                                    * self._differenciator)\
                                 / (2.0 * self.tau * dt)
        output = proportional + self._integrator + self._differenciator
        if output > self.limitMax:
            output = self.limitMax
        elif output < self.limitMin:
            output =  self.limitMin
        self._previousError = error
        self._previousMeasurement = measurement
        return output