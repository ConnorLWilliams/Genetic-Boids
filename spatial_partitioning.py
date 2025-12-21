import math
from boid import Boid, Genome
import numpy as np

class SpatialGrid:
    def __init__(self, bounds):
        self.cell_size: int = 20
        self.bounds: tuple[tuple[float, float], tuple[float, float]] = bounds
        self.cells = {}

    def build_grid(self, population):

        self.cells = {}
        for p in population:
            cell_coords = self.calculate_cell(p.x, p.y)
            if cell_coords not in self.cells:
                self.cells[cell_coords] = []
            self.cells[cell_coords].append(p)

    def calculate_cell(self, x, y):
        cell_x = math.floor((x - self.bounds[0][0]) / self.cell_size)
        cell_y = math.floor((y - self.bounds[1][0]) / self.cell_size)
        return (cell_x, cell_y)

    def get_nearby_boids(self, boid):
        """
        Return all of the boids in cells in the visual range
        """
        my_cell = self.calculate_cell(boid.x, boid.y)
        cell_radius = math.ceil(boid.genome.visual_range / self.cell_size)

        cells_to_group = []
        for dx in range(-cell_radius, cell_radius):
            for dy in range(-cell_radius, cell_radius):
                cell = (my_cell[0] + dx, my_cell[1] + dy)
                cells_to_group.append(cell)
        
        nearby = []
        for cell in cells_to_group:
            if cell in self.cells:
                for b in self.cells[cell]:
                    nearby.append(b)

        return nearby


