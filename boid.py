from dataclasses import dataclass
from typing import ClassVar, TypedDict, Tuple
import random
import math
from abc import ABC, abstractmethod

@dataclass
class Genome(ABC):
    
    visual_range: float

    def vary_genome(self, rate) -> "Genome":
        """
        Randomly varies each field by +- range
        """
        return self.__class__(
            **{
                field: getattr(self, field) * (1 + random.uniform(-rate, rate))
                for field in self.__dataclass_fields__
            }
        )

class Boid(ABC):
    _max_speed: ClassVar[float] = 10 # Global Speed Limit for Boids
    _world_bounds: ClassVar[Tuple[Tuple[float, float], Tuple[float, float]]] = ((-150, 150), (-150, 150))
    _selection_type: ClassVar[str] = "roulette"
    _mutation_rate: ClassVar[float] = 0.15
    _crossover_type: ClassVar[str] = "bit-mask"

    def __init__(self, x, y, vx, vy, genome: Genome):
        # General
        self.x: float = x
        self.y: float = y
        self.vx: float = vx
        self.vy: float = vy
        self.age: int = 0
        self.genome: Genome = genome

        self.update_dict = {}
       
    @abstractmethod
    def get_update_vals(self, world):
        pass
    
    @abstractmethod
    def get_fitness(self):
        pass

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

    @classmethod
    def set_selection_type(cls, selection_type: str):
        cls._selection_type = selection_type
