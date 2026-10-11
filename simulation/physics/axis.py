from dataclasses import dataclass, asdict
@dataclass
class Axis:
    position: float=0.0
    velocity: float=0.0
    acceleration: float=0.0
    target: float=0.0
    error: float=0.0
    max_velocity: float=500.0
    max_acceleration: float=5000.0
    def step(self,target,dt,freeze=False,gain=1.0):
        self.target=target; old=self.velocity
        desired=max(-self.max_velocity,min(self.max_velocity,(target-self.position)/dt))
        dv=max(-self.max_acceleration*dt,min(self.max_acceleration*dt,desired-old))
        self.velocity=0.0 if freeze else (old+dv)*gain
        delta=self.velocity*dt
        if abs(delta)>abs(target-self.position) and delta*(target-self.position)>0:
            delta=target-self.position; self.velocity=delta/dt
        self.position+=delta; self.acceleration=(self.velocity-old)/dt
        self.error=target-self.position
        return delta
    def state(self): return asdict(self)|{'actual':self.position}
