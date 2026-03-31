import pandas as pd
import matplotlib.pyplot as plt
import re

# ==========================================
# 1. CONFIGURATION: Set your targets and files
# ==========================================
TARGET_DATE = '1/15/2026'  
TARGET_HOUR = 16 
TARGET_SCED_TIMESTAMP = '01/15/2026 15:55:00' 

# DAM File Names
FILE_DAM_BIDS = '/Users/dannysalingerbrown/Desktop/Energy-Graphs-Misc/data/March16DAM_60Day/60d_DAM_EnergyBids-16-MAR-26.csv'
FILE_DAM_OFFERS = '/Users/dannysalingerbrown/Desktop/Energy-Graphs-Misc/data/March16DAM_60Day/60d_DAM_EnergyOnlyOffers-16-MAR-26.csv'
FILE_DAM_GEN = '/Users/dannysalingerbrown/Desktop/Energy-Graphs-Misc/data/March16DAM_60Day/60d_DAM_Gen_Resource_Data-16-MAR-26.csv'

# SCED File Names
FILE_SCED_EOC = '/Users/dannysalingerbrown/Desktop/Energy-Graphs-Misc/data/March16SCED_60Day/60d_SCED_Gen_Resource_Data-16-MAR-26.csv' 
FILE_SCED_GEN = '/Users/dannysalingerbrown/Desktop/Energy-Graphs-Misc/data/March16SCED_60Day/60d_SCED_Gen_Resource_Data-16-MAR-26.csv'

# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================
def parse_ercot_curve(df, mw_keyword, price_keyword, is_cumulative=True, limit_keyword=None):
    """Finds paired columns and mathematically converts cumulative ERCOT curves into incremental blocks."""
    mw_cols = [c for c in df.columns if mw_keyword.lower() in c.lower()]
    price_cols = [c for c in df.columns if price_keyword.lower() in c.lower()]
    
    def get_col_num(name):
        match = re.search(r'\d+', name.split('-')[-1])
        return int(match.group()) if match else 0
        
    mw_cols.sort(key=get_col_num)
    price_cols.sort(key=get_col_num)
    
    limit_col = None
    if limit_keyword:
        limit_cols = [c for c in df.columns if limit_keyword.lower() in c.lower()]
        if limit_cols:
            limit_col = limit_cols[0]
            # THE FIX: If ERCOT leaves HSL blank, it means the plant has 0 dispatchable limit!
            df[limit_col] = pd.to_numeric(df[limit_col].astype(str).str.replace(',', ''), errors='coerce').fillna(0)

    parsed_data = []
    prev_mw_col = None
    
    for mw_col, price_col in zip(mw_cols, price_cols):
        if mw_col in df.columns and price_col in df.columns:
            temp_df = df[[price_col, mw_col]].copy()
            temp_df.columns = ['Price', 'Raw_MW']
            
            temp_df['Raw_MW'] = pd.to_numeric(temp_df['Raw_MW'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
            temp_df['Price'] = pd.to_numeric(temp_df['Price'].astype(str).str.replace(',', ''), errors='coerce')
            
            if limit_col:
                temp_df['Raw_MW'] = pd.concat([temp_df['Raw_MW'], df[limit_col]], axis=1).min(axis=1)
            
            if is_cumulative and prev_mw_col is not None:
                prev_mw_raw = pd.to_numeric(df[prev_mw_col].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
                if limit_col:
                    prev_mw = pd.concat([prev_mw_raw, df[limit_col]], axis=1).min(axis=1)
                else:
                    prev_mw = prev_mw_raw
                    
                temp_df['MW'] = temp_df['Raw_MW'] - prev_mw
            else:
                temp_df['MW'] = temp_df['Raw_MW']
                
            temp_df = temp_df.dropna(subset=['Price'])
            temp_df = temp_df[temp_df['MW'] > 0]
            
            parsed_data.append(temp_df[['Price', 'MW']])
            prev_mw_col = mw_col
            
    if not parsed_data:
        return pd.DataFrame(columns=['Price', 'MW'])
        
    return pd.concat(parsed_data, ignore_index=True)

def clean_and_filter(df, target_date, target_hour):
    df.columns = df.columns.str.strip()
    df['Delivery Date'] = pd.to_datetime(df['Delivery Date'])
    df['Hour Ending'] = pd.to_numeric(df['Hour Ending'], errors='coerce')
    return df[(df['Delivery Date'] == pd.to_datetime(target_date)) & (df['Hour Ending'] == target_hour)]

# ==========================================
# 3. BUILD SCED CURVES
# ==========================================
def plot_sced():
    print(f"\n--- Processing SCED {TARGET_SCED_TIMESTAMP} ---")
    target_minute_str = TARGET_SCED_TIMESTAMP[:16] 
    
    eoc_df = pd.read_csv(FILE_SCED_EOC)
    eoc_df.columns = eoc_df.columns.str.strip()
    
    time_col = next((col for col in eoc_df.columns if 'SCED Time' in col or 'Timestamp' in col), None)
    if time_col is None:
        print("   -> ERROR: Could not find a Timestamp column.")
        return
        
    minute_df = eoc_df[eoc_df[time_col].astype(str).str.startswith(target_minute_str)].copy()
    if minute_df.empty:
        print("   -> ERROR: No data found for this minute.")
        return
        
    exact_timestamp = minute_df[time_col].iloc[0]
    print(f"   [Locked onto exact SCED run: {exact_timestamp}]")
    eoc_df = minute_df[minute_df[time_col] == exact_timestamp].copy()
    
    # THE FIX: Hard filter to drop purely offline statuses BEFORE math happens
    status_col = next((col for col in eoc_df.columns if 'Resource Status' in col), None)
    if status_col:
        # We drop OFF, OUT, and EMR (Emergency)
        eoc_df = eoc_df[~eoc_df[status_col].astype(str).str.upper().str.contains(r'OFF|OUT|EMR')]
        print(f"   [Filtered offline units. Remaining units to plot: {len(eoc_df)}]")

    sced_supply = parse_ercot_curve(eoc_df, mw_keyword='SCED1 Curve-MW', price_keyword='SCED1 Curve-Price', is_cumulative=True, limit_keyword='Telemetered HSL')
    sced_supply = sced_supply.sort_values(by='Price', ascending=True)
    sced_supply['Cumulative_MW'] = sced_supply['MW'].cumsum()
    
    sced_gen_df = eoc_df.copy() 
    col_name = 'Telemetered Net Output'
    
    if col_name in sced_gen_df.columns:
        sced_gen_df[col_name] = pd.to_numeric(sced_gen_df[col_name].astype(str).str.replace(',', ''), errors='coerce')
        total_system_demand = sced_gen_df[col_name].sum(skipna=True)
    else:
        total_system_demand = 0
        
    print(f"   Calculated System Demand: {total_system_demand:,.0f} MW")

    if len(sced_supply) == 0:
        print("   -> ABORTING SCED PLOT: No supply data survived the filters.")
        return

    plt.figure(figsize=(12, 7))
    plt.step(sced_supply['Cumulative_MW'], sced_supply['Price'], where='post', label='SCED Supply (EOCs)', color='#1f77b4', linewidth=2)
    if total_system_demand > 0:
        plt.axvline(x=total_system_demand, color='#d62728', linewidth=2, label=f'System Demand ({total_system_demand:,.0f} MW)')
        
    plt.title(f'ERCOT SCED Aggregate Curve - {exact_timestamp}', fontsize=14, fontweight='bold')
    plt.xlabel('Cumulative Quantity (MW)', fontsize=12)
    plt.ylabel('Price ($/MWh)', fontsize=12)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend(fontsize=11)
    
    if total_system_demand > 0 and len(sced_supply) > 0:
        clearing_row = sced_supply[sced_supply['Cumulative_MW'] >= total_system_demand]
        if not clearing_row.empty:
            sced_price = clearing_row['Price'].iloc[0]
            print(f"   => ACTUAL SCED CLEARING: {total_system_demand:,.0f} MW at ${sced_price:,.2f} / MWh")
            
            sced_text = f"Clearing Quantity: {total_system_demand:,.0f} MW\nClearing Price: ${sced_price:,.2f} / MWh"
            bbox_props = dict(boxstyle="round,pad=0.5", fc="white", ec="gray", lw=1.5, alpha=0.9)
            plt.gca().text(0.50, 0.50, sced_text, transform=plt.gca().transAxes, fontsize=12,
                           verticalalignment='center', bbox=bbox_props, fontweight='bold')

    plt.tight_layout()
    plt.savefig(f'SCED_Curve_HE{TARGET_HOUR}.png', dpi=300, bbox_inches='tight')
    plt.show()

# ==========================================
# 4. BUILD DAM CURVES
# ==========================================
def plot_dam():
    print(f"\n--- PROCESSING DAM {TARGET_DATE} HE {TARGET_HOUR} ---")
    
    bids_df = pd.read_csv(FILE_DAM_BIDS)
    bids_filtered = clean_and_filter(bids_df, TARGET_DATE, TARGET_HOUR)
    dam_demand = parse_ercot_curve(bids_filtered, mw_keyword='Bid MW', price_keyword='Price', is_cumulative=True)
    
    eo_offers_df = pd.read_csv(FILE_DAM_OFFERS)
    eo_filtered = clean_and_filter(eo_offers_df, TARGET_DATE, TARGET_HOUR)
    dam_supply_eo = parse_ercot_curve(eo_filtered, mw_keyword='Offer MW', price_keyword='Price', is_cumulative=True)
    
    gen_offers_df = pd.read_csv(FILE_DAM_GEN)
    gen_filtered = clean_and_filter(gen_offers_df, TARGET_DATE, TARGET_HOUR)
    dam_supply_gen = parse_ercot_curve(gen_filtered, mw_keyword='Curve-MW', price_keyword='Curve-Price', is_cumulative=True)
    if len(dam_supply_gen) == 0:
        dam_supply_gen = parse_ercot_curve(gen_filtered, mw_keyword='Curve MW', price_keyword='Curve Price', is_cumulative=True)
    
    if not dam_supply_gen.empty and not dam_supply_eo.empty:
        dam_supply = pd.concat([dam_supply_eo, dam_supply_gen], ignore_index=True)
    elif not dam_supply_gen.empty:
        dam_supply = dam_supply_gen
    else:
        dam_supply = dam_supply_eo
        
    if len(dam_supply) == 0 and len(dam_demand) == 0:
        print("   -> ABORTING DAM PLOT: No data left to plot.")
        return

    dam_demand = dam_demand.sort_values(by='Price', ascending=False)
    dam_demand['Cumulative_MW'] = dam_demand['MW'].cumsum()
    dam_supply = dam_supply.sort_values(by='Price', ascending=True)
    dam_supply['Cumulative_MW'] = dam_supply['MW'].cumsum()

    print("   [Calculating DAM intersection...]")
    all_prices = sorted(list(set(dam_supply['Price']).union(set(dam_demand['Price']))))
    dam_clearing_price = None
    dam_clearing_mw = None
    
    for p in all_prices:
        s_mw = dam_supply[dam_supply['Price'] <= p]['MW'].sum()
        d_mw = dam_demand[dam_demand['Price'] >= p]['MW'].sum()
        if s_mw >= d_mw:
            dam_clearing_price = p
            dam_clearing_mw = d_mw 
            break
            
    plt.figure(figsize=(12, 7))
    
    if len(dam_supply) > 0:
        x_sup = [0] + dam_supply['Cumulative_MW'].tolist()
        y_sup = [dam_supply['Price'].iloc[0]] + dam_supply['Price'].tolist()
        plt.step(x_sup, y_sup, where='pre', label='Aggregate Supply (Offers)', color='#1f77b4', linewidth=2)
        
    if len(dam_demand) > 0:
        x_dem = [0] + dam_demand['Cumulative_MW'].tolist()
        y_dem = [dam_demand['Price'].iloc[0]] + dam_demand['Price'].tolist()
        plt.step(x_dem, y_dem, where='pre', label='Aggregate Demand (Bids)', color='#d62728', linewidth=2)
    
    plt.title(f'ERCOT DAM Aggregate Curves - {TARGET_DATE} Hour Ending {TARGET_HOUR}', fontsize=14, fontweight='bold')
    plt.xlabel('Cumulative Quantity (MW)', fontsize=12)
    plt.ylabel('Price ($/MWh)', fontsize=12)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend(fontsize=11)
    
    if dam_clearing_price is not None:
        print(f"   => ACTUAL DAM CLEARING: {dam_clearing_mw:,.0f} MW at ${dam_clearing_price:,.2f} / MWh")
        
        dam_text = f"Clearing Quantity: {dam_clearing_mw:,.0f} MW\nClearing Price: ${dam_clearing_price:,.2f} / MWh"
        bbox_props = dict(boxstyle="round,pad=0.5", fc="white", ec="gray", lw=1.5, alpha=0.9)
        plt.gca().text(0.50, 0.50, dam_text, transform=plt.gca().transAxes, fontsize=12,
                       verticalalignment='center', bbox=bbox_props, fontweight='bold')

    plt.tight_layout()
    plt.savefig(f'DAM_Curve_HE{TARGET_HOUR}.png', dpi=300, bbox_inches='tight')
    plt.show()

# ==========================================
# 5. EXECUTE
# ==========================================
if __name__ == "__main__":
    plot_sced()
    plot_dam()