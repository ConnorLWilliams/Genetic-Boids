from boid import Boid, Genome
import configparser
from dataclasses import replace
import random
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class Simulation:

    def __init__(self, world_params, genome_params):

        self.population = self.generate_population(int(world_params['population_size']), float(world_params['boid_genome_startup_variance']), genome_params)

        x_min = float(world_params['xmin'])
        x_max = float(world_params['xmax'])
        y_min = float(world_params['ymin'])
        y_max = float(world_params['ymax'])

        world_bounds = ((x_min, x_max), (y_min, y_max))
        Boid.set_world_bounds(world_bounds)



    def generate_population(self, population_size, variation_rate, genome_params):
        default_genome = Genome(
            **{k: float(v) for k, v in genome_params.items()}
        )
        
        return [
            Boid(x = random.uniform(-100, 100),
                y = random.uniform(-100, 100),
                vx = random.uniform(2, 4),
                vy = random.uniform(2, 4),
                genome = default_genome.vary_genome(variation_rate))
            for _ in range(population_size)
        ]
    

    def tick(self):
        for boid in self.population:
            boid.get_update_vals(self.population)
            
        for boid in self.population:
            boid.update_vals()

if __name__ == "__main__":
    config = configparser.ConfigParser()
    try:
        config.read('config.ini')
    except configparser.Error as e:
        print(f"Error reading config file: {e}")

    sim = Simulation(config["World_Values"], config["Genome_Values"])
    
    fig, ax = plt.subplots()
    scat = ax.scatter([], [])

    ax.set_xlim(float(config["World_Values"]['xmin']), float(config["World_Values"]['xmax']))
    ax.set_ylim(float(config["World_Values"]["ymin"]), float(config["World_Values"]["ymax"]))

    def update(frame):
        sim.tick()
        x = [b.x for b in sim.population]
        y = [b.y for b in sim.population]
        scat.set_offsets(list(zip(x, y)))
        return scat,

    ani = FuncAnimation(fig, update, frames=200, interval=50, blit=True)
    plt.show() 
