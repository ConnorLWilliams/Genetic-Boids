from boid import Boid, Genome
from prey import Prey, Prey_Genome
from predator import Predator, Predator_Genome
import configparser
from dataclasses import replace
import random
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import math
from Genetic_Algorithm import breed
from collections import defaultdict
import numpy as np

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

        #TODO: Set Evolution Parameters for Prey and Predators from ini
        
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

        self.update_population()

    def update_population(self):
        killed_prey = []
        
        # TODO: Find a way to have this happen in the existing update loops
        for pred in self.pred_population:
            for prey in self.prey_population:
                # NOTE: This can be done with intersecting paths to avoid tunneling, using radius for now.
                if prey in killed_prey:
                    pass

                distance = math.dist([pred.x, pred.y], [prey.x, prey.y])

                if distance < pred.genome.catch_radius:
                    killed_prey.append(prey)
                    break # (Only kill 1 prey at a time)

        for p in killed_prey:
            self.prey_population.remove(p)

        for _ in range(len(killed_prey)):
            self.prey_population.append(breed(self.prey_population))

if __name__ == "__main__":
    config = configparser.ConfigParser()
    try:
        config.read('config.ini')
    except configparser.Error as e:
        print(f"Error reading config file: {e}")

    sim = Simulation(config["World_Values"], config["Prey_Values"], config["Predator_Values"])
   
    #NOTE: The code below that handles the plotting was made with help of Claude AI, I am planning to make this some kind of accessable web app so this is a placeholder visualization for testing.
    fig = plt.figure(figsize=(20, 10))
    gs = fig.add_gridspec(3, 4, hspace=0.3, wspace=0.3)

    # Main sim plot
    ax_sim = fig.add_subplot(gs[:, 0:2])
    ax_sim.set_title('Simulation')
    ax_sim.set_xlim(float(config["World_Values"]['xmin']), float(config["World_Values"]['xmax']))
    ax_sim.set_ylim(float(config["World_Values"]["ymin"]), float(config["World_Values"]["ymax"]))

    # Scatter plots for sim
    prey_scat = ax_sim.scatter([], [], c='blue', label='Prey', s=20)
    pred_scat = ax_sim.scatter([], [], c='red', label='Predators', s=30)
    ax_sim.legend()

    genome_params = ['avoid_factor', 'matching_factor', 'centering_factor', 'predator_detection_range', 'predator_turn_factor', 'speed_pref']

    # Create subplots for each genome parameter
    param_axes = {}
    param_lines = {}
    history = defaultdict(list)

    for idx, param in enumerate(genome_params):
        row = idx // 2
        col = 2 + (idx % 2)
        ax = fig.add_subplot(gs[row, col])
        ax.set_title(f'Avg {param}')
        ax.set_xlabel('Generation')
        ax.set_ylabel('Value')
        param_axes[param] = ax
        line, = ax.plot([], [], 'b-', linewidth=2)
        param_lines[param] = line

    frame_count = 0

    def update(frame):
        global frame_count
        frame_count += 1
    
        sim.tick()
    
        # Update prey positions
        prey_x = [b.x for b in sim.prey_population]
        prey_y = [b.y for b in sim.prey_population]
        prey_scat.set_offsets(list(zip(prey_x, prey_y)))
    
        # Update predator positions
        pred_x = [p.x for p in sim.pred_population]
        pred_y = [p.y for p in sim.pred_population]
        pred_scat.set_offsets(list(zip(pred_x, pred_y)))
    
        # Calculate and store average genome parameters
        if sim.prey_population:
            for param in genome_params:
                values = [getattr(b.genome, param) for b in sim.prey_population]
                avg_value = np.mean(values)
                history[param].append(avg_value)
            
                # Update the corresponding line plot
                generations = list(range(len(history[param])))
                param_lines[param].set_data(generations, history[param])
            
                # Adjust axis limits
                ax = param_axes[param]
                ax.relim()
                ax.autoscale_view()
    
        # Update title with population counts
        ax_sim.set_title(f'Simulation - Frame {frame_count} | Prey: {len(sim.prey_population)} | Predators: {len(sim.pred_population)}')
    
        return [prey_scat, pred_scat] + list(param_lines.values())

    ani = FuncAnimation(fig, update, frames=None, interval=30, blit=False)
    plt.show()
