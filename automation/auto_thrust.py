from .pid_controller import PIDController


class Autothrust():
    """Represent an autothrust system"""
    speed_hold = 2

    def __init__(self, thrust_reduction: float = 0.9):
        self.thrust_red = thrust_reduction
        self.pid = PIDController(0.0, 0.0, 0.0, 0, 1.0, 1.0, 1.0/60.0)
        self.thrust_reduction = False
        self.target = 0.0
        self.active_mode = None

    def SpeedHold(self, target):
        self.active_mode = Autothrust.speed_hold
        self.target = target
        kP = 1.0
        kI = 0.05
        kD = 0.1
        self.pid = PIDController(kP, kI, kD, 0.0, 1.0, 0, 1.0/60.0)

    def run(self, cas: float) -> float:
        if self.active_mode != Autothrust.speed_hold:
            return None
        return self.pid.compute(self.target, cas)
