import gridstatus

def check_ercot_columns():
    iso = gridstatus.Ercot()
    print("Fetching a single day of data to check column names...")
    
    # Fetch just one day (Jan 1, 2025) so it runs in seconds
    sced_dict = iso.get_60_day_sced_disclosure(date="2025-01-01")
    
    # Find the generation table key
    gen_key = None
    for key in sced_dict.keys():
        if 'gen' in key.lower() and 'resource' in key.lower() and 'load' not in key.lower():
            gen_key = key
            break
            
    if gen_key:
        df = sced_dict[gen_key]
        print("\nSUCCESS! Here are the exact column names ERCOT is using:")
        print(df.columns.tolist())
    else:
        print("Could not find the generation table.")

if __name__ == "__main__":
    check_ercot_columns()