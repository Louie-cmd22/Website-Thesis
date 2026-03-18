"""
Chromosome Representation and Generation
==========================================
Handles creation and validation of farming solution chromosomes.

Adapted from Comparative Analysis project.
"""

import random
import copy
import pandas as pd
from config.params import CHROMOSOME_CONSTRAINTS


def validate_chromosome(chromosome, seed_variety, fertilizer_data, farm_area_ha, constraints):
    """Validate that a chromosome is feasible."""
    errors = []

    if not isinstance(chromosome, dict):
        return (False, ["Chromosome must be a dictionary"])
    if 'fertilizer_composition' not in chromosome:
        errors.append("Missing 'fertilizer_composition'")
    if 'planting_density' not in chromosome:
        errors.append("Missing 'planting_density'")
    if errors:
        return (False, errors)

    fert_comp = chromosome['fertilizer_composition']
    if len(fert_comp) == 0:
        errors.append("fertilizer_composition cannot be empty")

    valid_ids = set(fertilizer_data["id"])
    for fert_id in fert_comp.keys():
        if fert_id not in valid_ids:
            errors.append(f"Invalid fertilizer ID: {fert_id}")

    total_sacks = sum(fert_comp.values())
    max_total = constraints['fertilizer']['max_total_sacks_per_ha'] * farm_area_ha
    if total_sacks > max_total:
        errors.append(f"Total sacks {total_sacks:.1f} exceeds max {max_total}")
    elif total_sacks == 0:
        errors.append("Total sacks cannot be zero")

    density = chromosome['planting_density']
    dc = constraints['planting_density'][seed_variety]
    if not (dc['min'] <= density <= dc['max']):
        errors.append(f"Density {density} out of range ({dc['min']}-{dc['max']})")

    for fert_id, sacks in fert_comp.items():
        if sacks <= 0:
            errors.append(f"Fertilizer {fert_id} has non-positive amount")

        if 'max_fertilizer_types' in constraints['fertilizer']:
            max_types = constraints['fertilizer']['max_fertilizer_types']
            num_types = len(fert_comp)
            if num_types > max_types:
                errors.append(f"Number of fertilizer types ({num_types}) exceeds maximum allowed ({max_types})")

    return (len(errors) == 0, errors)


def generate_random_chromosome(fertilizer_data, seed_variety, constraints, farm_area_ha):
    """Generate a valid random chromosome."""
    chromosome = {'fertilizer_composition': {}, 'planting_density': 0}

    valid_ids = list(fertilizer_data["id"])
    max_types = min(len(valid_ids), constraints['fertilizer'].get('max_fertilizer_types', 10))
    k = random.randint(1, max_types)
    selected = random.sample(valid_ids, k)

    max_total = constraints['fertilizer']['max_total_sacks_per_ha'] * farm_area_ha
    for fert_id in selected:
        avg = max_total / k
        chromosome['fertilizer_composition'][fert_id] = random.uniform(0.1, avg * 2)

    total = sum(chromosome['fertilizer_composition'].values())
    if total > max_total:
        ratio = max_total / total
        for fert_id in chromosome['fertilizer_composition']:
            chromosome['fertilizer_composition'][fert_id] = max(0.1,
                chromosome['fertilizer_composition'][fert_id] * ratio)

    dc = constraints['planting_density'][seed_variety]
    chromosome['planting_density'] = random.randint(dc['min'], dc['max'])

    is_valid, _ = validate_chromosome(chromosome, seed_variety, fertilizer_data, farm_area_ha, constraints)
    return chromosome, is_valid


def generate_smart_chromosome(fertilizer_data, seed_variety, farm_params, constraints, farm_area_ha):
    """
    Generate a chromosome using grid search to find an NPK-feasible solution.

    Searches combinations of Complete (F05), Urea (F01), MOP (F06), and DAP (F07)
    against the farm's actual initial soil NPK to find a combination that satisfies
    the [85%–115%] NPK adequacy constraint before optimization begins.

    Falls back to random generation if grid search fails.
    """
    from config.params import MIN_NPK_ADEQUACY_PERCENTAGE, MAX_NPK_PERCENTAGE

    TARGET_N = 134
    TARGET_P = 41
    TARGET_K = 102

    MIN_N = TARGET_N * MIN_NPK_ADEQUACY_PERCENTAGE
    MAX_N = TARGET_N * MAX_NPK_PERCENTAGE
    MIN_P = TARGET_P * MIN_NPK_ADEQUACY_PERCENTAGE
    MAX_P = TARGET_P * MAX_NPK_PERCENTAGE
    MIN_K = TARGET_K * MIN_NPK_ADEQUACY_PERCENTAGE
    MAX_K = TARGET_K * MAX_NPK_PERCENTAGE

    initial_n = farm_params['initial_n_kg_ha']
    initial_p = farm_params['initial_p_kg_ha']
    initial_k = farm_params['initial_k_kg_ha']

    SACK_SIZE_KG = 50

    fert_dict = {}
    for _, row in fertilizer_data.iterrows():
        fert_dict[row['id']] = {
            'n_percent': row['nitrogen'],
            'p_percent': row['phosphorus'],
            'k_percent': row['potassium']
        }

    candidates = []

    for complete_sacks in [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0]:
        for urea_sacks in [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]:
            for k_sacks in [0.0, 0.3, 0.6, 1.0, 1.5]:
                candidate = {'F05': complete_sacks, 'F01': urea_sacks, 'F06': k_sacks}
                candidate = {k: v for k, v in candidate.items() if v > 0}
                candidates.append(candidate)

    for dap_sacks in [0.2, 0.4, 0.6, 0.8, 1.0, 1.2]:
        for urea_sacks in [1.0, 2.0, 3.0, 4.0]:
            for k_sacks in [0.3, 0.6, 1.0]:
                candidate = {'F07': dap_sacks, 'F01': urea_sacks, 'F06': k_sacks}
                candidate = {k: v for k, v in candidate.items() if v > 0}
                candidates.append(candidate)

    best_candidate = None
    best_score = float('inf')
    first_feasible = None

    for fert_comp in candidates:
        total_n = initial_n
        total_p = initial_p
        total_k = initial_k

        for fert_id, sacks in fert_comp.items():
            if fert_id not in fert_dict:
                continue
            total_n += sacks * SACK_SIZE_KG * (fert_dict[fert_id]['n_percent'] / 100)
            total_p += sacks * SACK_SIZE_KG * (fert_dict[fert_id]['p_percent'] / 100)
            total_k += sacks * SACK_SIZE_KG * (fert_dict[fert_id]['k_percent'] / 100)

        n_valid = MIN_N <= total_n <= MAX_N
        p_valid = MIN_P <= total_p <= MAX_P
        k_valid = MIN_K <= total_k <= MAX_K

        violations = (0 if n_valid else 1000) + (0 if p_valid else 1000) + (0 if k_valid else 1000)
        distance = abs(total_n - TARGET_N) + abs(total_p - TARGET_P) + abs(total_k - TARGET_K)
        score = violations + distance

        if score < best_score:
            best_score = score
            best_candidate = fert_comp

        if n_valid and p_valid and k_valid and first_feasible is None:
            first_feasible = fert_comp
            break

    selected_fert = first_feasible if first_feasible else best_candidate

    if selected_fert is None:
        return generate_random_chromosome(fertilizer_data, seed_variety, constraints, farm_area_ha)

    chromosome = {'fertilizer_composition': selected_fert, 'planting_density': 0}

    total_sacks = sum(chromosome['fertilizer_composition'].values())
    max_total_sacks = constraints['fertilizer']['max_total_sacks_per_ha'] * farm_area_ha

    if total_sacks <= max_total_sacks:
        dc = constraints['planting_density'][seed_variety]
        chromosome['planting_density'] = random.randint(dc['min'], dc['max'])
        validated = validate_chromosome(chromosome, seed_variety, fertilizer_data, farm_area_ha, constraints)
        if validated[0]:
            return (chromosome, True)

    return generate_random_chromosome(fertilizer_data, seed_variety, constraints, farm_area_ha)
