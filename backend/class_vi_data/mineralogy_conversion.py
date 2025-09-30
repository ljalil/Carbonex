"""
Mineralogy Analysis and Conversion Functions

This module provides functions for converting between different representations 
of mineral compositions:
- Weight fractions ↔ Number of moles
- Weight fractions ↔ Weight percentages
- Normalization and validation functions

Key Functions:
- wt_frac_to_moles(): Convert weight fractions to moles
- moles_to_wt_frac(): Convert moles to weight fractions
- wt_frac_to_wt_percent(): Convert fractions to percentages
- wt_percent_to_wt_frac(): Convert percentages to fractions
- normalize_weight_fractions(): Normalize fractions to sum to 1.0
- calculate_mineral_composition(): Comprehensive analysis function
"""

# Mineral molar masses (g/mol)
mineral_molar_masses = { 
    'Quartz': 60.083,
    'Albite': 262.14,
    'K-feldspar': 278.33,
    'Illite': 389.34,
    'Kaolinite': 258.16,  # Fixed typo from 'Koalinite'
    'Calcite': 100.0869, 
    'Dolomite': 184.40,
    'Siderite': 115.85,
    'Chlorite': 555.797,
    'Pyrite': 119.98
}

# Weight fractions for each mineral (must sum to 1.0)
mineral_weight_fractions = { 
    'Quartz': 0.5,
    'Albite': 0.2,
    'K-feldspar': 0.2,
    'Illite': 0.1,
    'Kaolinite': 0.0,
    'Calcite': 0.0, 
    'Dolomite': 0.0,
    'Siderite': 0.0,
    'Chlorite': 0.0,
    'Pyrite': 0.0
}

# Total sample weight in grams
TOTAL_SAMPLE_WEIGHT = 1000  # g (1 kg sample)

def wt_frac_to_moles(weight_fractions, molar_masses, total_weight=None):
    """
    Convert weight fractions to number of moles for each mineral.
    
    Args:
        weight_fractions (dict): Weight fraction of each mineral (must sum to 1.0)
        molar_masses (dict): Molar mass of each mineral (g/mol)
        total_weight (float, optional): Total weight of the sample (g). If None, uses TOTAL_SAMPLE_WEIGHT
    
    Returns:
        dict: Number of moles for each mineral
    """
    if total_weight is None:
        total_weight = TOTAL_SAMPLE_WEIGHT
    
    moles = {}
    for mineral, weight_frac in weight_fractions.items():
        if mineral in molar_masses and molar_masses[mineral] > 0:
            mineral_weight = weight_frac * total_weight
            moles[mineral] = mineral_weight / molar_masses[mineral]
        else:
            moles[mineral] = 0.0
    
    return moles

def moles_to_wt_frac(moles, molar_masses):
    """
    Convert number of moles to weight fractions for each mineral.
    
    Args:
        moles (dict): Number of moles for each mineral
        molar_masses (dict): Molar mass of each mineral (g/mol)
    
    Returns:
        dict: Weight fractions for each mineral (will sum to 1.0)
    """
    # Calculate weight of each mineral
    weights = {}
    total_weight = 0
    
    for mineral, n_moles in moles.items():
        if mineral in molar_masses:
            weight = n_moles * molar_masses[mineral]
            weights[mineral] = weight
            total_weight += weight
        else:
            weights[mineral] = 0.0
    
    # Convert to weight fractions
    if total_weight > 0:
        weight_fractions = {mineral: weight / total_weight for mineral, weight in weights.items()}
    else:
        weight_fractions = {mineral: 0.0 for mineral in moles.keys()}
    
    return weight_fractions

def normalize_weight_fractions(weight_fractions):
    """
    Normalize weight fractions to sum to 1.0.
    
    Args:
        weight_fractions (dict): Weight fractions to normalize
    
    Returns:
        dict: Normalized weight fractions
    """
    total = sum(weight_fractions.values())
    if total > 0:
        return {mineral: frac / total for mineral, frac in weight_fractions.items()}
    else:
        return weight_fractions.copy()

def wt_frac_to_wt_percent(weight_fractions):
    """
    Convert weight fractions to weight percentages.
    
    Args:
        weight_fractions (dict): Weight fractions (0-1)
    
    Returns:
        dict: Weight percentages (0-100)
    """
    return {mineral: frac * 100 for mineral, frac in weight_fractions.items()}

def wt_percent_to_wt_frac(weight_percentages):
    """
    Convert weight percentages to weight fractions.
    
    Args:
        weight_percentages (dict): Weight percentages (0-100)
    
    Returns:
        dict: Weight fractions (0-1)
    """
    return {mineral: percent / 100 for mineral, percent in weight_percentages.items()}

def calculate_mineral_composition(weight_fractions, molar_masses, total_weight=None):
    """
    Calculate the weight and number of moles for each mineral in a sample.
    
    Args:
        weight_fractions (dict): Weight fraction of each mineral
        molar_masses (dict): Molar mass of each mineral (g/mol)
        total_weight (float, optional): Total weight of the sample (g). If None, uses TOTAL_SAMPLE_WEIGHT
    
    Returns:
        dict: Dictionary containing weight and moles for each mineral
    """
    if total_weight is None:
        total_weight = TOTAL_SAMPLE_WEIGHT
    
    # Use the conversion function to get moles
    moles = wt_frac_to_moles(weight_fractions, molar_masses, total_weight)
    
    results = {}
    
    print(f"Mineral Composition Analysis for {total_weight}g Sample")
    print("=" * 60)
    print(f"{'Mineral':<15} {'Weight (g)':<12} {'Molar Mass':<12} {'Moles':<12}")
    print("-" * 60)
    
    total_moles = 0
    
    for mineral in weight_fractions:
        if mineral in molar_masses:
            # Calculate weight of this mineral in the sample
            mineral_weight = weight_fractions[mineral] * total_weight
            mineral_moles = moles[mineral]
            
            # Store results
            results[mineral] = {
                'weight_g': mineral_weight,
                'molar_mass_g_per_mol': molar_masses[mineral],
                'moles': mineral_moles
            }
            
            # Print results if there's a significant amount
            if mineral_weight > 0:
                print(f"{mineral:<15} {mineral_weight:<12.2f} {molar_masses[mineral]:<12.2f} {mineral_moles:<12.6f}")
                total_moles += mineral_moles
    
    print("-" * 60)
    print(f"{'TOTAL':<15} {total_weight:<12.2f} {'':<12} {total_moles:<12.6f}")
    print("=" * 60)
    
    return results

# Validate weight fractions sum to 1.0
total_weight_fraction = sum(mineral_weight_fractions.values())
if abs(total_weight_fraction - 1.0) > 0.001:
    print(f"Warning: Weight fractions sum to {total_weight_fraction:.3f}, not 1.0")
    print("Normalizing weight fractions...")
    mineral_weight_fractions = normalize_weight_fractions(mineral_weight_fractions)

# Calculate mineral composition
mineral_composition = calculate_mineral_composition(
    mineral_weight_fractions, 
    mineral_molar_masses
)

# Additional analysis functions
def get_dominant_minerals(composition, min_weight_percent=1.0):
    """
    Get minerals that make up more than a specified percentage of the sample.
    
    Args:
        composition (dict): Results from calculate_mineral_composition
        min_weight_percent (float): Minimum weight percentage to be considered dominant
    
    Returns:
        list: List of dominant minerals
    """
    min_weight = (min_weight_percent / 100) * TOTAL_SAMPLE_WEIGHT
    dominant = []
    
    for mineral, data in composition.items():
        if data['weight_g'] >= min_weight:
            weight_percent = (data['weight_g'] / TOTAL_SAMPLE_WEIGHT) * 100
            dominant.append((mineral, weight_percent, data['moles']))
    
    # Sort by weight percentage (descending)
    dominant.sort(key=lambda x: x[1], reverse=True)
    return dominant

def calculate_molar_percentages(composition):
    """
    Calculate molar percentages of each mineral.
    
    Args:
        composition (dict): Results from calculate_mineral_composition
    
    Returns:
        dict: Molar percentages for each mineral
    """
    total_moles = sum(data['moles'] for data in composition.values())
    
    if total_moles == 0:
        return {mineral: 0 for mineral in composition}
    
    molar_percentages = {}
    for mineral, data in composition.items():
        molar_percentages[mineral] = (data['moles'] / total_moles) * 100
    
    return molar_percentages

if __name__ == "__main__":
    # Print dominant minerals
    print("\nDominant Minerals (>1% by weight):")
    print("-" * 50)
    dominant_minerals = get_dominant_minerals(mineral_composition, min_weight_percent=1.0)

    for mineral, weight_percent, moles in dominant_minerals:
        print(f"{mineral}: {weight_percent:.1f}% by weight, {moles:.6f} moles")

    # Print molar percentages
    print("\nMolar Percentages:")
    print("-" * 30)
    molar_percentages = calculate_molar_percentages(mineral_composition)

    for mineral, molar_percent in molar_percentages.items():
        if molar_percent > 0:
            print(f"{mineral}: {molar_percent:.2f}% by moles")

    # Summary statistics
    total_moles = sum(data['moles'] for data in mineral_composition.values())
    average_molar_mass = TOTAL_SAMPLE_WEIGHT / total_moles if total_moles > 0 else 0

    print(f"\nSummary Statistics:")
    print(f"Total moles in sample: {total_moles:.6f}")
    print(f"Average molar mass: {average_molar_mass:.2f} g/mol")
    print(f"Number of mineral phases: {len([m for m, d in mineral_composition.items() if d['weight_g'] > 0])}")

    # Example usage of conversion functions
    print("\n" + "="*60)
    print("CONVERSION FUNCTIONS EXAMPLES")
    print("="*60)

    # Example 1: Convert weight fractions to moles
    print("\n1. Converting weight fractions to moles:")
    print("-" * 40)
    example_wt_fractions = {
        'Quartz': 0.6,
        'Albite': 0.25,
        'Calcite': 0.15
    }
    print("Input weight fractions:", example_wt_fractions)
    example_moles = wt_frac_to_moles(example_wt_fractions, mineral_molar_masses)
    print("Output moles:", {k: f"{v:.6f}" for k, v in example_moles.items()})

    # Example 2: Convert moles back to weight fractions
    print("\n2. Converting moles back to weight fractions:")
    print("-" * 45)
    print("Input moles:", {k: f"{v:.6f}" for k, v in example_moles.items()})
    recovered_wt_fractions = moles_to_wt_frac(example_moles, mineral_molar_masses)
    print("Output weight fractions:", {k: f"{v:.6f}" for k, v in recovered_wt_fractions.items()})
    print("Sum of weight fractions:", f"{sum(recovered_wt_fractions.values()):.6f}")

    # Example 3: Weight percentage conversions
    print("\n3. Weight percentage conversions:")
    print("-" * 35)
    wt_percent = wt_frac_to_wt_percent(example_wt_fractions)
    print("Weight percentages:", {k: f"{v:.1f}%" for k, v in wt_percent.items()})
    recovered_fractions = wt_percent_to_wt_frac(wt_percent)
    print("Back to fractions:", {k: f"{v:.3f}" for k, v in recovered_fractions.items()})

    # Example 4: Working with different sample weights
    print("\n4. Different sample weights:")
    print("-" * 30)
    small_sample_moles = wt_frac_to_moles(example_wt_fractions, mineral_molar_masses, total_weight=100)
    large_sample_moles = wt_frac_to_moles(example_wt_fractions, mineral_molar_masses, total_weight=10000)
    print(f"100g sample moles: {sum(small_sample_moles.values()):.6f}")
    print(f"10kg sample moles: {sum(large_sample_moles.values()):.6f}")
    print(f"Ratio (should be 100): {sum(large_sample_moles.values())/sum(small_sample_moles.values()):.1f}")

    print("\n" + "="*60)

