import pandas as pd
import matplotlib.pyplot as plt

# 1. Load the data
file_path = '/Users/dannysalingerbrown/Desktop/Energy-Graphs-Misc/data/WorldBank_Commodity_Monthly.csv' 
df = pd.read_csv(file_path, skiprows=4)

# 2. Clean up columns and dates
df = df.rename(columns={df.columns[0]: 'Date'})
df['Date'] = pd.to_datetime(df['Date'].str.replace('M', '-'), errors='coerce')
df['Coal, Australian'] = pd.to_numeric(df['Coal, Australian'], errors='coerce')

# 3. Filter and Convert
df_filtered = df[df['Date'] >= '2000-01-01'].dropna(subset=['Coal, Australian']).copy()

# New conversion: $/mt divided by 20 MMBtu/mt
df_filtered['Coal_MMBtu'] = df_filtered['Coal, Australian'] / 20

# 4. Create and Save Graph 1 ($/tonne)
plt.figure(figsize=(12, 6))
plt.plot(df_filtered['Date'], df_filtered['Coal, Australian'], color='#e67e22', linewidth=2)
plt.title('Newcastle Coal Price Index: 2000 – 2026', fontsize=14, fontweight='bold')
plt.ylabel('Nominal USD per Metric Ton ($/tonne)', fontsize=12)
plt.xlabel('Year', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()

# Saving to your project folder
plt.savefig('/Users/dannysalingerbrown/Desktop/Energy-Graphs-Misc/coal_price_tonne.png', dpi=300)
plt.show()

# 5. Create and Save Graph 2 ($/MMBtu)
plt.figure(figsize=(12, 6))
plt.plot(df_filtered['Date'], df_filtered['Coal_MMBtu'], color='#2980b9', linewidth=2)
plt.title('Newcastle Coal Price Index ($/MMBtu): 2000 – 2026', fontsize=14, fontweight='bold')
plt.ylabel('Nominal USD per MMBtu ($/MMBtu)', fontsize=12)
plt.xlabel('Year', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()

# Saving to your project folder
plt.savefig('/Users/dannysalingerbrown/Desktop/Energy-Graphs-Misc/coal_price_mmbtu.png', dpi=300)
plt.show()

# Verify the final data points
print(df_filtered[['Date', 'Coal, Australian', 'Coal_MMBtu']].tail())