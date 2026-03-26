import pandas as pd
import re

# ==========================================
# 1. CONFIGURATION
# ==========================================
TARGET_SCED_TIMESTAMP = '01/15/2026 15:55:00'
FILE_SCED = '/Users/dannysalingerbrown/Desktop/Energy-Graphs-Misc/data/March16SCED_60Day/60d_SCED_Gen_Resource_Data-16-MAR-26.csv'

# ==========================================
# 2. RUN DIAGNOSTIC
# ==========================================
def run_diagnostic():
    print(f"\n--- RUNNING SCED DIAGNOSTIC FOR {TARGET_SCED_TIMESTAMP} ---")
    
    # Load the data
    df = pd.read_csv(FILE_SCED)
    df.columns = df.columns.str.strip()
    
    # Find the timestamp column
    time_col = next((col for col in df.columns if 'SCED Time' in col or 'Timestamp' in col), None)
    
    if not time_col:
        print("   -> ERROR: Could not find Timestamp column.")
        return
        
    # --- EXACT SECONDS LOCK-ON FIX ---
    target_minute_str = TARGET_SCED_TIMESTAMP[:16]
    minute_df = df[df[time_col].astype(str).str.startswith(target_minute_str)].copy()
    
    if minute_df.empty:
        print("   -> ERROR: No data found for this minute!")
        return
        
    # Extract the EXACT timestamp (with seconds) of the first SCED run in that minute
    exact_timestamp = minute_df[time_col].iloc[0]
    print(f"   [Locked onto exact SCED run: {exact_timestamp}]")
    
    # Filter strictly by that exact string
    df_filtered = minute_df[minute_df[time_col] == exact_timestamp].copy()
    # ---------------------------------

    # Grab the Resource Status
    status_col = next((col for col in df_filtered.columns if 'Resource Status' in col), 'Resource Status')
    
    # Dynamically hunt down the first Price and MW columns
    price_cols = [c for c in df_filtered.columns if 'sced1 curve-price' in c.lower()]
    mw_cols = [c for c in df_filtered.columns if 'sced1 curve-mw' in c.lower()]
    
    if not price_cols or not mw_cols:
        print("   -> ERROR: Could not find any Curve columns.")
        return
        
    def get_col_num(name):
        match = re.search(r'\d+', name.split('-')[-1])
        return int(match.group()) if match else 0
        
    price_cols.sort(key=get_col_num)
    mw_cols.sort(key=get_col_num)
    
    price_col = price_cols[0]
    mw_col = mw_cols[0]
    print(f"   [Found Target Columns: '{price_col}' and '{mw_col}']")

    # Clean the price and MW columns
    df_filtered['Price_1'] = pd.to_numeric(df_filtered[price_col].astype(str).str.replace(',', ''), errors='coerce')
    df_filtered['MW_1'] = pd.to_numeric(df_filtered[mw_col].astype(str).str.replace(',', ''), errors='coerce')
    
    # Drop empty rows
    df_valid = df_filtered.dropna(subset=['Price_1', 'MW_1'])

    # Isolate the deeply negative offers (The Wind/Solar PTC bids)
    negative_offers = df_valid[df_valid['Price_1'] <= -30].copy()
    
    print(f"Total Generators bidding at or below -$30/MWh: {len(negative_offers)}")
    print(f"Total Raw Capacity offered in this negative block: {negative_offers['MW_1'].sum():,.0f} MW")
    
    print("\n--- BREAKDOWN BY PHYSICAL RESOURCE STATUS ---")
    
    # Group by the status to see who is actually turned on vs turned off
    if status_col in df_valid.columns:
        breakdown = negative_offers.groupby(status_col)['MW_1'].sum().reset_index()
        breakdown = breakdown.sort_values(by='MW_1', ascending=False)
        
        for index, row in breakdown.iterrows():
            print(f"Status: {row[status_col]:<10} | Offered: {row['MW_1']:,.0f} MW")
    else:
        print("No status column found to group by.")

    print("\n---------------------------------------------------")
    print("If the total generator count drops significantly, the duplication bug is verified!")
    print("---------------------------------------------------\n")

# ==========================================
# 3. EXECUTE
# ==========================================
if __name__ == "__main__":
    run_diagnostic()