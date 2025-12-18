from dataclasses import dataclass
from typing import ClassVar, TypedDict, Tuple
import random
import math

@dataclass
class Genome:
    visual_range: float # How far can I see
    turning_factor: float # How fast to turn from screen edges
    screen_margin: float # How close can I get to screen edges
    bias_direction: float # What direction am I biased towards
    bias_val: float # How biased am I
    speed_limit: float # How fast can I go
    speed_pref: float # What is my prefered speed
    propulsion: float # How much energy do I add when I want
    avoid_factor: float # How much do I avoid nearby boids
    protected_range: float # How close of boids do I avoid
    matching_factor: float # How much do I match speeds
    centering_factor: float # How much do I match position

    def vary_genome(self, rate) -> "Genome":
        """
        Randomly varies each field by +- range
        """
        return Genome(
            **{
                field: getattr(self, field) * (1 + random.uniform(-rate, rate))
                for field in self.__dataclass_fields__
            }
        )

class Boid:
    _max_speed: ClassVar[float] = 10 # Global Speed Limit for Boids
    _world_bounds: ClassVar[Tuple[Tuple[float, float], Tuple[float, float]]] = ((-150, 150), (-150, 150)) #TODO: Need to set from world

    def __init__(self, x, y, vx, vy, genome: Genome):
        # General
        self.x: float = x
        self.y: float = y
        self.vx: float = vx
        self.vy: float = vy # might add a starting vel mag to genome
        age: int = 0
        self.genome: Genome = genome

        self.update_dict = {}
        
    def get_update_vals(self, boids: ["Boid"]):
        
        boid_yvel_ave = boid_ypos_avg = boid_xvel_ave = boid_xpos_avg = boid_neighbor_count = close_dy = close_dx = 0

        boid_neighbor_count = 0

        new_x = 0
        new_y = 0
        new_vx = 0
        new_vy = 0

        for boid in boids:
            distance = math.dist([self.x, self.y], [boid.x, boid.y])

            if (distance < self.genome.visual_range):
                if (distance > self.genome.protected_range): # sweet spot for flocking
                    boid_xpos_avg += boid.x
                    boid_ypos_avg += boid.y
                    boid_xvel_ave += boid.vx
                    boid_yvel_ave += boid.vy

                    boid_neighbor_count+=1
                
                else: # too close --> avoid
                    close_dx += self.x - boid.x
                    close_dy += self.y - boid.y

        if (boid_neighbor_count > 0):
            boid_xpos_avg = boid_xpos_avg / boid_neighbor_count
            boid_ypos_avg = boid_ypos_avg / boid_neighbor_count
            boid_xvel_ave = boid_xvel_ave / boid_neighbor_count
            boid_yvel_ave = boid_yvel_ave / boid_neighbor_count

            new_vx = (self.vx + 
                       (boid_xpos_avg - self.x)*self.genome.centering_factor + 
                       (boid_xvel_ave - self.vx)*self.genome.matching_factor)
            
            new_vy = (self.vy + 
                      (boid_ypos_avg - self.y)*self.genome.centering_factor + 
                      (boid_yvel_ave - self.vy)*self.genome.matching_factor)

        new_vx = new_vx + (close_dx*self.genome.avoid_factor)
        new_vy = new_vy + (close_dy*self.genome.avoid_factor)

        # Check that I am still in the screen_margin


        left_margin_check = self._world_bounds[0][0] + self.genome.screen_margin # -150 + 20 = -130
        right_margin_check = self._world_bounds[0][1] - self.genome.screen_margin # 150 - 20 = 130
        bottom_margin_check = self._world_bounds[1][0] + self.genome.screen_margin
        top_margin_check = self._world_bounds[1][1] - self.genome.screen_margin

        if self.x < left_margin_check: # too far left
            new_vx = new_vx + self.genome.turning_factor
        elif self.x > right_margin_check: # too far right
            new_vx = new_vx - self.genome.turning_factor

        if self.y < bottom_margin_check:
            new_vy = new_vy + self.genome.turning_factor
        elif self.y > top_margin_check:
            new_vy = new_vy - self.genome.turning_factor
        

        # Add bias
        theta = math.radians(self.genome.bias_direction)

        bias_dx = math.cos(theta)
        bias_dy = math.sin(theta)
         
        new_vx = (1 - self.genome.bias_val) * new_vx + self.genome.bias_val * bias_dx
        new_vy = (1 - self.genome.bias_val) * new_vy + self.genome.bias_val * bias_dy

        speed = math.hypot(new_vx, new_vy)

        target = self.genome.speed_pref
        gain = self.genome.propulsion

        if speed > 0:
            new_vx += gain * (target - speed) * (new_vx / speed)
            new_vy += gain * (target - speed) * (new_vy / speed)

        if speed > self._max_speed:
            new_vx = (new_vx/speed)*self._max_speed
            new_vy = (new_vy/speed)*self._max_speed
        
        new_x = self.x + new_vx
        new_y = self.y + new_vy

        self.update_dict = {
                'new_x': new_x,
                'new_y': new_y,
                'new_vx': new_vx,
                'new_vy': new_vy
                }


    def update_vals(self):
        self.x = self.update_dict['new_x']
        self.y = self.update_dict['new_y']
        self.vx = self.update_dict['new_vx']
        self.vy = self.update_dict['new_vy']

    @classmethod
    def set_max_speed(cls, speed: float):
        cls._max_speed = speed

    @classmethod
    def set_world_bounds(cls, bounds: Tuple[Tuple[float, float], Tuple[float, float]]):
        cls._world_bounds = bounds
