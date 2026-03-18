import pandas as pd
import matplotlib.pyplot as plt
import re

# ==========================================
# 1. CONFIGURATION: Set your targets and files
# ==========================================
# You can use any standard date format here now, the script will translate it!
TARGET_DATE = '1/15/2026'  
TARGET_HOUR = 8  
TARGET_SCED_TIMESTAMP = '01/15/2026 07:55:00' 

# DAM File Names
FILE_DAM_BIDS = '/Users/dannysalingerbrown/Downloads/March16DAM_60Day/60d_DAM_EnergyBids-16-MAR-26.csv'
FILE_DAM_OFFERS = '/Users/dannysalingerbrown/Downloads/March16DAM_60Day/60d_DAM_EnergyOnlyOffers-16-MAR-26.csv'
FILE_DAM_GEN = '/Users/dannysalingerbrown/Downloads/March16DAM_60Day/60d_DAM_Gen_Resource_Data-16-MAR-26.csv'

# SCED File Names
FILE_SCED_EOC = '/Users/dannysalingerbrown/Downloads/March16SCED_60Day/60d_SCED_Resource_AS_OFFERS-16-MAR-26.csv' 
FILE_SCED_GEN = '/Users/dannysalingerbrown/Downloads/March16SCED_60Day/60d_SCED_Gen_Resource_Data-16-MAR-26.csv'

# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================
def parse_ercot_curve(df, mw_keyword, price_keyword):
    """Finds paired MW and Price columns and extracts the data."""
    mw_cols = [c for c in df.columns if mw_keyword in c]
    price_cols = [c for c in df.columns if price_keyword in c]
    
    def get_col_num(name):
        match = re.search(r'\d+', name)
        return int(match.group()) if match else 0
        
    mw_cols.sort(key=get_col_num)
    price_cols.sort(key=get_col_num)
    
    parsed_data = []
    for mw_col, price_col in zip(mw_cols, price_cols):
        temp_df = df[[price_col, mw_col]].dropna()
        temp_df.columns = ['Price', 'MW']
        temp_df = temp_df[temp_df['MW'] > 0]
        parsed_data.append(temp_df)
        
    if not parsed_data:
        return pd.DataFrame(columns=['Price', 'MW'])
        
    return pd.concat(parsed_data, ignore_index=True)

def clean_and_filter(df, target_date, target_hour):
    """Bulletproofs the Date and Hour columns before filtering."""
    # Strip any hidden spaces in column headers
    df.columns = df.columns.str.strip()
    
    # Force official formats
    df['Delivery Date'] = pd.to_datetime(df['Delivery Date'])
    df['Hour Ending'] = pd.to_numeric(df['Hour Ending'], errors='coerce')
    
    # Filter
    return df[(df['Delivery Date'] == pd.to_datetime(target_date)) & (df['Hour Ending'] == target_hour)]

# ==========================================
# 3. BUILD DAM CURVES
# ==========================================
def plot_dam():
    print(f"\n--- DIAGNOSTICS FOR {TARGET_DATE} HE {TARGET_HOUR} ---")
    
    # --- DEMAND (BIDS) ---
    print("\n1. Loading Bids File...")
    bids_df = pd.read_csv(FILE_DAM_BIDS)
    bids_filtered = clean_and_filter(bids_df, TARGET_DATE, TARGET_HOUR)
    print(f"   Rows surviving robust filter: {len(bids_filtered)}")
    dam_demand = parse_ercot_curve(bids_filtered, mw_keyword='Bid MW', price_keyword='Price')
    
    # --- SUPPLY (OFFERS - Energy Only) ---
    print("\n2. Loading Energy Only Offers File...")
    eo_offers_df = pd.read_csv(FILE_DAM_OFFERS)
    eo_filtered = clean_and_filter(eo_offers_df, TARGET_DATE, TARGET_HOUR)
    print(f"   Rows surviving robust filter: {len(eo_filtered)}")
    dam_supply_eo = parse_ercot_curve(eo_filtered, mw_keyword='Offer MW', price_keyword='Price')
    
    # --- SUPPLY (OFFERS - Generation) ---
    print("\n3. Loading Gen Resource Offers File...")
    gen_offers_df = pd.read_csv(FILE_DAM_GEN)
    gen_filtered = clean_and_filter(gen_offers_df, TARGET_DATE, TARGET_HOUR)
    print(f"   Rows surviving robust filter: {len(gen_filtered)}")
    dam_supply_gen = parse_ercot_curve(gen_filtered, mw_keyword='Curve MW', price_keyword='Curve Price')
    
    # --- COMBINE & PLOT ---
    print("\n4. Final Plotting Phase...")
    dam_supply = pd.concat([dam_supply_eo, dam_supply_gen], ignore_index=True)
    print(f"   Total Supply points to plot: {len(dam_supply)}")
    print(f"   Total Demand points to plot: {len(dam_demand)}")
    
    if len(dam_supply) == 0 and len(dam_demand) == 0:
        print("   -> ABORTING PLOT: No data left to plot.")
        return

    # Sort and calculate cumulative sum
    dam_demand = dam_demand.sort_values(by='Price', ascending=False)
    dam_demand['Cumulative_MW'] = dam_demand['MW'].cumsum()
    
    dam_supply = dam_supply.sort_values(by='Price', ascending=True)
    dam_supply['Cumulative_MW'] = dam_supply['MW'].cumsum()

    # Create the Plot
    plt.figure(figsize=(12, 7))
    if len(dam_supply) > 0:
        plt.step(dam_supply['Cumulative_MW'], dam_supply['Price'], where='post', label='Aggregate Supply (Offers)', color='#1f77b4', linewidth=2)
    if len(dam_demand) > 0:
        plt.step(dam_demand['Cumulative_MW'], dam_demand['Price'], where='post', label='Aggregate Demand (Bids)', color='#d62728', linewidth=2)
    
    plt.title(f'ERCOT DAM Aggregate Curves - {TARGET_DATE} Hour Ending {TARGET_HOUR}', fontsize=14, fontweight='bold')
    plt.xlabel('Cumulative Quantity (MW)', fontsize=12)
    plt.ylabel('Price ($/MWh)', fontsize=12)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend(fontsize=11)
    plt.tight_layout()
    plt.show()

# ==========================================
# 4. BUILD SCED CURVES
# ==========================================
def plot_sced():
    print(f"\nProcessing SCED Data for {TARGET_SCED_TIMESTAMP}...")
    
    # Force our target timestamp into a bulletproof datetime object
    target_dt = pd.to_datetime(TARGET_SCED_TIMESTAMP)
    
    # --- SCED SUPPLY ---
    print("1. Loading SCED EOC File...")
    eoc_df = pd.read_csv(FILE_SCED_EOC)
    
    # Strip hidden spaces from headers 
    eoc_df.columns = eoc_df.columns.str.strip()
    
    # Safely find the timestamp column
    time_col = None
    for col in eoc_df.columns:
        if 'SCED Time' in col or 'Timestamp' in col:
            time_col = col
            break
            
    if time_col is None:
        print(f"   -> ERROR: Could not find a Timestamp column. Headers found: {eoc_df.columns.tolist()[:5]}...")
        return
        
    # BULLETPROOF FILTER: Convert the whole column to datetime before filtering
    eoc_df[time_col] = pd.to_datetime(eoc_df[time_col], errors='coerce')
    eoc_df = eoc_df[eoc_df[time_col] == target_dt]
    print(f"   Rows surviving timestamp filter: {len(eoc_df)}")
    
    sced_supply = parse_ercot_curve(eoc_df, mw_keyword='Curve MW', price_keyword='Curve Price')
    sced_supply = sced_supply.sort_values(by='Price', ascending=True)
    sced_supply['Cumulative_MW'] = sced_supply['MW'].cumsum()
    print(f"   Valid SCED Supply points extracted: {len(sced_supply)}")
    
    # --- SCED DEMAND ---
    print("\n2. Loading SCED Generation File for Demand Line...")
    sced_gen_df = pd.read_csv(FILE_SCED_GEN)
    sced_gen_df.columns = sced_gen_df.columns.str.strip()
    
    # Use the safe time column finder here too
    gen_time_col = None
    for col in sced_gen_df.columns:
        if 'SCED Time' in col or 'Timestamp' in col:
            gen_time_col = col
            break
            
    if gen_time_col:
        sced_gen_df[gen_time_col] = pd.to_datetime(sced_gen_df[gen_time_col], errors='coerce')
        sced_gen_df = sced_gen_df[sced_gen_df[gen_time_col] == target_dt]
    
    # Find the telemetry column
    col_name = None
    if 'Telemetered Net Output' in sced_gen_df.columns:
        col_name = 'Telemetered Net Output'
    else:
        match = sced_gen_df.columns[sced_gen_df.columns.str.contains('Telemetered|Net Output', case=False)]
        if len(match) > 0:
            col_name = match[0]
            
    total_system_demand = sced_gen_df[col_name].sum() if col_name else 0
    print(f"   Calculated System Demand: {total_system_demand:,.0f} MW")
    
    if len(sced_supply) == 0:
        print("   -> ABORTING SCED PLOT: No supply data survived the filters.")
        return

    # --- PLOT SCED ---
    print("\n3. Plotting SCED...")
    plt.figure(figsize=(12, 7))
    plt.step(sced_supply['Cumulative_MW'], sced_supply['Price'], where='post', label='SCED Supply (EOCs)', color='#1f77b4', linewidth=2)
    
    if total_system_demand > 0:
        plt.axvline(x=total_system_demand, color='#d62728', linewidth=2, label=f'System Demand ({total_system_demand:,.0f} MW)')
    
    plt.title(f'ERCOT SCED Aggregate Curve - {TARGET_SCED_TIMESTAMP}', fontsize=14, fontweight='bold')
    plt.xlabel('Cumulative Quantity (MW)', fontsize=12)
    plt.ylabel('Price ($/MWh)', fontsize=12)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend(fontsize=11)
    plt.tight_layout()
    plt.show()
# ==========================================
# 5. EXECUTE
# ==========================================
if __name__ == "__main__":
    plot_dam()
    # plot_sced()