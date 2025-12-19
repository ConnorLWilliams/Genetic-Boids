import math
from boid import Boid, Genome
import random

def breed(population: list[Boid]):
    parents = selection(population, type(population[0])._selection_type)
    child = crossover(parents, type(population[0])._crossover_type)
    mutation(child, type(population[0])._mutation_rate)
    return child

def selection(population: list[Boid], selection_type: str) -> tuple[Boid, Boid]:
    match(selection_type):
        case "roulette":
            return roulette_selection(population)

def roulette_selection(population: list[Boid]) -> tuple[Boid, Boid]:
    weights = []
    total_fitness = 0
    for p in population:
        w = p.get_fitness()
        weights.append(w)
        total_fitness += w

    for w in range(len(weights)):
        weights[w] = weights[w] / total_fitness # Normalize the total_fitness
    
    def select(population, weights):
        rand_select = random.random()
        accumulate = 0
        
        for w in range(len(weights)):
            accumulate += weights[w]
            if accumulate >= rand_select:
                return population[w]
        
        return population[0]

    p1 = select(population, weights)
    p2 = select(population, weights)

    return (p1, p2)

def crossover(parents: tuple[Boid, Boid], crossover_type: str):
    match(crossover_type):
        case 'bit-mask':
            return bit_mask_crossover(parents)

def bit_mask_crossover(parents: tuple[Boid, Boid]):
    p1 = parents[0]
    p2 = parents[1]

    genetic_makeup = vars(p1.genome)
    gene_names = list(genetic_makeup.keys())
    
    b1 = [random.randint(0, 1) for _ in range(len(genetic_makeup))]
    
    genome_dict = {}

    for i, gene_name in enumerate(gene_names):
        if b1[i] == 1:
            genome_dict[gene_name] = getattr(p1.genome, gene_name)
        else:
            genome_dict[gene_name] = getattr(p2.genome, gene_name) 
    child = type(p1)(x = random.uniform(p1._world_bounds[0][0], p1._world_bounds[0][1]),
                y = random.uniform(p2._world_bounds[1][0], p2._world_bounds[1][1]),
                vx = p1.vx,
                vy = p1.vy,
                genome = type(p1.genome)(**genome_dict))

    return child


def mutation(child, mutation_rate):
    check = random.random()
    if check <= mutation_rate:
        child.genome = child.genome.vary_genome(mutation_rate)


