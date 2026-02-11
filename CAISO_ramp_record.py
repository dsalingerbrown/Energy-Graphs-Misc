import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import os

# --- 1. CONFIGURATION ---
DATA_FOLDER = 'data'
FILES = {
    'supply':     os.path.join(DATA_FOLDER, 'CAISO-supply-20251005.csv'),
    'renewables': os.path.join(DATA_FOLDER, 'CAISO-renewables-20251005.csv'),
    'net_demand': os.path.join(DATA_FOLDER, 'CAISO-netdemand-20251005.csv'),
    'batteries':  os.path.join(DATA_FOLDER, 'CAISO-batteries-20251005.csv'),
    'imports':    os.path.join(DATA_FOLDER, 'CAISO-imports-20251005.csv')
}

DPI = 300
FIG_SIZE = (10, 6)

RENEWABLES_ORDER = ['Biomass', 'Biogas', 'Geothermal', 'Small hydro', 'Wind', 'Solar']

SUPPLY_ORDER = [
    'Batteries', 
    'Imports', 
    'Other', 
    'Coal', 
    'Nuclear', 
    'Large hydro', 
    'Natural gas', 
    'Renewables'
]

COLOR_MAP = {
    'Renewables': '#54a24b',       # Green
    'Solar': '#f28e2b',            # Orange
    'Wind': '#4e79a7',             # Blue
    'Natural gas': '#d37295',      # Rust/Pinkish 
    'Large hydro': '#499894',      # Teal
    'Small hydro': '#86bcb6',      # Light Teal
    'Nuclear': '#e15759',          # Red
    'Coal': '#000000',             # Black
    'Imports': '#9d7660',          # Brown
    'Batteries': '#5e4fa2',        # Purple
    'Biomass': '#bab0ac',          # Grey
    'Geothermal': '#59a14f',       # Green
    'Biogas': '#ff9da7',           # Light Pink
    'Other': '#d7d7d7',            # Light Grey
    'Demand': '#499894',           # Teal Line
    'Net demand': '#5e4fa2',       # Dark Purple Line/Area
    'Day-ahead net forecast': '#bab0ac', 
    'Hour-ahead forecast': '#76b7b2'
}

# --- 2. DATA PROCESSING ---

def load_and_transpose_data(file_path):
    if not os.path.exists(file_path):
        print(f"⚠️ File not found: {file_path}")
        return None
    try:
        df = pd.read_csv(file_path, index_col=0)
        df = df.T
        df.index = df.index.str.strip()
        df.index.name = 'Time'
        return df
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

def format_plot(ax, title, ylabel, data_len):
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.set_xlabel("Hour", fontsize=12)
    ax.grid(axis='y', linestyle='--', alpha=0.5)
    
    tick_indices = list(range(0, data_len + 1, 12)) 
    tick_labels = [str(i) for i in range(len(tick_indices))]
    
    ax.set_xticks(tick_indices)
    ax.set_xticklabels(tick_labels, fontsize=10)
    ax.set_xlim(0, data_len) 
    plt.yticks(fontsize=10)

# --- 3. PLOTTING FUNCTIONS ---

def plot_supply_trend(df, title, filename):
    if df is None: return
    df = df.apply(pd.to_numeric, errors='coerce').fillna(0)
    
    df_pos = df.clip(lower=0)
    df_neg = df.clip(upper=0)
    
    pos_cols = [c for c in SUPPLY_ORDER if c in df_pos.columns and df_pos[c].sum() > 0]
    remaining_cols = [c for c in df_pos.columns if c not in pos_cols and df_pos[c].sum() > 0]
    pos_cols = pos_cols + remaining_cols
    df_pos = df_pos[pos_cols]
    
    neg_cols = [c for c in df_neg.columns if df_neg[c].sum() < 0]
    df_neg = df_neg[neg_cols]
    
    fig, ax = plt.subplots(figsize=FIG_SIZE)
    colors_pos = [COLOR_MAP.get(col, '#333333') for col in pos_cols]
    ax.stackplot(range(len(df)), df_pos.T, labels=pos_cols, colors=colors_pos, alpha=0.9)
    
    if not df_neg.empty:
        colors_neg = [COLOR_MAP.get(col, '#333333') for col in neg_cols]
        ax.stackplot(range(len(df)), df_neg.T, labels=neg_cols, colors=colors_neg, alpha=0.9)
    
    format_plot(ax, title, "Generation (MW)", len(df))
    plt.subplots_adjust(right=0.75)
    
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    unique_labels = list(by_label.keys())[::-1]
    unique_handles = list(by_label.values())[::-1]
    
    ax.legend(unique_handles, unique_labels, loc='center left', bbox_to_anchor=(1.02, 0.5), title="Resource")
    plt.savefig(filename, dpi=DPI)
    plt.close()
    print(f"✅ Generated: {filename}")

def plot_renewables(df, title, filename):
    if df is None: return
    df = df.apply(pd.to_numeric, errors='coerce').fillna(0)
    
    present_cols = [c for c in RENEWABLES_ORDER if c in df.columns]
    df = df[present_cols]
    colors = [COLOR_MAP.get(col, '#333333') for col in present_cols]
    
    fig, ax = plt.subplots(figsize=FIG_SIZE)
    ax.stackplot(range(len(df)), df.T, labels=present_cols, colors=colors, alpha=0.9)
    
    format_plot(ax, title, "Generation (MW)", len(df))
    plt.subplots_adjust(right=0.75)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1], loc='center left', bbox_to_anchor=(1.02, 0.5), title="Resource")
    
    plt.savefig(filename, dpi=DPI)
    plt.close()
    print(f"✅ Generated: {filename}")

def plot_net_demand(df, title, filename):
    if df is None: return
    df = df.apply(pd.to_numeric, errors='coerce').fillna(0)

    fig, ax = plt.subplots(figsize=FIG_SIZE)
    x_idx = range(len(df))
    
    if 'Demand' in df.columns:
        ax.plot(x_idx, df['Demand'], color=COLOR_MAP['Demand'], linewidth=2, label='Demand')
    if 'Net demand' in df.columns:
        ax.plot(x_idx, df['Net demand'], color=COLOR_MAP['Net demand'], linewidth=2, label='Net demand')
        ax.fill_between(x_idx, df['Net demand'], color=COLOR_MAP['Net demand'], alpha=0.2)
    if 'Day-ahead net forecast' in df.columns:
        ax.plot(x_idx, df['Day-ahead net forecast'], color=COLOR_MAP['Day-ahead net forecast'], 
                linestyle=':', linewidth=1.5, label='Day-ahead net forecast')

    format_plot(ax, title, "Megawatts (MW)", len(df))
    plt.subplots_adjust(right=0.75)
    ax.legend(loc='center left', bbox_to_anchor=(1.02, 0.5))
    plt.savefig(filename, dpi=DPI)
    plt.close()
    print(f"✅ Generated: {filename}")

def plot_batteries(df, title, filename):
    if df is None: return
    df = df.apply(pd.to_numeric, errors='coerce').fillna(0)
    col_name = df.columns[0]
    
    fig, ax = plt.subplots(figsize=FIG_SIZE)
    x_idx = range(len(df))
    
    ax.plot(x_idx, df[col_name], color=COLOR_MAP['Batteries'], linewidth=1.5)
    ax.fill_between(x_idx, df[col_name], 0, color=COLOR_MAP['Batteries'], alpha=0.5)
    ax.axhline(0, color='black', linewidth=1)
    
    ax.text(0.02, 0.9, 'Discharging (+)', transform=ax.transAxes, color='#555', fontweight='bold')
    ax.text(0.02, 0.1, 'Charging (-)', transform=ax.transAxes, color='#555', fontweight='bold')

    format_plot(ax, title, "Megawatts (MW)", len(df))
    plt.subplots_adjust(right=0.75)
    plt.savefig(filename, dpi=DPI)
    plt.close()
    print(f"✅ Generated: {filename}")

def plot_imports(df, title, filename):
    if df is None: return
    df = df.apply(pd.to_numeric, errors='coerce').fillna(0)
    col_name = df.columns[0]
    
    fig, ax = plt.subplots(figsize=FIG_SIZE)
    ax.plot(range(len(df)), df[col_name], color=COLOR_MAP['Imports'], linewidth=2.5, label='Imports')
    
    format_plot(ax, title, "Megawatts (MW)", len(df))
    plt.subplots_adjust(right=0.75)
    plt.savefig(filename, dpi=DPI)
    plt.close()
    print(f"✅ Generated: {filename}")

# --- 4. MAIN EXECUTION ---
def main():
    print("--- Starting Graph Generation ---")
    
    # Titles updated with "CA" prefix
    plot_supply_trend(load_and_transpose_data(FILES['supply']), 
                      "CA Supply Trend (Oct 5, 2025)", "1_Supply_Trend.png")

    plot_renewables(load_and_transpose_data(FILES['renewables']), 
                      "CA Renewables Trend (Oct 5, 2025)", "2_Renewables_Trend.png")

    plot_net_demand(load_and_transpose_data(FILES['net_demand']), 
                      "CA Net Demand Trend (Oct 5, 2025)", "3_Net_Demand.png")

    plot_batteries(load_and_transpose_data(FILES['batteries']), 
                      "CA Batteries Trend (Oct 5, 2025)", "4_Batteries.png")

    plot_imports(load_and_transpose_data(FILES['imports']), 
                      "CA Imports Trend (Oct 5, 2025)", "5_Imports.png")
    
    print("--- All Graphs Completed ---")

if __name__ == "__main__":
    main()