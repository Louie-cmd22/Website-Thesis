"""Quick test to verify all modules work."""
import sys
sys.path.insert(0, '.')

from config.params import ALGORITHM_PARAMS, CHROMOSOME_CONSTRAINTS
print('Config OK:', ALGORITHM_PARAMS['population_size'])

from models.yield_model import YieldModel
from models.cost_model import CostModel
from models.fitness import Fitness
print('Models OK')

from algorithm.chromosome import generate_random_chromosome, generate_smart_chromosome
from algorithm.optimizer import Optimizer
print('Algorithm OK')

farm_params = {
    'farm_area_ha': 1.0,
    'topography': 'Plain',
    'soil_type': 'Loamy',
    'soil_ph': 6.5,
    'initial_n_kg_ha': 80.0,
    'initial_p_kg_ha': 25.0,
    'initial_k_kg_ha': 60.0,
    'planting_month': 6,
    'irrigation_available': False,
}

opt = Optimizer(farm_params, 'Hybrid', random_seed=42)
best = opt.run()
print('Optimizer OK')
print(f'Best density: {best["planting_density"]:.0f}')
print(f'Best ferts: {best["fertilizer_composition"]}')

ym = YieldModel(
    farm_area_ha=1.0, seed_variety='Hybrid',
    planting_density=best['planting_density'],
    fertilizer_composition=best['fertilizer_composition'],
    topography='Plain', soil_type='Loamy', soil_ph=6.5,
    initial_n_kg_ha=80.0, initial_p_kg_ha=25.0, initial_k_kg_ha=60.0,
    planting_month=6, irrigation_available=False, data_dir='data'
)
cm = CostModel(
    farm_area_ha=1.0, seed_variety='Hybrid',
    planting_density=best['planting_density'],
    fertilizer_composition=best['fertilizer_composition'],
    topography='Plain', data_dir='data'
)

y = ym.calculate_yield()
c = cm.calculate_total_cost()
print(f'Yield: {y:.0f} kg')
print(f'Cost: {c:.0f} pesos')
print(f'Revenue: {y*17:.0f} pesos')
print(f'Profit: {y*17-c:.0f} pesos')
print('\nAll tests passed!')
