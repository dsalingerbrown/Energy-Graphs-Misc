import pandas as pd
import matplotlib.pyplot as plt

# 1. Load the data
file_path = '/Users/dannysalingerbrown/Desktop/Energy-Graphs-Misc/data/WorldBank_Commodity_Monthly.csv' 
df = pd.read_csv(file_path, skiprows=4)

# 2. Clean up columns and dates
df = df.rename(columns={df.columns[0]: 'Date'})
df['Date'] = pd.to_datetime(df['Date'].str.replace('M', '-'), errors='coerce')

# Target Brent Crude column specifically
df['Crude oil, Brent'] = pd.to_numeric(df['Crude oil, Brent'], errors='coerce')

# 3. Filter and Convert (2000 to present)
df_filtered = df[df['Date'] >= '2000-01-01'].dropna(subset=['Crude oil, Brent']).copy()

# Conversion: $/bbl divided by 5 MMBtu/bbl
df_filtered['Oil_MMBtu'] = df_filtered['Crude oil, Brent'] / 5

# 4. Create and Save Graph 1 ($/barrel)
plt.figure(figsize=(12, 6))
plt.plot(df_filtered['Date'], df_filtered['Crude oil, Brent'], color='#c0392b', linewidth=2)
plt.title('Brent Crude Oil Price: 2000 – 2026', fontsize=14, fontweight='bold')
plt.ylabel('Nominal USD per Barrel ($/bbl)', fontsize=12)
plt.xlabel('Year', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()

# Saving to your project folder
plt.savefig('/Users/dannysalingerbrown/Desktop/Energy-Graphs-Misc/oil_price_bbl.png', dpi=300)
plt.show()

# 5. Create and Save Graph 2 ($/MMBtu)
plt.figure(figsize=(12, 6))
plt.plot(df_filtered['Date'], df_filtered['Oil_MMBtu'], color='#8e44ad', linewidth=2)
plt.title('Brent Crude Oil Price ($/MMBtu): 2000 – 2026', fontsize=14, fontweight='bold')
plt.ylabel('Nominal USD per MMBtu ($/MMBtu)', fontsize=12)
plt.xlabel('Year', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()

# Saving to your project folder
plt.savefig('/Users/dannysalingerbrown/Desktop/Energy-Graphs-Misc/oil_price_mmbtu.png', dpi=300)
plt.show()

# Verify the final data points
print(df_filtered[['Date', 'Crude oil, Brent', 'Oil_MMBtu']].tail())