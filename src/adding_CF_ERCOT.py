import pandas as pd
import numpy as np

def format_final_matrices(mw_csv, cdr_excel, output_mw="ercot_MW_Matrix.csv", output_cf="ercot_CF_Matrix.csv"):
    print("Loading the raw 40-minute MW matrix...")
    df_mw = pd.read_csv(mw_csv, index_col='Hour')

    # --- THE NUCLEAR SCRUBBER ---
    # 1. Clean the column names (Headers)
    df_mw.columns = [str(c).replace("'", "").strip() for c in df_mw.columns]

    # 2. Clean the ACTUAL DATA inside the matrix
    # This rips out hidden apostrophes and commas inside the numbers
    df_mw = df_mw.replace({"'": "", ",": ""}, regex=True)
    
    # 3. Force everything to be a pure math number
    df_mw = df_mw.apply(pd.to_numeric, errors='coerce')
    # ----------------------------

    print("Hunting for Rated Capacities in the CDR report...")
    df_raw = pd.read_excel(cdr_excel, sheet_name="Unit Details", header=None)
    header_idx = -1
    for i, row in df_raw.iterrows():
        row_str = " ".join(row.dropna().astype(str)).upper()
        if "UNIT CODE" in row_str and "INSTALLED CAPACITY" in row_str:
            header_idx = i
            break

    if header_idx == -1:
        print("ERROR: Could not find the capacity column in the Excel sheet.")
        return

    df_cdr = pd.read_excel(cdr_excel, sheet_name="Unit Details", header=header_idx)
    df_cdr.columns = df_cdr.columns.astype(str).str.strip().str.upper()

    cap_col = [col for col in df_cdr.columns if 'INSTALLED CAPACITY' in col][0]
    
    # Clean CDR unit codes
    df_cdr['UNIT CODE'] = df_cdr['UNIT CODE'].astype(str).str.replace("'", "", regex=False).str.strip()
    
    capacity_dict = dict(zip(df_cdr['UNIT CODE'], pd.to_numeric(df_cdr[cap_col], errors='coerce')))

    capacities = [capacity_dict.get(col, np.nan) for col in df_mw.columns]

    print("Calculating Hourly Capacity Factors [0, 1]...")
    df_cf = df_mw / capacities
    df_cf = df_cf.clip(lower=0.0, upper=1.0)

    print("Adding Rated Capacity to the top row...")
    df_cap_row = pd.DataFrame([capacities], columns=df_mw.columns, index=['RATED_CAPACITY_MW'])

    final_mw = pd.concat([df_cap_row, df_mw])
    final_cf = pd.concat([df_cap_row, df_cf])

    print(f"Saving to {output_mw} and {output_cf}...")
    # --- STRICT CSV FORMATTING ---
    # float_format forces standard periods for decimals and sets decimal places
    final_mw.to_csv(output_mw, float_format='%.2f')
    final_cf.to_csv(output_cf, float_format='%.4f')
    print("Done! Your data is completely scrubbed, numeric, and ready for R.")

if __name__ == "__main__":
    format_final_matrices(
        mw_csv="/Users/dannysalingerbrown/Desktop/Energy-Graphs-Misc/data/ercot_hourly_output_2025.csv",
        cdr_excel="/Users/dannysalingerbrown/Desktop/Energy-Graphs-Misc/data/CapacityDemandandReservesReport_December2025.xlsx",
        output_mw="/Users/dannysalingerbrown/Desktop/Energy-Graphs-Misc/data/ercot_MW_Matrix.csv",
        output_cf="/Users/dannysalingerbrown/Desktop/Energy-Graphs-Misc/data/ercot_CF_Matrix.csv"
    )