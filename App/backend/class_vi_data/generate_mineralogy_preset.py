import pandas as pd
import json

# Read the CSV file
mineralogy = pd.read_csv("backend/class_vi_data/mineralogy.csv")

# Replace "Tr" values with 0 in all columns
mineralogy = mineralogy.replace("Tr", 0)

# Select and rename columns as in the original script
mineralogy = mineralogy[
    [
        "API Number",
        "Depth",
        "Quartz",
        "Calcite/Aragonite",
        "Dolomite",
        "Siderite",
        "Total K-feldspars",
        "Albite",
        "Illite",
        "Kaolinite",
        "Pyrite",
        "Chlorite",
        "Smectite",
    ]
]

mineralogy = mineralogy.rename(
    columns={
        "Total K-feldspars": "K-feldspar",
        "Calcite/Aragonite": "Calcite",
    }
)

# Convert all mineral columns to numeric (excluding API Number and Depth)
mineral_columns = [col for col in mineralogy.columns if col not in ['API Number', 'Depth']]
for col in mineral_columns:
    mineralogy[col] = pd.to_numeric(mineralogy[col], errors='coerce')

# Fill NaN values with 0
mineralogy = mineralogy.fillna(0)

# Remove rows where API Number or Depth is NaN or empty
mineralogy = mineralogy.dropna(subset=['API Number', 'Depth'])
mineralogy = mineralogy[mineralogy['API Number'] != '']
mineralogy = mineralogy[mineralogy['Depth'] != '']

# Create composite identifier with API Number and Depth
mineralogy['Composite_ID'] = mineralogy['API Number'].astype(str) + ' (' + mineralogy['Depth'].astype(str) + 'ft)'

print("Column names after processing:")
print(mineralogy.columns.tolist())
print(f"\nNumber of samples: {len(mineralogy)}")
print(f"Number of unique composite IDs: {mineralogy['Composite_ID'].nunique()}")

# Create the presets dictionary
presets = {}

# Iterate through each row and create a preset
for index, row in mineralogy.iterrows():
    composite_id = row['Composite_ID']
    
    # Skip if Composite ID is empty
    if not composite_id or composite_id == 'nan':
        continue
    
    # Create preset for this composite ID
    preset = {}
    mineral_values = []
    
    # First pass: collect all mineral values (excluding API Number, Depth, and Composite_ID)
    for column in mineralogy.columns:
        if column not in ['API Number', 'Depth', 'Composite_ID']:
            # Convert to float and ensure it's between 0 and 1 (assuming percentages)
            value = float(row[column])
            # If values are in percentages (>1), convert to fractions
            if value > 1:
                value = value / 100
            mineral_values.append((column, value))
    
    # Calculate sum of all mineral fractions
    total_sum = sum(value for _, value in mineral_values)
    
    # Normalize if sum is not equal to 1 (with small tolerance for floating point precision)
    if abs(total_sum - 1.0) > 1e-6:
        if total_sum > 0:  # Avoid division by zero
            # Normalize each value by the total sum
            for column, value in mineral_values:
                normalized_value = value / total_sum
                preset[column] = round(normalized_value, 4)
        else:
            # If all values are zero, set equal fractions
            equal_fraction = 1.0 / len(mineral_values)
            for column, _ in mineral_values:
                preset[column] = round(equal_fraction, 4)
    else:
        # Sum is already 1, just round the values
        for column, value in mineral_values:
            preset[column] = round(value, 4)
    
    presets[composite_id] = preset

print(f"\nGenerated {len(presets)} presets")

# Save to JSON file
output_path = "frontend/src/presets/mineralogyPresets.json"
with open(output_path, 'w') as f:
    json.dump(presets, f, indent=2)

print(f"Mineralogy presets saved to {output_path}")

# Display first few presets as example
print("\nFirst 3 presets:")
for i, (key, value) in enumerate(presets.items()):
    if i >= 3:
        break
    print(f"\n{key}:")
    for mineral, amount in value.items():
        print(f"  {mineral}: {amount}")