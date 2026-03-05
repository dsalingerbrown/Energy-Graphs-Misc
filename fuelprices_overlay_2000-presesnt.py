import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# 1. Load the data
file_path = '/Users/dannysalingerbrown/Desktop/Energy-Graphs-Misc/data/WorldBank_Commodity_Monthly.csv' 
df = pd.read_csv(file_path, skiprows=4)

# 2. Clean up columns and dates
df = df.rename(columns={df.columns[0]: 'Date'})
df['Date'] = pd.to_datetime(df['Date'].str.replace('M', '-'), errors='coerce')

# Target the specific columns based on the World Bank Pink Sheet
oil_col = 'Crude oil, Brent'
coal_col = 'Coal, Australian'
gas_col = 'Natural gas, US'

# Ensure all target columns are numeric
for col in [oil_col, coal_col, gas_col]:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# 3. Filter (2000 to present) and drop rows missing any of our 3 fuels
df_filtered = df[df['Date'] >= '2000-01-01'].copy()
df_filtered = df_filtered.dropna(subset=[oil_col, coal_col, gas_col])

# 4. Standardize all prices to $/MMBtu
# Gas is natively in $/MMBtu
df_filtered['Gas_MMBtu'] = df_filtered[gas_col]

# Oil: Updated to 5 MMBtu per barrel
df_filtered['Oil_MMBtu'] = df_filtered[oil_col] / 5.0

# Coal: Updated to 26 MMBtu per metric ton
df_filtered['Coal_MMBtu'] = df_filtered[coal_col] / 26.0

# 5. Create and Save the Combined Graph
plt.figure(figsize=(14, 7))

# Plotting each fuel with distinct colors
plt.plot(df_filtered['Date'], df_filtered['Oil_MMBtu'], label='Brent Crude', color='#c0392b', linewidth=2)
plt.plot(df_filtered['Date'], df_filtered['Coal_MMBtu'], label='Australian Coal', color='#7f8c8d', linewidth=2)
plt.plot(df_filtered['Date'], df_filtered['Gas_MMBtu'], label='US Natural Gas', color='#2980b9', linewidth=2)

# Set axis labels to be larger
plt.ylabel('Nominal USD per MMBtu ($/MMBtu)', fontsize=16)
plt.xlabel('Year', fontsize=16)

# Add legend (enlarged slightly to match the new axis sizes)
plt.legend(loc='upper left', fontsize=14)

# Format x-axis ticks: Every 2 years
ax = plt.gca()
ax.xaxis.set_major_locator(mdates.YearLocator(2))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

# Slant x-axis labels and make all tick markers larger
plt.xticks(rotation=45)
plt.tick_params(axis='both', which='major', labelsize=14)

plt.tight_layout()

# Save to your project folder with transparent background
plt.savefig('/Users/dannysalingerbrown/Desktop/Energy-Graphs-Misc/combined_fuels_mmbtu.png', dpi=300, transparent=True)
plt.show()

# Verify the final aligned data points
print("Latest Data Points ($/MMBtu):")
print(df_filtered[['Date', 'Oil_MMBtu', 'Coal_MMBtu', 'Gas_MMBtu']].tail())