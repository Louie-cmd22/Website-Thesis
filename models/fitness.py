"""
Fitness Function for Corn Input Optimization - Website Edition
==============================================================
Combines YieldModel and CostModel to evaluate farming solutions.

INDEPENDENT IMPLEMENTATION:
- Does NOT import from Comparative-Analysis
- All logic and configuration are self-contained in Website
- Imports only from local config.params (MA-specific settings)

Fitness Evaluation:
    Fitness = Gross Margin = Revenue - Total Cost

Where:
    Revenue = Yield (kg/ha) × Farm Area (ha) × Market Price (₱/kg)
    Total Cost = Seed + Fertilizer + Operations + Herbicide costs

This is a pure economic optimization problem: maximize profit while
satisfying agronomic constraints (NPK adequacy 85-115%).
"""

import pandas as pd
from pathlib import Path
from models.yield_model import YieldModel
from models.cost_model import CostModel
from config.params import (
    MIN_NPK_ADEQUACY_PERCENTAGE,
    MAX_NPK_PERCENTAGE,
    CORN_MARKET_PRICE,
    RECOMMENDED_N,
    RECOMMENDED_P,
    RECOMMENDED_K,
    OPTIMAL_DENSITY_BY_VARIETY
)


class Fitness:
    """Evaluates farming solutions for MA optimization."""

    RECOMMENDED_N = RECOMMENDED_N
    RECOMMENDED_P = RECOMMENDED_P
    RECOMMENDED_K = RECOMMENDED_K

    OPTIMAL_DENSITY_BY_VARIETY = OPTIMAL_DENSITY_BY_VARIETY

    def __init__(
        self,
        farm_area_ha,
        seed_variety,
        planting_density,
        fertilizer_composition,
        topography,
        soil_type,
        soil_ph,
        initial_n_kg_ha,
        initial_p_kg_ha,
        initial_k_kg_ha,
        planting_month,
        irrigation_available,
        data_dir='data'
    ):
        """
        Initialize Fitness evaluator with farming parameters.

        Parameters:
            farm_area_ha (float): Farm size in hectares
            seed_variety (str): Seed type ("Hybrid", "Glutinous", "OPV")
            planting_density (int): Plants per hectare
            fertilizer_composition (dict): Fertilizer IDs and sack quantities
            topography (str): Terrain type ("Plain" or "Elevated")
            soil_type (str): Soil classification ("Sandy", "Loamy", "Clay")
            soil_ph (float): Soil pH level (optimal: 6.0-7.0)
            initial_n_kg_ha (float): Initial nitrogen in soil (kg/ha)
            initial_p_kg_ha (float): Initial phosphorus in soil (kg/ha)
            initial_k_kg_ha (float): Initial potassium in soil (kg/ha)
            planting_month (int): Month of planting (1-12)
            irrigation_available (bool): Whether irrigation is available
            data_dir (str): Directory containing CSV data files
        """
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
            farm_area_ha=farm_area_ha,
            seed_variety=seed_variety,
            planting_density=planting_density,
            fertilizer_composition=fertilizer_composition,
            topography=topography,
            soil_type=soil_type,
            soil_ph=soil_ph,
            initial_n_kg_ha=initial_n_kg_ha,
            initial_p_kg_ha=initial_p_kg_ha,
            initial_k_kg_ha=initial_k_kg_ha,
            planting_month=planting_month,
            irrigation_available=irrigation_available,
            data_dir=data_dir
        )

        self.cost_model = CostModel(
            farm_area_ha=farm_area_ha,
            seed_variety=seed_variety,
            planting_density=planting_density,
            fertilizer_composition=fertilizer_composition,
            topography=topography,
            data_dir=data_dir
        )

    def calculate_fitness(self):
        """
        Calculate fitness = Revenue - Total Cost (Gross Margin).

        Process:
            1. Calculate total corn yield (kg) from yield model
            2. Calculate revenue from yield and market price
            3. Calculate total costs from cost model
            4. Return gross margin (profit)

        Returns:
            float: Gross margin (net profit) in Philippine Pesos (₱)
                   Positive value = profitable solution
                   Negative value = loss-making solution
        """
        total_yield_kg = self.yield_model.calculate_yield()
        revenue = total_yield_kg * CORN_MARKET_PRICE
        total_cost = self.cost_model.calculate_total_cost()
        return revenue - total_cost
