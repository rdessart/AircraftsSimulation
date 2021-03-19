from .pid_controller import PIDController


class Autothrust():
    """Represent an autothrust system"""
    thrust_hold = 1
    speed_hold = 2

    def __init__(self, thrust_reduction: float = 0.9):
        self.thrust_red = thrust_reduction
        self.pid = PIDController(0.0, 0.0, 0.0, 0, 1.0, 1.0, 1.0/60.0)
        self.thrust_reduction = False
        self.target = 0.0
        self.active_mode = None

    def ThrustHold(self, target):
        self.active_mode = Autothrust.thrust_hold

    def SpeedHold(self, target):
        self.active_mode = Autothrust.speed_hold
        self.target = target
        Kp = 1.0
        Ki = 0.05
        Kd = 0.1
        limit = 1
        if self.thrust_reduction:
            limit = self.thrust_red
        self.pid = PIDController(Kp, Ki, Kd, 0.0, limit, 0.0, 1.0/60.0)

    def run(self, cas: float) -> float:
        if self.active_mode is None:
            return None
        elif self.active_mode == Autothrust.thrust_hold:
            if self.thrust_reduction:
                return self.thrust_red
            return 1.0

        elif self.active_mode == Autothrust.speed_hold:
            return self.pid.compute(self.target, cas)
