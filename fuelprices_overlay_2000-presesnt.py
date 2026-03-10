import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# 1. Load and Clean Data (Same as your original)
file_path = '/Users/dannysalingerbrown/Desktop/Energy-Graphs-Misc/data/WorldBank_Commodity_Monthly.csv' 
df = pd.read_csv(file_path, skiprows=4)
df = df.rename(columns={df.columns[0]: 'Date'})
df['Date'] = pd.to_datetime(df['Date'].str.replace('M', '-'), errors='coerce')

oil_col = 'Crude oil, Brent'
coal_col = 'Coal, Australian'
gas_col = 'Natural gas, US'

for col in [oil_col, coal_col, gas_col]:
    df[col] = pd.to_numeric(df[col], errors='coerce')

df_filtered = df[df['Date'] >= '2000-01-01'].copy().dropna(subset=[oil_col, coal_col, gas_col])

# Standardization
df_filtered['Gas_MMBtu'] = df_filtered[gas_col]
df_filtered['Oil_MMBtu'] = df_filtered[oil_col] / 5.0
df_filtered['Coal_MMBtu'] = df_filtered[coal_col] / 26.0

# --- Helper Function to Plot (To avoid repeating code) ---
def plot_fuels(ax):
    ax.plot(df_filtered['Date'], df_filtered['Oil_MMBtu'], label='Brent Crude', color='#c0392b', linewidth=2)
    ax.plot(df_filtered['Date'], df_filtered['Coal_MMBtu'], label='Australian Coal', color='#7f8c8d', linewidth=2)
    ax.plot(df_filtered['Date'], df_filtered['Gas_MMBtu'], label='US Natural Gas', color='#2980b9', linewidth=2)
    ax.set_ylabel('Nominal USD per MMBtu ($/MMBtu)', fontsize=16)
    ax.set_xlabel('Year', fontsize=16)
    ax.legend(loc='upper left', fontsize=14)
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.tick_params(axis='x', rotation=45)
    ax.tick_params(axis='both', which='major', labelsize=14)

# --- GRAPH 1: STANDARD WITH BOX ---
plt.figure(figsize=(14, 7))
plot_fuels(plt.gca())
plt.tight_layout()
plt.savefig('/Users/dannysalingerbrown/Desktop/Energy-Graphs-Misc/fuels_with_spines.png', dpi=300, transparent=True)
plt.show()

# --- GRAPH 2: CLEAN WITHOUT BOX ---
plt.figure(figsize=(14, 7))
ax2 = plt.gca()
plot_fuels(ax2)

# Remove the spines (the "box")
for side in ['top', 'right', 'left', 'bottom']:
    ax2.spines[side].set_visible(False)

plt.tight_layout()
plt.savefig('/Users/dannysalingerbrown/Desktop/Energy-Graphs-Misc/fuels_no_spines.png', dpi=300, transparent=True)
plt.show()

print("Latest Data Points ($/MMBtu):")
print(df_filtered[['Date', 'Oil_MMBtu', 'Coal_MMBtu', 'Gas_MMBtu']].tail())