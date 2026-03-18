"""
Cost Model for Corn Input Optimization - Website Edition
========================================================
Calculates total farming input costs for corn production.

INDEPENDENT IMPLEMENTATION:
- Does NOT import from Comparative-Analysis
- All logic and validation are self-contained in Website

Cost Breakdown:
    Total_Cost = Seed_Cost + Fertilizer_Cost + Operational_Costs + Herbicide_Cost

Input Costs Components:
1. Seed Cost: Based on planting density and variety
2. Fertilizer Cost: NPK composition from chromosome optimization
3. Operational Costs: Land prep, planting, application labor, harvesting
4. Herbicide Cost: Herbicide application (Hybrid variety only)
"""

import pandas as pd
from pathlib import Path


class CostModel:
    """Calculate total farming costs based on inputs and conditions."""

    # Operational costs per hectare for Plain topography
    # Includes: land prep, planting, fertilizer applications, harvesting, and variety-specific costs
    OPERATIONAL_COSTS_PLAIN = {
        "shared": {
            "land_prep": 6000,
            "planting": 5000,
            "fert_app_1": 3000,
            "fert_app_2": 3000,
            "harvesting": 10000,
        },
        "Hybrid": {"herbicide_labor": 2000},
        "Glutinous": {"weeding_labor": 2000},
        "OPV": {"weeding_labor": 2000}
    }

    OPERATIONAL_COSTS_ELEVATED = {
        "shared": {
            "planting": 5000,
            "fert_app_labor": 6000,
        },
        "Hybrid": {
            "herbicide_labor_1": 2000,
            "herbicide_labor_2": 2000,
        },
        "Glutinous": {"weeding_labor": 2000},
        "OPV": {"weeding_labor": 2000}
    }

    HERBICIDE_COST_PER_GALLON = 1500
    HERBICIDE_GALLONS_REQUIRED = {
        "Plain": 2,
        "Elevated": 4
    }

    def __init__(self, farm_area_ha, seed_variety, planting_density,
                 fertilizer_composition, topography, data_dir=Path("data")):
        """
        Initialize cost model with farm parameters.

        Parameters:
            farm_area_ha (float): Farm size in hectares
            seed_variety (str): Seed type ("Hybrid", "Glutinous", "OPV")
            planting_density (int): Plants per hectare
            fertilizer_composition (dict): Fertilizer IDs and sack quantities
            topography (str): Terrain type ("Plain" or "Elevated")
            data_dir (Path): Directory containing CSV data files
        """
        self.farm_area_ha = farm_area_ha
        self.planting_density = planting_density
        self.fertilizer_composition = fertilizer_composition
        self.topography = topography
        self.data_dir = Path(data_dir)

        # Load fertilizer and seed data
        fertilizer_data = pd.read_csv(self.data_dir / "region_6_fertilizers.csv")
        self.fertilizers = fertilizer_data.set_index("id").to_dict(orient="index")

        seed_data = pd.read_csv(self.data_dir / "seed_varieties.csv")
        self.seeds = seed_data.set_index("id").to_dict(orient="index")
        self.variety_name_to_id = {row["name"]: row["id"] for _, row in seed_data.iterrows()}

        if topography not in ["Plain", "Elevated"]:
            raise ValueError(f"Invalid topography: {topography}. Must be 'Plain' or 'Elevated'")

        if farm_area_ha < 1.0:
            raise ValueError(f"Farm area must be at least 1 hectare, got {farm_area_ha}")

        if seed_variety in self.variety_name_to_id:
            self.seed_variety = self.variety_name_to_id[seed_variety]
        elif seed_variety in self.seeds:
            self.seed_variety = seed_variety
        else:
            available_names = list(self.variety_name_to_id.keys())
            raise ValueError(f"Unknown seed variety: {seed_variety}. Available: {available_names}")

    def calculate_seed_cost(self):
        """
        Calculate total seed cost based on optimized planting density.

        Formula:
            Total_seeds = planting_density × seeds_per_hill × farm_area_ha
            Seeds_weight_kg = Total_seeds / seeds_per_kg
            Seed_cost = Seeds_weight_kg × price_per_kg

        Returns:
            float: Total seed cost in Philippine Pesos (₱)
        """
        seed = self.seeds[self.seed_variety]
        total_seeds = self.planting_density * seed["seeds_per_hill"] * self.farm_area_ha
        seeds_weight_kg = total_seeds / seed["seeds_per_kg"]
        return seeds_weight_kg * seed["price_per_kg"]

    def calculate_fertilizer_cost(self):
        """
        Calculate total fertilizer cost based on fertilizer composition.

        The fertilizer_composition dictionary contains:
        - Keys: Fertilizer IDs (e.g., "F01", "F06")
        - Values: Number of sacks PER HECTARE (not total farm)

        Formula:
            Total_Sacks = Sacks_per_ha × Farm_Area_ha
            Fertilizer_Cost = Σ (Price_per_sack × Total_Sacks) for all fertilizers

        Returns:
            float: Total fertilizer cost in Philippine Pesos (₱)
        """
        total = 0
        for fert_id, sacks_per_ha in self.fertilizer_composition.items():
            fert = self.fertilizers.get(fert_id)
            if fert is None:
                continue
            total += sacks_per_ha * self.farm_area_ha * fert.get("price", 0)
        return total

    def calculate_operational_costs(self):
        """
        Calculate total operational costs including land prep and agricultural labor.

        Costs vary by topography and seed variety:

        PLAIN HYBRID (₱32,000/ha):
            Land prep: ₱6,000
            Planting: ₱5,000
            1st fertilizer application: ₱3,000
            2nd fertilizer application: ₱3,000
            Herbicide labor: ₱2,000
            Harvesting: ₱10,000
            Total: ₱32,000 + herbicide material cost

        ELEVATED HYBRID (₱15,000/ha labor):
            Planting: ₱5,000
            Fertilizer applications labor: ₱6,000
            1st herbicide application labor: ₱2,000
            2nd herbicide application labor: ₱2,000
            Total: ₱15,000 + herbicide material cost

        Returns:
            float: Total operational cost in Philippine Pesos (₱)
        """
        variety_name = self.seeds[self.seed_variety]["name"]
        cost_dict = self.OPERATIONAL_COSTS_PLAIN if self.topography == "Plain" else self.OPERATIONAL_COSTS_ELEVATED
        total = sum(cost_dict["shared"].values())
        if variety_name in cost_dict:
            total += sum(cost_dict[variety_name].values())
        return total * self.farm_area_ha

    def calculate_herbicide_cost(self):
        """
        Calculate herbicide cost (Hybrid variety only).

        Glyphosate-based herbicide application for weed control in Hybrid varieties.
        Glutinous and OPV varieties use hand weeding (labor cost already in operational).

        Returns:
            float: Total herbicide cost in Philippine Pesos (₱), or 0.0 for non-Hybrid
        """
        variety_name = self.seeds[self.seed_variety]["name"]
        if variety_name != "Hybrid":
            return 0.0
        gallons = self.HERBICIDE_GALLONS_REQUIRED[self.topography]
        return gallons * self.HERBICIDE_COST_PER_GALLON * self.farm_area_ha

    def calculate_total_cost(self):
        """
        Calculate total farming cost (sum of all cost components).

        Returns:
            float: Total farming cost in Philippine Pesos (₱)
        """
        return (self.calculate_seed_cost() +
                self.calculate_fertilizer_cost() +
                self.calculate_operational_costs() +
                self.calculate_herbicide_cost())
