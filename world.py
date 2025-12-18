from boid import Boid, Genome
from prey import Prey, Prey_Genome
from predator import Predator, Predator_Genome
import configparser
from dataclasses import replace
import random
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class Simulation:

    def __init__(self, world_params, prey_genome_params, pred_genome_params):

        self.world = {}

        self.prey_population = self.generate_prey_population(int(world_params['prey_pop_size']), float(world_params['boid_genome_startup_variance']), prey_genome_params)

        self.pred_population = self.generate_predator_population(int(world_params['predator_pop_size']), float(world_params['boid_genome_startup_variance']), pred_genome_params)

        x_min = float(world_params['xmin'])
        x_max = float(world_params['xmax'])
        y_min = float(world_params['ymin'])
        y_max = float(world_params['ymax'])

        world_bounds = ((x_min, x_max), (y_min, y_max))
        Boid.set_world_bounds(world_bounds)
        
        # World Dictionary
        self.world['prey_population'] = self.prey_population
        self.world['predator_population'] = self.pred_population
        self.world['world_bound'] = world_bounds


    def generate_prey_population(self, population_size, variation_rate, genome_params):
        default_genome = Prey_Genome(
            **{k: float(v) for k, v in genome_params.items()}
        )
        
        return [
            Prey(x = random.uniform(-100, 100),
                y = random.uniform(-100, 100),
                vx = random.uniform(2, 4),
                vy = random.uniform(2, 4),
                genome = default_genome.vary_genome(variation_rate))
            for _ in range(population_size)
        ]

    def generate_predator_population(self, population_size, variation_rate, genome_params):
        default_genome = Predator_Genome(
            **{k: float(v) for k, v in genome_params.items()}
        )
        
        return [
            Predator(x = random.uniform(-100, 100),
                y = random.uniform(-100, 100),
                vx = random.uniform(2, 4),
                vy = random.uniform(2, 4),
                genome = default_genome.vary_genome(variation_rate))
            for _ in range(population_size)
        ] 

    def tick(self):
        for prey in self.prey_population:
            prey.get_update_vals(self.world)
        
        for pred in self.pred_population:
            pred.get_update_vals(self.world)
        
        for boid in self.prey_population:
            boid.update_vals()

        for boid in self.pred_population:
            boid.update_vals()

if __name__ == "__main__":
    config = configparser.ConfigParser()
    try:
        config.read('config.ini')
    except configparser.Error as e:
        print(f"Error reading config file: {e}")

    sim = Simulation(config["World_Values"], config["Prey_Values"], config["Predator_Values"])
    
    fig, ax = plt.subplots()
    # Initial scatter plots
    prey_scat = ax.scatter([], [], c='blue', label='Prey')
    pred_scat = ax.scatter([], [], c='red', label='Predators')

    ax.set_xlim(float(config["World_Values"]['xmin']), float(config["World_Values"]['xmax']))
    ax.set_ylim(float(config["World_Values"]["ymin"]), float(config["World_Values"]["ymax"]))

    def update(frame):
        sim.tick()
        
        # Prey positions
        prey_x = [b.x for b in sim.prey_population]
        prey_y = [b.y for b in sim.prey_population]
        prey_scat.set_offsets(list(zip(prey_x, prey_y)))

        # Predator positions
        pred_x = [p.x for p in sim.pred_population]
        pred_y = [p.y for p in sim.pred_population]
        pred_scat.set_offsets(list(zip(pred_x, pred_y)))

        return prey_scat, pred_scat

    ani = FuncAnimation(fig, update, frames=200, interval=50, blit=True)
    plt.show() 
