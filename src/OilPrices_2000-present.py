import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

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

# --- Grab the starting coordinates for our text labels ---
# We use the very first date in the filtered dataset, plus a small date shift 
label_x_date = df_filtered['Date'].iloc[0] + pd.Timedelta(days=180) 
start_price_bbl = df_filtered['Crude oil, Brent'].iloc[0]
start_price_mmbtu = df_filtered['Oil_MMBtu'].iloc[0]

# 4. Create and Save Graph 1 ($/barrel)
plt.figure(figsize=(12, 6))
plt.plot(df_filtered['Date'], df_filtered['Crude oil, Brent'], color='#c0392b', linewidth=2)

# Add text label above the start of the line (offset by +10 for the bbl scale)
plt.text(label_x_date, start_price_bbl + 30, 'Brent Crude Oil', 
         color='#c0392b', fontsize=14, fontweight='bold')

# Set axis labels to be larger
plt.ylabel('Nominal USD per Barrel ($/bbl)', fontsize=16)
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
plt.savefig('/Users/dannysalingerbrown/Desktop/Energy-Graphs-Misc/oil_price_bbl.png', dpi=300, transparent=True)
plt.show()

# 5. Create and Save Graph 2 ($/MMBtu)
plt.figure(figsize=(12, 6))
plt.plot(df_filtered['Date'], df_filtered['Oil_MMBtu'], color='#8e44ad', linewidth=2)

# Add text label above the start of the line (offset by +2 for the MMBtu scale)
plt.text(label_x_date, start_price_mmbtu + 6, 'Brent Crude Oil', 
         color='#8e44ad', fontsize=14, fontweight='bold')

# Set axis labels to be larger
plt.ylabel('Nominal USD per MMBtu ($/MMBtu)', fontsize=16)
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
plt.savefig('/Users/dannysalingerbrown/Desktop/Energy-Graphs-Misc/oil_price_mmbtu.png', dpi=300, transparent=True)
plt.show()

# Verify the final data points
print(df_filtered[['Date', 'Crude oil, Brent', 'Oil_MMBtu']].tail())