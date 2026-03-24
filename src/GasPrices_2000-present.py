import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# 1. Load the data
file_path = '/Users/dannysalingerbrown/Desktop/Energy-Graphs-Misc/data/WorldBank_Commodity_Monthly.csv' 
df = pd.read_csv(file_path, skiprows=4)

# 2. Clean up columns and dates
df = df.rename(columns={df.columns[0]: 'Date'})
df['Date'] = pd.to_datetime(df['Date'].str.replace('M', '-'), errors='coerce')

# Target the US Natural Gas column specifically (Henry Hub)
gas_col = 'Natural gas, US'
df[gas_col] = pd.to_numeric(df[gas_col], errors='coerce')

# 3. Filter and Convert (2000 to present)
df_filtered = df[df['Date'] >= '2000-01-01'].dropna(subset=[gas_col]).copy()

# Conversion: $/MMBtu to $/Mcf
# Using the standard energy density factor of 1.038 MMBtu per Mcf
df_filtered['Gas_Mcf'] = df_filtered[gas_col] * 1.038

# --- Grab the starting coordinates for our text labels ---
# We use the very first date in the filtered dataset, plus a small date shift 
label_x_date = df_filtered['Date'].iloc[0] + pd.Timedelta(days=180) 
start_price_mmbtu = df_filtered[gas_col].iloc[0]
start_price_mcf = df_filtered['Gas_Mcf'].iloc[0]

# 4. Create and Save Graph 1 ($/MMBtu)
plt.figure(figsize=(12, 6))
plt.plot(df_filtered['Date'], df_filtered[gas_col], color='#2980b9', linewidth=2)

# Add text label above the start of the line (offset by +1 for the MMBtu scale)
plt.text(label_x_date, start_price_mmbtu-1, 'Natural Gas (Henry Hub)', 
         color='#2980b9', fontsize=14, fontweight='bold')

# Set axis labels to be larger
plt.ylabel('Nominal USD per MMBtu ($/MMBtu)', fontsize=16)
plt.xlabel('Year', fontsize=16)

# Format x-axis ticks: Every 2 years
ax = plt.gca()
ax.xaxis.set_major_locator(mdates.YearLocator(2))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

# Slant x-axis labels and make all tick markers larger
plt.xticks(rotation=45)
plt.tick_params(axis='both', which='major', labelsize=14)

plt.tight_layout()
# Save with transparent background
plt.savefig('/Users/dannysalingerbrown/Desktop/Energy-Graphs-Misc/natgas_price_mmbtu.png', dpi=300, transparent=True)
plt.show()

# 5. Create and Save Graph 2 ($/Mcf)
plt.figure(figsize=(12, 6))
plt.plot(df_filtered['Date'], df_filtered['Gas_Mcf'], color='#27ae60', linewidth=2)

# Add text label above the start of the line (offset by +1 for the Mcf scale)
plt.text(label_x_date, start_price_mcf-1, 'Natural Gas (Henry Hub)', 
         color='#27ae60', fontsize=14, fontweight='bold')

# Set axis labels to be larger
plt.ylabel('Nominal USD per Thousand Cubic Feet ($/Mcf)', fontsize=16)
plt.xlabel('Year', fontsize=16)

# Format x-axis ticks: Every 2 years
ax2 = plt.gca()
ax2.xaxis.set_major_locator(mdates.YearLocator(2))
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

# Slant x-axis labels and make all tick markers larger
plt.xticks(rotation=45)
plt.tick_params(axis='both', which='major', labelsize=14)

plt.tight_layout()
# Save with transparent background
plt.savefig('/Users/dannysalingerbrown/Desktop/Energy-Graphs-Misc/natgas_price_mcf.png', dpi=300, transparent=True)
plt.show()

# Verify the final data points
print("Latest Data Points:")
print(df_filtered[['Date', gas_col, 'Gas_Mcf']].tail())