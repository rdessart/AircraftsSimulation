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
