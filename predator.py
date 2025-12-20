from boid import Boid, Genome
from dataclasses import dataclass
from typing import ClassVar, TypedDict, Tuple
import random
import math

@dataclass
class Predator_Genome(Genome):
    speed_limit: float # How fast can I go
    speed_pref: float # How fast do I like to go
    vision_radius: float # How far can I see
    close_radius: float # Radius in which I look for a group
    group_follow_size: int # What is the smallest size I consider a group
    grouping_radius: float # How close to another Boid does one have to be to be considered a group
    catch_radius: float # How close do I start following a Boid

class Predator(Boid):
    _max_speed: ClassVar[float] = 15
    _world_bounds: ClassVar[Tuple[Tuple[float, float], Tuple[float, float]]] = ((-150, 150), (-150, 150))

    def init(self, x, y, vx, vy, genome: Predator_Genome):
        self.x: float = x
        self.y: float = y
        self.vx: float = vx
        self.vy: float = vy
        self.age: int = 0
        self.kills: int = 0
        self.genome: Predator_Genome = genome

        self.update_dict: dict = {}

    def get_update_vals(self, world):

        #TODO: This is placeholder code --> figuring out specifics of Predator Functions

        # New Behavoir Idea:
            # 3 Rings of Behavoir
                # Far: No Prey Boids Near
                    # Move like a Boid --> Try to get close to any group
                    # Move towards the average point of all boids in visual range
                # Close: Near some Prey Boids
                    # Move towards the closest group of n boids --> Pick a group to chase (clustering? DBScan?)
                        # Has params: min_members, and max_hop_dist
                    # Move towards the center of detected clusters
                # Strike: Next to a Prey Boid
                    # Move only towards the closest Boid --> Pick a Boid to chase
                    # Close distance, Chase distance
                        # Find a Boid in Close range (very small), Chase it as long as it is in Chase Range (Slightly Larger)


        self.age += 1

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
    
    def far_behavoir(self, world):
        pass

    def close_behavoir(self, world):
        pass

    def strike_behavoir(self, world):
        pass

    def simple_behavoir(self, world)

    def count_kill(self):
        self.kills += 1
        
    def get_fitness(self):
        return (self.kills / self.age)

