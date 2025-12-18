from boid import Boid, Genome
from dataclasses import dataclass
from typing import ClassVar, TypedDict, Tuple
import random
import math

@dataclass
class Predator_Genome(Genome):
    speed_limit: float
    speed_pref: float
    

class Predator(Boid):
    _max_speed: ClassVar[float] = 15
    _world_bounds: ClassVar[Tuple[Tuple[float, float], Tuple[float, float]]] = ((-150, 150), (-150, 150))

    def init(self, x, y, vx, vy, genome: Predator_Genome):
        self.x: float = x
        self.y: float = y
        self.vx: float = vx
        self.vy: float = vy
        age: int = 0
        self.genome: Predator_Genome = genome

        self.update_dict: dict = {}

    def get_update_vals(self, world):

        #TODO: This is placeholder code --> figuring out specifics of Predator Functions

        prey = world['prey_population']
            
        min_dist = float("inf")
        min_x = 0.0
        min_y = 0.0

        for p in prey:
            distance = math.dist([self.x, self.y], [p.x, p.y])
            if distance < min_dist:
                min_dist = distance
                min_x = p.x
                min_y = p.y

        dx = min_x - self.x
        dy = min_y - self.y
        if min_dist > 0: # Calculate unit vectors
            ux = dx / min_dist
            uy = dy / min_dist
        else:
            ux = uy = 0.0
            
        new_vx = ux * self.genome.speed_pref
        new_vy = uy * self.genome.speed_pref
        new_x = self.x + new_vx
        new_y = self.y + new_vy



        self.update_dict = {
                'new_x': new_x,
                'new_y': new_y,
                'new_vx': new_vx,
                'new_vy': new_vy
                }


