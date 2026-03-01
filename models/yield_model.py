"""
Yield Model for Corn Input Optimization
========================================
Calculates corn yield based on agronomic factors.

Adapted from Comparative Analysis project.

Final_Yield = Base_Yield × Nutrient_Factor × Density_Factor × Soil_Factor ×
              Seasonal_Factor × Pest_Factor × Land_Prep_Factor
"""

import pandas as pd
from pathlib import Path
import math


class YieldModel:
    """Calculates corn yield based on agronomic factors."""

    RECOMMENDED_N = 134
    RECOMMENDED_P = 41
    RECOMMENDED_K = 102

    SOIL_TYPE_FACTORS = {
        "Sandy": 0.85,
        "Loamy": 1.0,
        "Clay": 0.90
    }

    OPTIMAL_DENSITY_BY_VARIETY = {
        "Glutinous": 55556,
        "Hybrid": 71429,
        "OPV": 53333
    }

    TOPOGRAPHY_FACTOR = {
        "Plain": 1.0,
        "Elevated": 0.90
    }

    WET_SEASON_MONTHS = [5, 6, 7, 8, 9, 10, 11]
    DRY_SEASON_MONTHS = [12, 1, 2, 3, 4]

    BASE_YIELD_POTENTIAL = {
        "Hybrid": 5000,
        "Glutinous": 5000,
        "OPV": 5000
    }

    def __init__(self,
                 farm_area_ha,
                 soil_type,
                 initial_n_kg_ha,
                 initial_p_kg_ha,
                 initial_k_kg_ha,
                 soil_ph=6.5,
                 topography="Plain",
                 planting_month=6,
                 seed_variety="Hybrid",
                 fertilizer_composition=None,
                 planting_density=55000,
                 data_dir=Path("data"),
                 irrigation_available=False):

        self.farm_area_ha = farm_area_ha
        self.soil_type = soil_type
        self.initial_n_kg_ha = initial_n_kg_ha
        self.initial_p_kg_ha = initial_p_kg_ha
        self.initial_k_kg_ha = initial_k_kg_ha
        self.soil_ph = soil_ph
        self.topography = topography
        self.planting_month = planting_month
        self.seed_variety = seed_variety
        self.fertilizer_composition = fertilizer_composition or {}
        self.planting_density = planting_density
        self.data_dir = Path(data_dir)
        self.irrigation_available = irrigation_available

        fertilizer_data = pd.read_csv(self.data_dir / "region_6_fertilizers.csv")
        self.fertilizers = fertilizer_data.set_index("id").to_dict(orient="index")

        seed_data = pd.read_csv(self.data_dir / "seed_varieties.csv")
        self.seeds = seed_data.set_index("id").to_dict(orient="index")

    def get_synergistic_nutrient_requirements(self):
        """Calculate dynamic nutrient requirements based on planting density."""
        optimal_density = self.OPTIMAL_DENSITY_BY_VARIETY[self.seed_variety]
        synergy_ratio = self.planting_density / optimal_density
        return (
            self.RECOMMENDED_N * synergy_ratio,
            self.RECOMMENDED_P * synergy_ratio,
            self.RECOMMENDED_K * synergy_ratio
        )

    def _get_nutrient_factor_from_percentage(self, percentage):
        """Convert nutrient percentage to a factor using Asymmetric Hybrid Curve."""
        if percentage <= 0:
            return 0.0
        elif percentage < 85:
            scaled = percentage / 85
            return scaled ** 0.5 * 0.5
        elif percentage < 100:
            return (percentage / 100) ** 0.5
        elif percentage <= 115:
            return max(0.0, 1.0 - (percentage - 100) / 15)
        else:
            overage = percentage - 115
            penalty_factor = 1.0 - (overage * 0.5)
            return max(-1.0, penalty_factor)

    def calculate_nutrient_factor(self):
        """Calculate how well applied fertilizers meet corn's NPK needs."""
        n_required, p_required, k_required = self.get_synergistic_nutrient_requirements()

        if n_required == 0 or p_required == 0 or k_required == 0:
            return 0.5

        nitrogen_per_ha = 0
        phosphorus_per_ha = 0
        potassium_per_ha = 0

        for fertilizer_id, sacks_per_ha in self.fertilizer_composition.items():
            fert = self.fertilizers.get(fertilizer_id)
            if fert is None:
                continue
            nitrogen_per_ha += sacks_per_ha * 50 * (fert.get("nitrogen", 0) / 100)
            phosphorus_per_ha += sacks_per_ha * 50 * (fert.get("phosphorus", 0) / 100)
            potassium_per_ha += sacks_per_ha * 50 * (fert.get("potassium", 0) / 100)

        total_n = self.initial_n_kg_ha + nitrogen_per_ha
        total_p = self.initial_p_kg_ha + phosphorus_per_ha
        total_k = self.initial_k_kg_ha + potassium_per_ha

        n_pct = (total_n / n_required) * 100
        p_pct = (total_p / p_required) * 100
        k_pct = (total_k / k_required) * 100

        factor_n = self._get_nutrient_factor_from_percentage(n_pct)
        factor_p = self._get_nutrient_factor_from_percentage(p_pct)
        factor_k = self._get_nutrient_factor_from_percentage(k_pct)

        return factor_n * factor_p * factor_k

    def calculate_density_factor(self):
        """Calculate how plant density affects corn yield (Gaussian)."""
        optimal_density = self.OPTIMAL_DENSITY_BY_VARIETY[self.seed_variety]
        deviation = (self.planting_density - optimal_density) / optimal_density
        sigma = 0.15
        density_factor = 1.2 * math.exp(-(deviation ** 2) / (2 * sigma ** 2))
        return max(0.3, min(density_factor, 1.2))

    def _get_ph_multiplier(self, ph):
        """Convert soil pH to a multiplier."""
        if 6.0 <= ph <= 7.0:
            return 1.0
        distance = abs(ph - 6.0) if ph < 6.0 else abs(ph - 7.0)
        return max(0.50, 1.0 - distance * 0.15)

    def calculate_soil_factor(self):
        """Calculate total soil quality factor."""
        soil_type_factor = self.SOIL_TYPE_FACTORS[self.soil_type]
        ph_multiplier = self._get_ph_multiplier(self.soil_ph)
        return max(0.68, min(soil_type_factor * ph_multiplier, 1.0))

    def calculate_seasonal_factor(self):
        """Calculate moisture availability factor."""
        if self.planting_month in self.WET_SEASON_MONTHS:
            return 1.0
        elif self.irrigation_available:
            return 0.95
        else:
            return 0.90

    def calculate_pest_factor(self):
        """Calculate pest pressure factor."""
        return 0.90 if self.planting_month in self.WET_SEASON_MONTHS else 0.95

    def calculate_land_prep_factor(self):
        """Calculate land preparation factor based on topography."""
        return self.TOPOGRAPHY_FACTOR[self.topography]

    def calculate_yield(self):
        """Calculate total corn yield by combining all agronomic factors."""
        NF = self.calculate_nutrient_factor()
        DF = self.calculate_density_factor()
        SF_s = self.calculate_soil_factor()
        SF_p = self.calculate_pest_factor()
        SF_l = self.calculate_seasonal_factor()
        PF = self.calculate_land_prep_factor()
        base = self.BASE_YIELD_POTENTIAL[self.seed_variety]
        return base * NF * DF * SF_s * SF_p * SF_l * PF
