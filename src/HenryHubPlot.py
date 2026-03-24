import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# Data extracted from your text
data = [
    ("MAR 2026", 3.159), ("APR 2026", 3.076), ("MAY 2026", 3.093), ("JUN 2026", 3.265),
    ("JUL 2026", 3.535), ("AUG 2026", 3.604), ("SEP 2026", 3.583), ("OCT 2026", 3.646),
    ("NOV 2026", 3.920), ("DEC 2026", 4.523), ("JAN 2027", 4.868), ("FEB 2027", 4.332),
    ("MAR 2027", 3.560), ("APR 2027", 3.239), ("MAY 2027", 3.226), ("JUN 2027", 3.354),
    ("JUL 2027", 3.528), ("AUG 2027", 3.581), ("SEP 2027", 3.558), ("OCT 2027", 3.627),
    ("NOV 2027", 3.867), ("DEC 2027", 4.454), ("JAN 2028", 4.808), ("FEB 2028", 4.229),
    ("MAR 2028", 3.482), ("APR 2028", 3.104), ("MAY 2028", 3.089), ("JUN 2028", 3.217),
    ("JUL 2028", 3.384), ("AUG 2028", 3.441), ("SEP 2028", 3.425), ("OCT 2028", 3.495),
    ("NOV 2028", 3.739), ("DEC 2028", 4.287), ("JAN 2029", 4.608), ("FEB 2029", 4.065),
    ("MAR 2029", 3.379), ("APR 2029", 3.089), ("MAY 2029", 3.076), ("JUN 2029", 3.228),
    ("JUL 2029", 3.407), ("AUG 2029", 3.477), ("SEP 2029", 3.467), ("OCT 2029", 3.534),
    ("NOV 2029", 3.741), ("DEC 2029", 4.253), ("JAN 2030", 4.566), ("FEB 2030", 4.206),
    ("MAR 2030", 3.582), ("APR 2030", 3.132), ("MAY 2030", 3.105), ("JUN 2030", 3.249),
    ("JUL 2030", 3.419), ("AUG 2030", 3.497), ("SEP 2030", 3.496), ("OCT 2030", 3.574),
    ("NOV 2030", 3.807), ("DEC 2030", 4.303)
]

# Separate data
dates = [datetime.strptime(d[0], "%b %Y") for d in data]
prices = [d[1] for d in data]

# Create the plot
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(dates, prices, marker='o', linestyle='-', markersize=4, label='Prior Settle Price')

# --- Formatting the X-Axis (Years Only) ---
# Locate every year (defaults to Jan 1st)
ax.xaxis.set_major_locator(mdates.YearLocator())
# Format label as just the year number (e.g., "2027")
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

# Optional: Add padding to x-axis so '2026' and '2031' labels are visible/clean
ax.set_xlim(datetime(2026, 1, 1), datetime(2031, 1, 1))

# Labels and Title
plt.title('CME Henry Hub Natural Gas Futures (2026 - 2030)', fontsize=14)
plt.ylabel('Price ($/MMBtu)', fontsize=12)
plt.xlabel('Year', fontsize=12)

# Grid lines will now align vertically with the January/Year marks
plt.grid(True, linestyle='--', alpha=0.7)

plt.tight_layout()
plt.show()