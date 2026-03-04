import pandas as pd
import matplotlib.pyplot as plt

# 1. Load the data
file_path = '/Users/dannysalingerbrown/Desktop/Energy-Graphs-Misc/data/WorldBank_Commodity_Monthly.csv' 
df = pd.read_csv(file_path, skiprows=4)

# 2. Clean up columns and dates
df = df.rename(columns={df.columns[0]: 'Date'})
df['Date'] = pd.to_datetime(df['Date'].str.replace('M', '-'), errors='coerce')

# Target the US Natural Gas column specifically (Henry Hub)
# Using the exact name from the World Bank dataset
gas_col = 'Natural gas, US'
df[gas_col] = pd.to_numeric(df[gas_col], errors='coerce')

# 3. Filter and Convert (2000 to present)
df_filtered = df[df['Date'] >= '2000-01-01'].dropna(subset=[gas_col]).copy()

# Conversion: $/MMBtu to $/Mcf
# Using the standard energy density factor of 1.038 MMBtu per Mcf
df_filtered['Gas_Mcf'] = df_filtered[gas_col] * 1.038

# 4. Create and Save Graph 1 ($/MMBtu)
plt.figure(figsize=(12, 6))
plt.plot(df_filtered['Date'], df_filtered[gas_col], color='#2980b9', linewidth=2)
plt.title('US Natural Gas Price (Henry Hub): 2000 – 2026', fontsize=14, fontweight='bold')
plt.ylabel('Nominal USD per MMBtu ($/MMBtu)', fontsize=12)
plt.xlabel('Year', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()

# Saving to your project folder
plt.savefig('/Users/dannysalingerbrown/Desktop/Energy-Graphs-Misc/natgas_price_mmbtu.png', dpi=300)
plt.show()

# 5. Create and Save Graph 2 ($/Mcf)
plt.figure(figsize=(12, 6))
plt.plot(df_filtered['Date'], df_filtered['Gas_Mcf'], color='#27ae60', linewidth=2)
plt.title('US Natural Gas Price ($/Mcf): 2000 – 2026', fontsize=14, fontweight='bold')
plt.ylabel('Nominal USD per Thousand Cubic Feet ($/Mcf)', fontsize=12)
plt.xlabel('Year', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()

# Saving to your project folder
plt.savefig('/Users/dannysalingerbrown/Desktop/Energy-Graphs-Misc/natgas_price_mcf.png', dpi=300)
plt.show()

# Verify the final data points
print("Latest Data Points:")
print(df_filtered[['Date', gas_col, 'Gas_Mcf']].tail())