import copy
class Population:
    def __init__(self, individuals: list, nc: int, mutation_rate: float, crossover_rate: float):
        self.individuals = copy.deepcopy(individuals)
        self.size = len(individuals)
        self.crossover_points = nc
        self.fitness_avg = 0
        self.fitness = 0
        self.best_fitness = 0
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        