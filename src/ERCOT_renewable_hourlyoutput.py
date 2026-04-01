import pandas as pd
import gridstatus
from dateutil.relativedelta import relativedelta
import gc  # Used to forcefully free up RAM

def build_annual_ercot_sced_matrix(start_date="2025-01-01", end_date="2025-12-31", output_csv="ercot_hourly_output_2025.csv", target_csv="target_ercot_renewables.csv"):
    
    # --- 1. Load your target list of Wind and Solar units ---
    print("Loading target renewables list...")
    try:
        targets_df = pd.read_csv(target_csv)
        # Convert to a clean list and strip any accidental spaces
        target_units = targets_df['Resource Name'].astype(str).str.strip().tolist()
        print(f"Loaded {len(target_units)} target wind and solar units to filter by.")
    except FileNotFoundError:
        print(f"ERROR: Could not find '{target_csv}'. Please check the path and try again!")
        return
    # ---------------------------------------------------------

    iso = gridstatus.Ercot()
    
    current_date = pd.to_datetime(start_date)
    end_dt = pd.to_datetime(end_date)
    
    hourly_master_list = []

    print("Starting data extraction and aggregation...")
    
    # Loop through month-by-month to manage memory
    # Loop through in 3-day chunks to prevent Mac memory crashes
    while current_date <= end_dt:
        next_chunk = current_date + pd.Timedelta(days=2)
        if next_chunk > end_dt:
            next_chunk = end_dt
            
        start_str = current_date.strftime('%Y-%m-%d')
        end_str = next_chunk.strftime('%Y-%m-%d')
        print(f"Fetching data for {start_str} to {end_str}...")

        # Fetch the 60-Day SCED Disclosure dictionary
        sced_dict = iso.get_60_day_sced_disclosure(date=start_str, end=end_str)
        
        # Dynamically find the Generation Resource Data table key
        gen_key = None
        for key in sced_dict.keys():
            if 'gen' in key.lower() and 'resource' in key.lower() and 'load' not in key.lower():
                gen_key = key
                break
        
        if gen_key is None:
            raise KeyError("Could not automatically find the Generation Resource Data table in the ZIP.")
        
        df = sced_dict[gen_key]
        
        # Strip invisible trailing/leading spaces from ERCOT's column names
        df.columns = df.columns.str.strip()
        
        # Use the exact column names we found
        t_col = 'SCED Timestamp'
        r_col = 'Resource Name'
        out_col = 'Telemetered Net Output'
        
        cols_to_keep = [t_col, r_col, out_col]
        df = df[cols_to_keep].copy()
        
        # --- 2. FILTERING FOR MEMORY SAVING ---
        # Strip spaces from ERCOT's resource names to ensure a perfect match
        df[r_col] = df[r_col].astype(str).str.strip()
        
        # Instantly delete any rows where the Resource Name is NOT in your CSV list
        df = df[df[r_col].isin(target_units)]
        # ---------------------------------------
        
        # Convert timestamp to a proper datetime object and floor to the hour
        df[t_col] = pd.to_datetime(df[t_col])
        df['Hour'] = df[t_col].dt.floor('h')
        
        # Force the output to be numeric, just in case ERCOT included blank text strings
        df[out_col] = pd.to_numeric(df[out_col], errors='coerce')
        
        # Aggregate 5-minute telemetry to hourly average (True MWh)
        hourly_df = df.groupby(['Hour', r_col])[out_col].mean().reset_index()
        hourly_master_list.append(hourly_df)
        
        # Move to the next chunk
        current_date = next_chunk + pd.Timedelta(days=1)
        
        # --- 3. FORCE MEMORY CLEANUP ---
        # Delete the massive raw dictionaries and dataframes for this month
        del sced_dict
        del df
        # Force the computer to immediately empty the trash and free up RAM
        gc.collect() 
        # --------------------------------

    print("Concatenating monthly data...")
    # Combine all months into one large DataFrame
    full_hourly = pd.concat(hourly_master_list, ignore_index=True)
    
    print("Pivoting data to final matrix format...")
    # Pivot: Rows = Hour, Columns = Resource Name
    final_matrix = full_hourly.pivot(index='Hour', columns='Resource Name', values='Telemetered Net Output')
    
    print(f"Saving to {output_csv}...")
    final_matrix.to_csv(output_csv)
    print("Done!")

if __name__ == "__main__":
    # Point the target_csv directly to the file you just created
    build_annual_ercot_sced_matrix(
        target_csv="/Users/dannysalingerbrown/Desktop/Energy-Graphs-Misc/data/target_ercot_renewables.csv",
        output_csv="/Users/dannysalingerbrown/Desktop/Energy-Graphs-Misc/src/ercot_hourly_output_2025.csv"
    )