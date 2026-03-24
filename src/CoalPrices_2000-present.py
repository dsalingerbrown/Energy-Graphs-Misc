import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

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

# --- Grab the starting coordinates for our text labels ---
# We will use the very first date in the filtered dataset, plus a small date shift 
# so it doesn't hug the y-axis too tightly.
label_x_date = df_filtered['Date'].iloc[0] + pd.Timedelta(days=180) 
start_price_tonne = df_filtered['Coal, Australian'].iloc[0]
start_price_mmbtu = df_filtered['Coal_MMBtu'].iloc[0]

# 4. Create and Save Graph 1 ($/tonne)
plt.figure(figsize=(12, 6))
plt.plot(df_filtered['Date'], df_filtered['Coal, Australian'], color='#e67e22', linewidth=2)

# Add text label above the start of the line (offset by +15 for the tonne scale)
plt.text(label_x_date, start_price_tonne + 40, 'Coal (Newcastle Index)', 
         color='#e67e22', fontsize=14, fontweight='bold')

# Set axis labels to be larger
plt.ylabel('Nominal USD per Metric Ton ($/tonne)', fontsize=16)
plt.xlabel('Year', fontsize=16)

# Format x-axis ticks: Every 2 years
ax = plt.gca()
ax.xaxis.set_major_locator(mdates.YearLocator(2))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

# Slant x-axis labels and make all tick markers larger
plt.xticks(rotation=45)
plt.tick_params(axis='both', which='major', labelsize=14)

plt.tight_layout()
# Added transparent=True here
plt.savefig('/Users/dannysalingerbrown/Desktop/Energy-Graphs-Misc/coal_price_tonne.png', dpi=300, transparent=True)
plt.show()

# 5. Create and Save Graph 2 ($/MMBtu)
plt.figure(figsize=(12, 6))
plt.plot(df_filtered['Date'], df_filtered['Coal_MMBtu'], color='#2980b9', linewidth=2)

# Add text label above the start of the line (offset by +0.75 for the MMBtu scale)
plt.text(label_x_date, start_price_mmbtu + 2, 'Coal (Newcastle Index)', 
         color='#2980b9', fontsize=14, fontweight='bold')

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
# Added transparent=True here
plt.savefig('/Users/dannysalingerbrown/Desktop/Energy-Graphs-Misc/coal_price_mmbtu.png', dpi=300, transparent=True)
plt.show()

# Verify the final data points
print(df_filtered[['Date', 'Coal, Australian', 'Coal_MMBtu']].tail())