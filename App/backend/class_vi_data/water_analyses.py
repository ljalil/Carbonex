import pandas as pd
import json

# Read the CSV file
war = pd.read_csv("backend/class_vi_data/water_analyses.csv")

# Select relevant columns
war = war[
    [
        "API Number",
        "Formation",
        "Sodium (mg/L)",
        "Potassium (mg/L)",
        "Magnesium (mg/L)",
        "Calcium (mg/L)",
        "Chloride (mg/L)",
        "Sulfate (mg/L)",
        "Bicarbonate (mg/L)",
        "Carbonate (mg/L)",
        "pH",
    ]
]

# Rename columns to match store structure (using ion notation)
war = war.rename(
    columns={
        "Sodium (mg/L)": "Na+",
        "Potassium (mg/L)": "K+",
        "Magnesium (mg/L)": "Mg+2",
        "Calcium (mg/L)": "Ca+2",
        "Chloride (mg/L)": "Cl-",
        "Sulfate (mg/L)": "SO4-2",
        "Bicarbonate (mg/L)": "HCO3-",
        "Carbonate (mg/L)": "CO3-2",
    }
)

# Convert all concentration columns to numeric
ion_columns = ["Na+", "K+", "Mg+2", "Ca+2", "Cl-", "SO4-2", "HCO3-", "CO3-2"]
for col in ion_columns:
    war[col] = pd.to_numeric(war[col], errors='coerce')

# Fill NaN values with 0
war = war.fillna(0)

# Remove rows where API Number or Formation is NaN or empty
war = war.dropna(subset=['API Number', 'Formation'])
war = war[war['API Number'] != '']
war = war[war['Formation'] != '']

# Create composite identifier with API Number and Formation name
war['Composite_ID'] = war['API Number'].astype(str) + ' (' + war['Formation'].astype(str) + ')'

print("Column names after processing:")
print(war.columns.tolist())
print(f"\nNumber of samples: {len(war)}")
print(f"Number of unique composite IDs: {war['Composite_ID'].nunique()}")

# Atomic/molecular weights for conversion from mg/L to mol/kg (g/mol)
molar_masses = {
    "Na+": 22.99,      # Sodium
    "K+": 39.10,       # Potassium
    "Mg+2": 24.305,    # Magnesium
    "Ca+2": 40.078,    # Calcium
    "Cl-": 35.45,      # Chloride
    "SO4-2": 96.06,    # Sulfate (as SO4)
    "HCO3-": 61.017,   # Bicarbonate
    "CO3-2": 60.009,   # Carbonate
}

# Typical partial molar volumes at 25 °C in cm^3/mol (literature averages)
partial_molar_volumes = {
    "Na+": 16.6,
    "K+": 25.0,
    "Ca+2": -24.4,
    "Mg+2": -19.6,
    "Cl-": 16.6,
    "SO4-2": -20.1,
    "HCO3-": 28.5,
    "CO3-2": 41.5,
}

def solution_density(concentrations_mg_l, temp_c=25.0):
    """
    Estimate solution density from ion concentrations in mg/L
    Returns density in g/cm^3
    """
    # Pure water density at temperature
    rho_w = 0.99987 + 6.69e-5 * temp_c - 8.0e-6 * temp_c * temp_c
    m_w = rho_w * 1000.0  # g/L
    n_w = m_w / 18.015    # mol/L
    V_w = n_w * 18.015    # cm^3/L
    
    m_s = 0.0  # Total mass of solutes
    V_s = 0.0  # Total volume of solutes
    
    for ion, conc_mg_l in concentrations_mg_l.items():
        if ion not in molar_masses or ion not in partial_molar_volumes:
            raise ValueError(f"Missing data for ion {ion}")
        
        M = molar_masses[ion]
        V_m = partial_molar_volumes[ion]
        n_i = (conc_mg_l / 1000.0) / M  # mol/L
        m_i = n_i * M                   # g/L
        V_i = n_i * V_m                 # cm^3/L
        m_s += m_i
        V_s += V_i
    
    m_total = m_w + m_s
    V_total = V_w + V_s
    return m_total / V_total  # g/cm^3

def mg_l_to_molality(concentrations_mg_l, temp_c=25.0):
    """
    Convert mg/L to mol/kg water
    """
    rho = solution_density(concentrations_mg_l, temp_c)
    rho_g_l = rho * 1000.0  # g/L
    
    # Total mass of solutes in g/L
    m_solutes = sum(conc / 1000.0 for conc in concentrations_mg_l.values())
    
    # Mass of water in g/L
    m_water = rho_g_l - m_solutes
    kg_water = m_water / 1000.0
    
    molalities = {}
    for ion, conc_mg_l in concentrations_mg_l.items():
        M = molar_masses[ion]
        n_i = (conc_mg_l / 1000.0) / M  # moles
        b_i = n_i / kg_water             # mol/kg
        molalities[ion] = b_i
    
    return molalities

# Create the presets dictionary
presets = {}

# Iterate through first 100 rows only and create a preset
for index, row in war.head(100).iterrows():
    composite_id = row['Composite_ID']
    
    # Skip if Composite ID is empty
    if not composite_id or composite_id == 'nan':
        continue
    
    # Create preset for this composite ID
    # First, gather all mg/L concentrations for this sample
    concentrations_mg_l = {ion: float(row[ion]) for ion in ion_columns}
    
    # Convert mg/L to mol/kg using proper density-corrected conversion
    molalities = mg_l_to_molality(concentrations_mg_l, temp_c=25.0)
    
    # Round and store
    preset = {ion: round(molalities[ion], 6) for ion in ion_columns}
    
    presets[composite_id] = preset

print(f"\nGenerated {len(presets)} presets")

# Save to JSON file
output_path = "frontend/src/presets/waterChemistryPresets.json"
with open(output_path, 'w') as f:
    json.dump(presets, f, indent=2)

print(f"Water chemistry presets saved to {output_path}")

# Display first few presets as example
print("\nFirst 3 presets:")
for i, (key, value) in enumerate(presets.items()):
    if i >= 3:
        break
    print(f"\n{key}:")
    for ion, concentration in value.items():
        print(f"  {ion}: {concentration} mol/kg")
