"""
Optimization Algorithm
=======================
Currently: Memetic Algorithm (GA + Hill Climbing local search)
This module is a placeholder — swap the algorithm by replacing this file.

To switch algorithms:
1. Replace the Optimizer class with your preferred algorithm
2. Keep the same interface: __init__(farm_params, seed_variety) and run() -> dict
3. run() must return a dict with 'planting_density' and 'fertilizer_composition'
"""

import copy
import random
import pandas as pd
from pathlib import Path
from config.params import ALGORITHM_PARAMS, LOCAL_SEARCH_PARAMS, CHROMOSOME_CONSTRAINTS
from algorithm.chromosome import (
    generate_random_chromosome, generate_smart_chromosome, validate_chromosome
)
from models.fitness import Fitness


class Optimizer:
    """
    Memetic Algorithm optimizer for corn farming inputs.

    Interface:
        optimizer = Optimizer(farm_params, seed_variety)
        best_solution = optimizer.run()
    """

    BALANCED_FERTILIZER_ID = 'F05'
    NEIGHBOR_DENSITY_ADJUSTMENT = 1000
    NEIGHBOR_FERTILIZER_ADJUSTMENT = 0.1

    def __init__(self, farm_params, seed_variety, random_seed=None):
        self.farm_params = farm_params
        self.seed_variety = seed_variety
        self.random_seed = random_seed
        if random_seed is not None:
            random.seed(random_seed)

        self.population_size = ALGORITHM_PARAMS['population_size']
        self.max_generations = ALGORITHM_PARAMS['max_generations']
        self.mutation_rate = ALGORITHM_PARAMS['mutation_rate']
        self.crossover_rate = ALGORITHM_PARAMS['crossover_rate']
        self.elitism_count = ALGORITHM_PARAMS['elitism_count']
        self.mutation_step_size = ALGORITHM_PARAMS['mutation_step_size']

        self.local_search_probability = LOCAL_SEARCH_PARAMS['local_search_probability']
        self.no_improvement_threshold = LOCAL_SEARCH_PARAMS['no_improvement_threshold']
        self.max_iterations_safety_limit = LOCAL_SEARCH_PARAMS['max_iterations_safety_limit']

        self.population = []
        self.fitness_scores = []
        self.best_solution = None
        self.best_fitness = float('-inf')
        self.generation = 0
        self.fitness_history = []
        self.local_search_count = 0

        self.data_dir = Path(__file__).parent.parent / 'data'
        self.fertilizer_data = pd.read_csv(self.data_dir / 'region_6_fertilizers.csv')
        self.constraints = CHROMOSOME_CONSTRAINTS

        self.fitness_calculator = Fitness(
            farm_area_ha=farm_params['farm_area_ha'],
            seed_variety=seed_variety,
            planting_density=0,
            fertilizer_composition={},
            topography=farm_params['topography'],
            soil_type=farm_params['soil_type'],
            soil_ph=farm_params['soil_ph'],
            initial_n_kg_ha=farm_params['initial_n_kg_ha'],
            initial_p_kg_ha=farm_params['initial_p_kg_ha'],
            initial_k_kg_ha=farm_params['initial_k_kg_ha'],
            planting_month=farm_params['planting_month'],
            irrigation_available=farm_params['irrigation_available'],
            data_dir=str(self.data_dir)
        )

    def initialize_population(self):
        """Create initial population: 50% smart + 50% random."""
        self.population = []
        smart_size = self.population_size // 2

        for _ in range(smart_size):
            chrom, valid = generate_smart_chromosome(
                self.fertilizer_data, self.seed_variety,
                self.farm_params, self.constraints, self.farm_params['farm_area_ha']
            )
            if valid:
                self.population.append(chrom)
            else:
                chrom, valid = generate_random_chromosome(
                    self.fertilizer_data, self.seed_variety,
                    self.constraints, self.farm_params['farm_area_ha']
                )
                if valid:
                    self.population.append(chrom)

        for _ in range(self.population_size - smart_size):
            chrom, valid = generate_random_chromosome(
                self.fertilizer_data, self.seed_variety,
                self.constraints, self.farm_params['farm_area_ha']
            )
            if valid:
                self.population.append(chrom)

    def _evaluate_chromosome(self, chromosome):
        """Calculate fitness for a single chromosome."""
        self.fitness_calculator.planting_density = chromosome['planting_density']
        self.fitness_calculator.fertilizer_composition = chromosome['fertilizer_composition']
        self.fitness_calculator.yield_model.planting_density = chromosome['planting_density']
        self.fitness_calculator.yield_model.fertilizer_composition = chromosome['fertilizer_composition']
        self.fitness_calculator.cost_model.planting_density = chromosome['planting_density']
        self.fitness_calculator.cost_model.fertilizer_composition = chromosome['fertilizer_composition']
        return self.fitness_calculator.calculate_fitness()

    def evaluate_fitness(self):
        """Calculate fitness for entire population."""
        self.fitness_scores = []
        for chrom in self.population:
            score = self._evaluate_chromosome(chrom)
            self.fitness_scores.append(score)
            if score > self.best_fitness:
                self.best_fitness = score
                self.best_solution = copy.deepcopy(chrom)

        gen_best = max(self.fitness_scores) if self.fitness_scores else float('-inf')
        self.fitness_history.append(gen_best)

    def selection(self):
        """Tournament selection."""
        size = ALGORITHM_PARAMS['tournament_size']
        
        def _pick():
            idxs = random.sample(range(len(self.population)), size)
            fits = [self.fitness_scores[i] for i in idxs]
            return self.population[idxs[fits.index(max(fits))]]

        return _pick(), _pick()

    def crossover(self, p1, p2):
        """Uniform crossover."""
        child = {
            'planting_density': random.choice([p1['planting_density'], p2['planting_density']]),
            'fertilizer_composition': {}
        }
        all_ids = set(p1['fertilizer_composition'].keys()) | set(p2['fertilizer_composition'].keys())
        for fid in all_ids:
            in1 = fid in p1['fertilizer_composition']
            in2 = fid in p2['fertilizer_composition']
            if in1 and in2:
                child['fertilizer_composition'][fid] = random.choice([
                    p1['fertilizer_composition'][fid],
                    p2['fertilizer_composition'][fid]
                ])
            elif in1:
                child['fertilizer_composition'][fid] = p1['fertilizer_composition'][fid]
            else:
                child['fertilizer_composition'][fid] = p2['fertilizer_composition'][fid]
        return child

    def mutation(self, chromosome):
        """Gaussian mutation."""
        mutated = copy.deepcopy(chromosome)
        sigma_d = mutated['planting_density'] * self.mutation_step_size
        mutated['planting_density'] += random.gauss(0, sigma_d)

        nutrients = list(mutated['fertilizer_composition'].keys())
        if nutrients:
            to_mutate = random.sample(nutrients, k=random.randint(1, min(2, len(nutrients))))
            for n in to_mutate:
                sigma = mutated['fertilizer_composition'][n] * self.mutation_step_size
                new_val = mutated['fertilizer_composition'][n] + random.gauss(0, sigma)
                mutated['fertilizer_composition'][n] = max(0.1, new_val)
        return mutated

    def repair_chromosome(self, chromosome):
        """Repair constraint violations."""
        repaired = copy.deepcopy(chromosome)

        dc = self.constraints['planting_density'][self.seed_variety]
        repaired['planting_density'] = max(dc['min'], min(dc['max'], repaired['planting_density']))

        for fid in repaired['fertilizer_composition']:
            repaired['fertilizer_composition'][fid] = max(0.1, repaired['fertilizer_composition'][fid])

        # Max types
        max_types = self.constraints['fertilizer'].get('max_fertilizer_types', 10)
        if len(repaired['fertilizer_composition']) > max_types:
            sorted_f = sorted(repaired['fertilizer_composition'].items(), key=lambda x: x[1], reverse=True)
            repaired['fertilizer_composition'] = dict(sorted_f[:max_types])

        # Max total sacks (proportional scaling)
        total = sum(repaired['fertilizer_composition'].values())
        max_sacks = self.constraints['fertilizer']['max_total_sacks_per_ha']
        if total > max_sacks:
            ratio = max_sacks / total
            for fid in repaired['fertilizer_composition']:
                repaired['fertilizer_composition'][fid] = max(0.1,
                    repaired['fertilizer_composition'][fid] * ratio)

        return repaired

    def _calculate_nutrient_percentages(self, chromosome):
        """Calculate current nutrient levels as percentages of recommended."""
        nitrogen_per_ha = 0
        phosphorus_per_ha = 0
        potassium_per_ha = 0

        fert_data = self.fertilizer_data.set_index('id')
        for fert_id, sacks in chromosome['fertilizer_composition'].items():
            if fert_id not in fert_data.index:
                continue
            nitrogen_per_ha   += sacks * 50 * (fert_data.loc[fert_id, 'nitrogen']   / 100)
            phosphorus_per_ha += sacks * 50 * (fert_data.loc[fert_id, 'phosphorus'] / 100)
            potassium_per_ha  += sacks * 50 * (fert_data.loc[fert_id, 'potassium']  / 100)

        total_n = self.farm_params['initial_n_kg_ha'] + nitrogen_per_ha
        total_p = self.farm_params['initial_p_kg_ha'] + phosphorus_per_ha
        total_k = self.farm_params['initial_k_kg_ha'] + potassium_per_ha

        # Percentages relative to DA recommended levels
        n_pct = (total_n / 134) * 100
        p_pct = (total_p /  41) * 100
        k_pct = (total_k / 102) * 100

        return n_pct, p_pct, k_pct

    def _identify_deficient_nutrients(self, n_pct, p_pct, k_pct):
        """Return nutrients sorted from most deficient to least."""
        nutrients = [('N', n_pct), ('P', p_pct), ('K', k_pct)]
        nutrients.sort(key=lambda x: x[1])
        return [n[0] for n in nutrients]

    def _find_best_fertilizer_for_nutrient(self, target_nutrient):
        """Find the fertilizer ID with the highest content of the target nutrient."""
        fert_data = self.fertilizer_data.set_index('id')
        col = {'N': 'nitrogen', 'P': 'phosphorus', 'K': 'potassium'}.get(target_nutrient)
        if col is None:
            return 'F05'
        try:
            best = fert_data[col].idxmax()
            return best if best and not __import__('pandas').isna(best) else 'F05'
        except Exception:
            return 'F05'

    def _get_neighbors(self, chromosome):
        """Generate 6 deficiency-driven promising neighbors (mirrors Comparative Analysis MA)."""
        neighbors = []

        n_pct, p_pct, k_pct = self._calculate_nutrient_percentages(chromosome)
        deficiency_ranking = self._identify_deficient_nutrients(n_pct, p_pct, k_pct)
        most_deficient   = deficiency_ranking[0]
        second_deficient = deficiency_ranking[1]

        best_for_most   = self._find_best_fertilizer_for_nutrient(most_deficient)
        best_for_second = self._find_best_fertilizer_for_nutrient(second_deficient)

        # Neighbor 1: Add 0.1 sack of best fertilizer for most-deficient nutrient
        nb1 = copy.deepcopy(chromosome)
        nb1['fertilizer_composition'][best_for_most] = (
            nb1['fertilizer_composition'].get(best_for_most, 0) + self.NEIGHBOR_FERTILIZER_ADJUSTMENT
        )
        neighbors.append(nb1)

        # Neighbor 2: Add 0.1 sack of best fertilizer for second-deficient nutrient
        nb2 = copy.deepcopy(chromosome)
        nb2['fertilizer_composition'][best_for_second] = (
            nb2['fertilizer_composition'].get(best_for_second, 0) + self.NEIGHBOR_FERTILIZER_ADJUSTMENT
        )
        neighbors.append(nb2)

        # Neighbor 3: Add 0.1 sack of balanced fertilizer (F05)
        nb3 = copy.deepcopy(chromosome)
        nb3['fertilizer_composition'][self.BALANCED_FERTILIZER_ID] = (
            nb3['fertilizer_composition'].get(self.BALANCED_FERTILIZER_ID, 0) + self.NEIGHBOR_FERTILIZER_ADJUSTMENT
        )
        neighbors.append(nb3)

        # Neighbor 4: Reduce most-applied fertilizer, add balanced F05
        nb4 = copy.deepcopy(chromosome)
        if nb4['fertilizer_composition']:
            max_f = max(nb4['fertilizer_composition'], key=nb4['fertilizer_composition'].get)
            nb4['fertilizer_composition'][max_f] -= self.NEIGHBOR_FERTILIZER_ADJUSTMENT
            if nb4['fertilizer_composition'][max_f] <= 0:
                del nb4['fertilizer_composition'][max_f]
            nb4['fertilizer_composition'][self.BALANCED_FERTILIZER_ID] = (
                nb4['fertilizer_composition'].get(self.BALANCED_FERTILIZER_ID, 0) + self.NEIGHBOR_FERTILIZER_ADJUSTMENT
            )
            neighbors.append(nb4)

        # Neighbor 5: Adjust density toward optimal
        nb5 = copy.deepcopy(chromosome)
        optimal = self.constraints['planting_density'][self.seed_variety]['optimal']
        if nb5['planting_density'] < optimal:
            nb5['planting_density'] = min(nb5['planting_density'] + self.NEIGHBOR_DENSITY_ADJUSTMENT,
                                          optimal * 1.1)
        elif nb5['planting_density'] > optimal * 1.1:
            nb5['planting_density'] = max(nb5['planting_density'] - self.NEIGHBOR_DENSITY_ADJUSTMENT,
                                          optimal)
        neighbors.append(nb5)

        # Neighbor 6: Synergy – increase density AND add balanced fertilizer together
        nb6 = copy.deepcopy(chromosome)
        max_density = self.constraints['planting_density'][self.seed_variety]['max']
        nb6['planting_density'] = min(
            nb6['planting_density'] + self.NEIGHBOR_DENSITY_ADJUSTMENT * 0.5,
            max_density
        )
        nb6['fertilizer_composition'][self.BALANCED_FERTILIZER_ID] = (
            nb6['fertilizer_composition'].get(self.BALANCED_FERTILIZER_ID, 0) + self.NEIGHBOR_FERTILIZER_ADJUSTMENT
        )
        neighbors.append(nb6)

        # Enforce max fertilizer types on all neighbors
        max_types = self.constraints['fertilizer'].get('max_fertilizer_types', 10)
        for nb in neighbors:
            if len(nb['fertilizer_composition']) > max_types:
                sorted_f = sorted(nb['fertilizer_composition'].items(), key=lambda x: x[1], reverse=True)
                nb['fertilizer_composition'] = dict(sorted_f[:max_types])

        return neighbors

    def hill_climb(self, chromosome):
        """Perform local search to refine a chromosome."""
        best = copy.deepcopy(chromosome)
        best_fitness = self._evaluate_chromosome(best)
        no_improve = 0
        iteration = 0

        while no_improve < self.no_improvement_threshold and iteration < self.max_iterations_safety_limit:
            iteration += 1
            neighbors = self._get_neighbors(best)
            improved = False

            for nb in neighbors:
                nb = self.repair_chromosome(nb)
                is_valid, _ = validate_chromosome(
                    nb, self.seed_variety, self.fertilizer_data,
                    self.farm_params['farm_area_ha'], self.constraints
                )
                if not is_valid:
                    continue
                nb_fitness = self._evaluate_chromosome(nb)
                if nb_fitness > best_fitness:
                    best = copy.deepcopy(nb)
                    best_fitness = nb_fitness
                    improved = True
                    no_improve = 0
                    break

            if not improved:
                no_improve += 1

        self.local_search_count += 1
        return best

    def run_generation(self):
        """Run one generation of MA (GA + selective local search)."""
        elite_idx = sorted(range(len(self.population)),
                           key=lambda i: self.fitness_scores[i], reverse=True)[:self.elitism_count]
        elites = [copy.deepcopy(self.population[i]) for i in elite_idx]

        new_pop = []
        local_search_slots = int(self.population_size * self.local_search_probability)

        while len(new_pop) < self.population_size - self.elitism_count:
            p1, p2 = self.selection()
            child = self.crossover(p1, p2) if random.random() < self.crossover_rate else copy.deepcopy(random.choice([p1, p2]))
            if random.random() < self.mutation_rate:
                child = self.mutation(child)
            child = self.repair_chromosome(child)

            # Local search on top slots (Partial Lamarckism)
            if len(new_pop) < local_search_slots:
                child = self.hill_climb(child)

            new_pop.append(child)

        self.population = elites + new_pop
        self.evaluate_fitness()
        self.generation += 1

    def run(self, progress_callback=None):
        """
        Run the optimization algorithm.

        Args:
            progress_callback: Optional callable(generation, max_gen, best_fitness)
                for reporting progress to UI.

        Returns:
            dict: Best chromosome found with 'planting_density' and 'fertilizer_composition'
        """
        self.initialize_population()
        self.evaluate_fitness()

        while self.generation < self.max_generations:
            self.run_generation()

            if progress_callback:
                progress_callback(self.generation, self.max_generations, self.best_fitness)

        return self.best_solution
