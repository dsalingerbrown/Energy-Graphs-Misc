import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# 1. Load Data
# UPDATE THIS PATH to where your new EIA dataset is saved
file_path = '/Users/dannysalingerbrown/Desktop/Energy-Graphs-Misc/data/EIA_PriceData.csv' 
df = pd.read_csv(file_path)

# 2. Clean and Pivot Data
# Drop the "13th month" rows (which represent annual averages in EIA data)
df = df[df['YYYYMM'] % 100 != 13].copy()

# Convert YYYYMM to datetime
df['Date'] = pd.to_datetime(df['YYYYMM'], format='%Y%m', errors='coerce')

# Ensure the 'Value' column is numeric
df['Value'] = pd.to_numeric(df['Value'], errors='coerce')

# Map the descriptions to our specific categories using partial string matching
def categorize_fuel(desc):
    desc = str(desc)
    if 'Cost of Coal' in desc:
        return 'Coal'
    elif 'Cost of Natur' in desc:
        return 'Gas'
    elif 'Cost of Distil' in desc:
        return 'Distillate'
    elif 'Cost of Resid' in desc:
        return 'Residual'
    return None

df['Fuel'] = df['Description'].apply(categorize_fuel)

# Drop rows that don't match our target fuels
df = df.dropna(subset=['Fuel'])

# Pivot the table to get dates as rows and fuels as columns
df_pivot = df.pivot_table(index='Date', columns='Fuel', values='Value', aggfunc='mean').reset_index()

# Calculate the average of Distillate and Residual for the combined Oil price
df_pivot['Oil_MMBtu'] = df_pivot[['Distillate', 'Residual']].mean(axis=1)

# Standardize column names for the plotting function (No division needed, already in $/MMBtu)
df_pivot['Coal_MMBtu'] = df_pivot['Coal']
df_pivot['Gas_MMBtu'] = df_pivot['Gas']

# Filter for year 2000 onwards and drop rows missing data for our 3 main lines
df_filtered = df_pivot[df_pivot['Date'] >= '2000-01-01'].copy().dropna(subset=['Oil_MMBtu', 'Coal_MMBtu', 'Gas_MMBtu'])

# 3. Plotting Setup
# Define colors
color_oil = '#e67e22' 
color_coal = '#34495e' 
color_gas = '#2980b9' 

def plot_fuels(ax):
    # Plotting lines
    ax.plot(df_filtered['Date'], df_filtered['Oil_MMBtu'], color=color_oil, linewidth=2.5)
    ax.plot(df_filtered['Date'], df_filtered['Coal_MMBtu'], color=color_coal, linewidth=2.5)
    ax.plot(df_filtered['Date'], df_filtered['Gas_MMBtu'], color=color_gas, linewidth=2.5)
    
    ax.set_ylabel('$/MMBtu', fontsize=16)
    ax.set_xlabel('', fontsize=16)
    
    # Labels at the START (Left side)
    first_date = df_filtered['Date'].iloc[0]
    
    # We use a very small horizontal offset for the text itself
    label_date = first_date - pd.DateOffset(months=4)
    
    # OIL: Sits slightly above its line
    ax.text(label_date, df_filtered['Oil_MMBtu'].iloc[0] + 0.1, 'Oil', 
            color=color_oil, fontweight='bold', ha='right', va='bottom', fontsize=12)
    
    # GAS: Sits slightly above its line
    ax.text(label_date, df_filtered['Gas_MMBtu'].iloc[0] + 0.2, 'Natural Gas ', 
            color=color_gas, fontweight='bold', ha='right', va='top', fontsize=12)
    
    # COAL: Sits centered at its line
    ax.text(label_date, df_filtered['Coal_MMBtu'].iloc[0], 'Coal ', 
            color=color_coal, fontweight='bold', ha='right', va='center', fontsize=12)

    # X-axis formatting
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    
    # Limit to provide a clear margin for the text
    ax.set_xlim(left=pd.Timestamp('1997-01-01'), right=df_filtered['Date'].max() + pd.DateOffset(months=6))
    
    # Hide all year labels before 2000
    plt.draw() 
    labels = ax.get_xticklabels()
    for l in labels:
        try:
            year_val = int(l.get_text())
            if year_val < 2000:
                l.set_visible(False)
        except:
            pass
            
    ax.tick_params(axis='x', rotation=45)
    ax.tick_params(axis='both', which='major', labelsize=14)

# --- GRAPH 1: STANDARD WITH BOX ---
plt.figure(figsize=(16, 8)) 
plot_fuels(plt.gca())
plt.tight_layout()
plt.savefig('/Users/dannysalingerbrown/Desktop/Energy-Graphs-Misc/eia_fuels_with_spines.png', dpi=300, transparent=True)
plt.show()

# --- GRAPH 2: CLEAN WITHOUT BOX ---
plt.figure(figsize=(16, 8))
ax2 = plt.gca()
plot_fuels(ax2)

for side in ['top', 'right', 'left', 'bottom']:
    ax2.spines[side].set_visible(False)

plt.tight_layout()
plt.savefig('/Users/dannysalingerbrown/Desktop/Energy-Graphs-Misc/eia_fuels_no_spines.png', dpi=300, transparent=True)
plt.show()