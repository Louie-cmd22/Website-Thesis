"""
Algorithm Parameters Configuration - Website Edition
====================================================
Centralized configuration for Memetic Algorithm (MA) web prototype.

INDEPENDENT IMPLEMENTATION:
- Website does NOT import from Comparative-Analysis
- All parameters and logic are self-contained
- Follows Comparative-Analysis methodology but as standalone code

ALGORITHM CHOICE: Memetic Algorithm (MA)
- Combines GA (population-based search) with hill climbing (local refinement)
- 50 generations + local search = 5,000 + 5,000 = 10,000 total function evaluations
- Better for real-world optimization with continuous refinement
- Ideal for web prototype: fewer generations, faster user feedback
"""

MAX_EVALUATIONS = 10000

ALGORITHM_PARAMS = {
    'population_size': 100,
    'max_generations': 50,
    'crossover_rate': 0.9,
    'mutation_rate': 0.05,
    'elitism_count': 2,
    'tournament_size': 3,
    'early_stopping_generations': None,
    'random_seed': None,
    'selection_method': 'tournament',
    'crossover_method': 'uniform',
    'mutation_method': 'gaussian',
    'boundary_handling': 'clipping',
    'mutation_step_size': 0.05
}

LOCAL_SEARCH_PARAMS = {
    'local_search_method': 'hill_climbing',
    'local_search_probability': 0.1,
    'local_search_selection': 'best',
    'hill_climbing_max_iterations': 10,
    'hill_climbing_step_size': 0.05,
    'improvement_threshold': 0,
    'max_iterations_safety_limit': 100,
    'no_improvement_threshold': 5
}

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

MIN_NPK_ADEQUACY_PERCENTAGE = 0.85
MAX_NPK_PERCENTAGE = 1.15

RECOMMENDED_N = 134
RECOMMENDED_P = 41
RECOMMENDED_K = 102

OPTIMAL_DENSITY_BY_VARIETY = {
    'Glutinous': 55556,
    'Hybrid': 71429,
    'OPV': 53333
}

BASE_YIELD_POTENTIAL = {
    'Hybrid': 5000,
    'Glutinous': 5000,
    'OPV': 5000
}

CORN_MARKET_PRICE = 17

SOIL_TYPE_FACTORS = {
    "Sandy": 0.85,
    "Loamy": 1.0,
    "Clay": 0.90
}

TOPOGRAPHY_FACTOR = {
    "Plain": 1.0,
    "Elevated": 0.90
}

WET_SEASON_MONTHS = [5, 6, 7, 8, 9, 10, 11]
DRY_SEASON_MONTHS = [12, 1, 2, 3, 4]

MONTH_NAMES = {
    1: 'January', 2: 'February', 3: 'March', 4: 'April',
    5: 'May', 6: 'June', 7: 'July', 8: 'August',
    9: 'September', 10: 'October', 11: 'November', 12: 'December'
}
