"""
Cost Model for Corn Input Optimization
=======================================
Calculates total farming cost.

Total_Cost = Seed_Cost + Fertilizer_Cost + Operational_Costs + Herbicide_Cost

Adapted from Comparative Analysis project.
"""

import pandas as pd
from pathlib import Path


class CostModel:
    """Calculate farming costs based on inputs and conditions."""

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
        self.farm_area_ha = farm_area_ha
        self.planting_density = planting_density
        self.fertilizer_composition = fertilizer_composition
        self.topography = topography
        self.data_dir = Path(data_dir)

        fertilizer_data = pd.read_csv(self.data_dir / "region_6_fertilizers.csv")
        self.fertilizers = fertilizer_data.set_index("id").to_dict(orient="index")

        seed_data = pd.read_csv(self.data_dir / "seed_varieties.csv")
        self.seeds = seed_data.set_index("id").to_dict(orient="index")
        self.variety_name_to_id = {row["name"]: row["id"] for _, row in seed_data.iterrows()}

        # Resolve variety
        if seed_variety in self.variety_name_to_id:
            self.seed_variety = self.variety_name_to_id[seed_variety]
        elif seed_variety in self.seeds:
            self.seed_variety = seed_variety
        else:
            raise ValueError(f"Unknown seed variety: {seed_variety}")

    def calculate_seed_cost(self):
        """Calculate total seed cost."""
        seed = self.seeds[self.seed_variety]
        total_seeds = self.planting_density * seed["seeds_per_hill"] * self.farm_area_ha
        seeds_weight_kg = total_seeds / seed["seeds_per_kg"]
        return seeds_weight_kg * seed["price_per_kg"]

    def calculate_fertilizer_cost(self):
        """Calculate total fertilizer cost."""
        total = 0
        for fert_id, sacks_per_ha in self.fertilizer_composition.items():
            fert = self.fertilizers.get(fert_id)
            if fert is None:
                continue
            total += sacks_per_ha * self.farm_area_ha * fert.get("price", 0)
        return total

    def calculate_operational_costs(self):
        """Calculate operational costs (labor, land prep, etc.)."""
        variety_name = self.seeds[self.seed_variety]["name"]
        cost_dict = self.OPERATIONAL_COSTS_PLAIN if self.topography == "Plain" else self.OPERATIONAL_COSTS_ELEVATED
        total = sum(cost_dict["shared"].values())
        if variety_name in cost_dict:
            total += sum(cost_dict[variety_name].values())
        return total * self.farm_area_ha

    def calculate_herbicide_cost(self):
        """Calculate herbicide cost (Hybrid only)."""
        variety_name = self.seeds[self.seed_variety]["name"]
        if variety_name != "Hybrid":
            return 0.0
        gallons = self.HERBICIDE_GALLONS_REQUIRED[self.topography]
        return gallons * self.HERBICIDE_COST_PER_GALLON * self.farm_area_ha

    def calculate_total_cost(self):
        """Calculate total farming cost."""
        return (self.calculate_seed_cost() +
                self.calculate_fertilizer_cost() +
                self.calculate_operational_costs() +
                self.calculate_herbicide_cost())
