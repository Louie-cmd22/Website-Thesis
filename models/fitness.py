"""
Fitness Function for Corn Input Optimization
=============================================
Combines YieldModel and CostModel to evaluate farming solutions.

Fitness = Gross Margin = Revenue - Total Cost

Adapted from Comparative Analysis project.
"""

import pandas as pd
from pathlib import Path
from models.yield_model import YieldModel
from models.cost_model import CostModel
from config.params import MIN_NPK_ADEQUACY_PERCENTAGE, MAX_NPK_PERCENTAGE, CORN_MARKET_PRICE


class Fitness:
    """Evaluates farming solutions for optimization."""

    RECOMMENDED_N = 134
    RECOMMENDED_P = 41
    RECOMMENDED_K = 102

    OPTIMAL_DENSITY_BY_VARIETY = {
        "Glutinous": 55556,
        "Hybrid": 71429,
        "OPV": 53333
    }

    def __init__(self, farm_area_ha, seed_variety, planting_density,
                 fertilizer_composition, topography, soil_type, soil_ph,
                 initial_n_kg_ha, initial_p_kg_ha, initial_k_kg_ha,
                 planting_month, irrigation_available, data_dir='data'):

        self.planting_density = planting_density
        self.fertilizer_composition = fertilizer_composition
        self.farm_area_ha = farm_area_ha
        self.initial_n_kg_ha = initial_n_kg_ha
        self.initial_p_kg_ha = initial_p_kg_ha
        self.initial_k_kg_ha = initial_k_kg_ha
        self.seed_variety = seed_variety
        self.data_dir = Path(data_dir)

        fertilizer_data = pd.read_csv(self.data_dir / "region_6_fertilizers.csv")
        self.fertilizers = fertilizer_data.set_index("id").to_dict(orient="index")

        self.yield_model = YieldModel(
            farm_area_ha=farm_area_ha, seed_variety=seed_variety,
            planting_density=planting_density, fertilizer_composition=fertilizer_composition,
            topography=topography, soil_type=soil_type, soil_ph=soil_ph,
            initial_n_kg_ha=initial_n_kg_ha, initial_p_kg_ha=initial_p_kg_ha,
            initial_k_kg_ha=initial_k_kg_ha, planting_month=planting_month,
            irrigation_available=irrigation_available, data_dir=data_dir
        )

        self.cost_model = CostModel(
            farm_area_ha=farm_area_ha, seed_variety=seed_variety,
            planting_density=planting_density, fertilizer_composition=fertilizer_composition,
            topography=topography, data_dir=data_dir
        )

    def calculate_fitness(self):
        """Calculate fitness = Revenue - Total Cost."""
        total_yield_kg = self.yield_model.calculate_yield()
        revenue = total_yield_kg * CORN_MARKET_PRICE
        total_cost = self.cost_model.calculate_total_cost()
        return revenue - total_cost
