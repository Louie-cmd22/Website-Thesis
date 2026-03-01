"""
Algorithm Parameters Configuration
===================================
Centralized configuration for the optimization algorithm.

Adapted from Comparative Analysis project for website use.
"""
    
# ========== ALGORITHM PARAMETERS ==========
# Currently using Memetic Algorithm (MA) settings
# Can be swapped to GA or other algorithm later

ALGORITHM_PARAMS = {
    'population_size': 100,
    'max_generations': 50,            # MA uses 50 generations + local search
    'crossover_rate': 0.9,
    'mutation_rate': 0.05,
    'elitism_count': 2,
    'tournament_size': 3,
    'early_stopping_generations': None,
    'random_seed': None,              # None = random each run for website
    'selection_method': 'tournament',
    'crossover_method': 'uniform',
    'mutation_method': 'gaussian',
    'boundary_handling': 'clipping',
    'mutation_step_size': 0.05,
}

# MA-Specific Local Search Parameters
LOCAL_SEARCH_PARAMS = {
    'local_search_probability': 0.1,
    'hill_climbing_max_iterations': 10,
    'hill_climbing_step_size': 0.05,
    'no_improvement_threshold': 5,
    'max_iterations_safety_limit': 100,
}

# ========== CHROMOSOME CONSTRAINTS ==========
CHROMOSOME_CONSTRAINTS = {
    'planting_density': {
        'Glutinous': {'min': 50000, 'max': 61112, 'optimal': 55556},
        'Hybrid':    {'min': 64286, 'max': 78572, 'optimal': 71429},
        'OPV':       {'min': 48000, 'max': 58666, 'optimal': 53333}
    },
    'fertilizer': {
        'max_total_sacks_per_ha': 12,
        'max_fertilizer_types': 5
    }
}

# ========== AGRONOMIC CONSTRAINTS ==========
MIN_NPK_ADEQUACY_PERCENTAGE = 0.85   # 85% minimum
MAX_NPK_PERCENTAGE = 1.15            # 115% maximum

# ========== RECOMMENDED NUTRIENT LEVELS (kg/ha) ==========
RECOMMENDED_N = 134
RECOMMENDED_P = 41
RECOMMENDED_K = 102

# ========== MARKET PRICE ==========
CORN_MARKET_PRICE = 17  # ₱ per kg (2026 Region 6 benchmark)

# ========== PLANTING SEASON MAPPINGS ==========
MONTH_NAMES = {
    1: 'January', 2: 'February', 3: 'March', 4: 'April',
    5: 'May', 6: 'June', 7: 'July', 8: 'August',
    9: 'September', 10: 'October', 11: 'November', 12: 'December'
}

WET_SEASON_MONTHS = [5, 6, 7, 8, 9, 10, 11]
DRY_SEASON_MONTHS = [12, 1, 2, 3, 4]
