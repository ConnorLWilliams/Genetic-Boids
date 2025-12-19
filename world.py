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
import sys
import time

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
        killed_prey = set()
        
        # TODO: Find a way to have this happen in the existing update loops
        for pred in self.pred_population:
            for prey in self.prey_population:
                # NOTE: This can be done with intersecting paths to avoid tunneling, using radius for now.
                if prey in killed_prey:
                    continue

                distance = math.dist([pred.x, pred.y], [prey.x, prey.y])

                if distance < pred.genome.catch_radius:
                    killed_prey.add(prey)
                    break # (Only kill 1 prey at a time)

        for p in killed_prey:
            self.prey_population.remove(p)

        for _ in range(len(killed_prey)):
            self.prey_population.append(breed(self.prey_population))

def real_time(sim, genome_params):
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
        nonlocal frame_count
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

def fast_sim(sim, itterations):
    history = defaultdict(list)
    gene_names = list(vars(sim.prey_population[0].genome).keys())
    
    start_time = time.perf_counter()

    for _ in range(itterations):
        sim.tick()
        
        for param in gene_names:
            values = [getattr(b.genome, param) for b in sim.prey_population]
            avg_value = np.mean(values)
            history[param].append(avg_value)
    
    end_time = time.perf_counter()

    elapsed_time = end_time - start_time
    print(f"Runtime: {elapsed_time:0.4f} seconds") 

    plot_evolution(history, gene_names, itterations)

def plot_evolution(history, gene_names, iterations):
    """
    Create subplots showing evolution of each parameter over time

    NOTE: Same as above this is plotting is generated with Claude for now
    """
    num_params = len(gene_names)
    
    # Calculate grid dimensions
    cols = 3
    rows = (num_params + cols - 1) // cols  # Ceiling division
    
    fig, axes = plt.subplots(rows, cols, figsize=(15, 4 * rows))
    fig.suptitle('Evolution of Genome Parameters Over Time', fontsize=16, y=0.995)
    
    # Flatten axes array for easy indexing
    if num_params == 1:
        axes = [axes]
    else:
        axes = axes.flatten() if num_params > cols else axes
    
    for idx, param in enumerate(gene_names):
        ax = axes[idx]
        generations = list(range(len(history[param])))
        
        ax.plot(generations, history[param], linewidth=2, color='blue')
        ax.set_title(f'{param}', fontsize=12, fontweight='bold')
        ax.set_xlabel('Generation')
        ax.set_ylabel('Average Value')
        ax.grid(True, alpha=0.3)
    
    # Hide extra subplots if any
    for idx in range(num_params, len(axes)):
        axes[idx].set_visible(False)
    
    plt.tight_layout()
    plt.show()




if __name__ == "__main__":
    config = configparser.ConfigParser()
    try:
        config.read('config.ini')
    except configparser.Error as e:
        print(f"Error reading config file: {e}")

    sim = Simulation(config["World_Values"], config["Prey_Values"], config["Predator_Values"])
   
    if len(sys.argv) > 1:
        match sys.argv[1]:
            case 'fast_sim':
                try:
                    itter = int(sys.argv[2])
                except:
                    print("number of itterations misformated or not put. Default: 10,000")
                    itter = 10000
                fast_sim(sim, itter)
            case _: # Also counts for if they put 'real_time'
                gene_names = list(vars(sim.prey_population[0].genome).keys())
                
                try:
                    gene_display_list = sys.argv[2:]

                    if len(gene_display_list) > 6:
                        raise ValueError("Too Many Values")

                    elif not all(item in gene_names for item in gene_display_list): # is the input not a subset?
                        raise ValueError("Failed Subset")

                    else:
                        genome_params = gene_display_list
                except:
                    print("Input display genes not valid or not given (max 6). Displaying default")
                    genome_params = ['centering_factor', 'predator_turn_factor', 'speed_pref']

                # Add choosing graph parameters here

                real_time(sim, genome_params)

        sys.exit(0) # end the script

    genome_params = ['centering_factor', 'predator_turn_factor', 'speed_pref']
    real_time(sim, genome_params) # Default Behavoir 
