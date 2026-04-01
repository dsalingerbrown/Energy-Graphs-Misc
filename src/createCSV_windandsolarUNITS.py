import pandas as pd

def extract_renewables_from_cdr(cdr_filename="ERCOT_CDR_Report.xlsx", output_csv="target_ercot_renewables.csv"):
    print(f"Loading {cdr_filename}...")
    
    try:
        # 1. Read the raw Excel sheet specifically targeting 'Unit Details'
        # We set header=None initially so we can hunt for the true header row
        df_raw = pd.read_excel(cdr_filename, sheet_name="Unit Details", header=None)
        
        # 2. Hunt for the true header row
        header_row_idx = -1
        for index, row in df_raw.iterrows():
            # Convert the entire row to an uppercase string to check its contents
            row_string = " ".join(row.dropna().astype(str)).upper()
            if "UNIT CODE" in row_string and "FUEL" in row_string:
                header_row_idx = index
                break
                
        if header_row_idx == -1:
            raise KeyError("Scanned the 'Unit Details' sheet but could not find a row containing 'UNIT CODE' and 'FUEL'.")
            
        print(f"  -> Found headers on Excel row {header_row_idx + 1}. Processing data...")
        
        # 3. Re-load the dataframe using the correct row as the header
        df = pd.read_excel(cdr_filename, sheet_name="Unit Details", header=header_row_idx)
        
        # Clean up the column names
        df.columns = df.columns.str.strip().str.upper()
        
        # Clean the FUEL column and handle empty cells
        df['FUEL_CLEAN'] = df['FUEL'].astype(str).str.strip().str.upper()
        
        # 4. Filter for rows where the fuel type contains WIND or SOLAR
        renewables_df = df[df['FUEL_CLEAN'].str.contains('WIND|SOLAR', na=False)]
        
        # Extract the UNIT CODE column
        target_units = renewables_df[['UNIT CODE']].copy()
        
        # Rename to match the SCED aggregation script
        target_units.rename(columns={'UNIT CODE': 'Resource Name'}, inplace=True)
        
        # Clean the resource names and remove duplicates
        target_units['Resource Name'] = target_units['Resource Name'].astype(str).str.strip()
        target_units.drop_duplicates(inplace=True)
        
        # 5. Save to CSV
        target_units.to_csv(output_csv, index=False)
        print(f"Success! Found {len(target_units)} unique Wind and Solar units.")
        print(f"Saved to '{output_csv}'. You can now run your main SCED aggregation script.")

    except ValueError as ve:
        print(f"ERROR: {ve} (Make sure the tab is actually named 'Unit Details')")
    except FileNotFoundError:
        print(f"ERROR: Could not find the file '{cdr_filename}'.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Pointing exactly to your file
    extract_renewables_from_cdr(cdr_filename="/Users/dannysalingerbrown/Desktop/Energy-Graphs-Misc/data/CapacityDemandandReservesReport_December2025.xlsx")