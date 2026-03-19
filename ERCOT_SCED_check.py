import pandas as pd

FILE_SCED = '/Users/dannysalingerbrown/Downloads/March16SCED_60Day/60d_SCED_Gen_Resource_Data-16-MAR-26.csv'
df = pd.read_csv(FILE_SCED, nrows=5)

print("\n--- HUNTING FOR THE DEMAND COLUMN ---")
# Print every column that ISN'T a curve or a timestamp
possible_cols = [c for c in df.columns if 'MW' not in c and 'Price' not in c and 'Time' not in c]
print(possible_cols)