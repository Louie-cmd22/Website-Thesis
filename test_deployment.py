#!/usr/bin/env python3
"""Quick deployment readiness check for Website"""
import sys
sys.path.insert(0, '.')

print("=" * 60)
print("WEBSITE DEPLOYMENT READINESS CHECK")
print("=" * 60)

# Test imports
print("\n1. Testing imports...")
errors = []

try:
    from models.yield_model import YieldModel
    print("   ✓ YieldModel imports correctly")
except Exception as e:
    print(f"   ✗ YieldModel import failed: {e}")
    errors.append(f"YieldModel: {e}")

try:
    from models.cost_model import CostModel
    print("   ✓ CostModel imports correctly")
except Exception as e:
    print(f"   ✗ CostModel import failed: {e}")
    errors.append(f"CostModel: {e}")

try:
    from models.fitness import FitnessModel
    print("   ✓ FitnessModel imports correctly")
except Exception as e:
    print(f"   ✗ FitnessModel import failed: {e}")
    errors.append(f"FitnessModel: {e}")

try:
    from config.params import ALGORITHM_PARAMS, CHROMOSOME_CONSTRAINTS
    print("   ✓ Config params import correctly")
except Exception as e:
    print(f"   ✗ Config params import failed: {e}")
    errors.append(f"Config params: {e}")

try:
    from algorithm.optimizer import Optimizer
    print("   ✓ Optimizer imports correctly")
except Exception as e:
    print(f"   ✗ Optimizer import failed: {e}")
    errors.append(f"Optimizer: {e}")

# Test density factor (5 ton rule)
print("\n2. Testing yield model constraints (5000 kg max)...")
try:
    from models.yield_model import YieldModel
    ym = YieldModel(
        farm_area_ha=1.0,
        soil_type='Loamy',
        initial_n_kg_ha=100,
        initial_p_kg_ha=30,
        initial_k_kg_ha=70,
        seed_variety='Hybrid',
        planting_density=71429,  # optimal
        data_dir='data'
    )
    
    # DF should be 1.0 at optimal
    df = ym.calculate_density_factor()
    print(f"   Density Factor at optimal density: {df:.4f}")
    if df > 1.0:
        print(f"   ✗ CRITICAL: Density factor exceeds 1.0 ({df:.4f})")
        errors.append(f"Density factor > 1.0: {df}")
    else:
        print(f"   ✓ Density factor respects 1.0 maximum")
    
    # Test that max yield respects 5000 kg constraint
    # Calculate with all factors optimal
    yield_kg = ym.calculate_yield()
    print(f"   Yield at optimal conditions: {yield_kg:.1f} kg/ha")
    if yield_kg > 5000.5:  # Allow small floating point margin
        print(f"   ✗ CRITICAL: Yield exceeds 5000 kg constraint ({yield_kg:.1f})")
        errors.append(f"Yield exceeds 5000 kg: {yield_kg}")
    else:
        print(f"   ✓ Yield respects 5000 kg maximum")
        
except Exception as e:
    print(f"   ✗ Yield model test failed: {e}")
    errors.append(f"Yield model test: {e}")

# Test seed calculation (seed bag rule)
print("\n3. Testing seed variety data...")
try:
    import pandas as pd
    seed_data = pd.read_csv('data/seed_varieties.csv')
    
    required_cols = ['id', 'name', 'seeds_per_hill', 'seeds_per_kg', 'price_per_kg']
    missing = [col for col in required_cols if col not in seed_data.columns]
    
    if missing:
        print(f"   ✗ Missing columns in seed_varieties.csv: {missing}")
        errors.append(f"Seed data missing columns: {missing}")
    else:
        print(f"   ✓ seed_varieties.csv has all required columns")
        print(f"   ✓ Varieties present: {', '.join(seed_data['name'].tolist())}")
        
except Exception as e:
    print(f"   ✗ Seed data test failed: {e}")
    errors.append(f"Seed data: {e}")

# Test fertilizer data
print("\n4. Testing fertilizer data...")
try:
    import pandas as pd
    fert_data = pd.read_csv('data/region_6_fertilizers.csv')
    
    required_cols = ['id', 'name', 'price']
    missing = [col for col in required_cols if col not in fert_data.columns]
    
    if missing:
        print(f"   ✗ Missing columns in region_6_fertilizers.csv: {missing}")
        errors.append(f"Fertilizer data missing columns: {missing}")
    else:
        print(f"   ✓ region_6_fertilizers.csv has all required columns")
        print(f"   ✓ Fertilizers present: {', '.join(fert_data['id'].tolist())}")
        
except Exception as e:
    print(f"   ✗ Fertilizer data test failed: {e}")
    errors.append(f"Fertilizer data: {e}")

# Final summary
print("\n" + "=" * 60)
if errors:
    print(f"DEPLOYMENT STATUS: ✗ NOT READY ({len(errors)} issues)")
    print("\nIssues to fix:")
    for i, err in enumerate(errors, 1):
        print(f"  {i}. {err}")
else:
    print("DEPLOYMENT STATUS: ✓ READY FOR DEPLOYMENT")
    print("\nAll checks passed!")
    print("  • Density factor correctly limits max yield to 5000 kg/ha")
    print("  • Seed variety data complete and accessible")
    print("  • Fertilizer data complete and accessible")
    print("  • All required imports working")

print("=" * 60)
