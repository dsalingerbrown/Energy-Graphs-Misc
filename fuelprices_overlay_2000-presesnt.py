import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# 1. Load and Clean Data (Unchanged)
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

# Define colors
color_oil = '#e67e22' 
color_coal = '#34495e' 
color_gas = '#2980b9' 

# --- Updated Helper Function ---
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
    ax.text(label_date, df_filtered['Oil_MMBtu'].iloc[0] + 0.1, 'Crude Oil (Brent) ', 
            color=color_oil, fontweight='bold', ha='right', va='bottom', fontsize=12)
    
    # GAS: Sits slightly above its line
    ax.text(label_date, df_filtered['Gas_MMBtu'].iloc[0] + 0.8, 'Gas (US Henry Hub) ', 
            color=color_gas, fontweight='bold', ha='right', va='top', fontsize=12)
    
    # COAL: Sits centered at its line (it is the bottom-most line in 2000)
    ax.text(label_date, df_filtered['Coal_MMBtu'].iloc[0], 'Coal (Newcastle) ', 
            color=color_coal, fontweight='bold', ha='right', va='center', fontsize=12)

    # X-axis formatting
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    
    # BIGGER SHIFT: Set limit to 1992 to provide a clear margin
    ax.set_xlim(left=pd.Timestamp('1995-01-01'), right=df_filtered['Date'].max() + pd.DateOffset(months=6))
    
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
plt.savefig('/Users/dannysalingerbrown/Desktop/Energy-Graphs-Misc/fuels_with_spines.png', dpi=300, transparent=True)
plt.show()

# --- GRAPH 2: CLEAN WITHOUT BOX ---
plt.figure(figsize=(16, 8))
ax2 = plt.gca()
plot_fuels(ax2)

for side in ['top', 'right', 'left', 'bottom']:
    ax2.spines[side].set_visible(False)

plt.tight_layout()
plt.savefig('/Users/dannysalingerbrown/Desktop/Energy-Graphs-Misc/fuels_no_spines.png', dpi=300, transparent=True)
plt.show()