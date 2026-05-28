import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 1. Set up our time window (Full year of 2025)
start_date = datetime(2025, 1, 1, 0, 0)
hours_in_year = 365 * 24

# Create a list of every single hour in the year
timestamps = [start_date + timedelta(hours=i) for i in range(hours_in_year)]

# 2. Let's create the ingredients for our recipe
data = []

# Setting a random seed so we get the same results every time
np.random.seed(42)

for dt in timestamps:
    # Extract time features
    hour = dt.hour
    month = dt.month
    day_of_week = dt.weekday() # 0 is Monday, 6 is Sunday
    is_weekend = 1 if day_of_week >= 5 else 0
    
    # Simulate Delhi Temperature (°C) based on the month
    # Summer months (May=5, June=6, July=7) are hot. Winter months are cold.
    if month in [5, 6, 7]:
        base_temp = 35
    elif month in [11, 12, 1]:
        base_temp = 15
    else:
        base_temp = 25
    
    # Temperature varies slightly during the day (hotter at 2 PM, cooler at 4 AM)
    hourly_temp_variation = 5 * np.sin((hour - 6) * np.pi / 12)
    temperature = base_temp + hourly_temp_variation + np.random.normal(0, 2)
    
    # 3. Calculate Power Consumption (in kWh)
    power = 100 # The baseline power of the campus
    
    # Add power if it's a working class hour (9 AM to 5 PM) on a weekday
    if 9 <= hour <= 17 and not is_weekend:
        power += 150
    elif 18 <= hour <= 22: # Evening hostel use
        power += 80
        
    # Add massive AC power if temperature is high
    if temperature > 30:
        power += (temperature - 30) * 15 # The hotter it gets, the more ACs work!
        
    # Drop power on weekends
    if is_weekend:
        power *= 0.7
        
    # Add a little bit of random noise (because real life isn't perfectly predictable)
    power += np.random.normal(0, 10)
    
    # Keep power above a reasonable minimum
    power = max(power, 40)
    
    # Save this hour's row of information
    data.append({
        "Timestamp": dt,
        "Hour": hour,
        "Month": month,
        "DayOfWeek": day_of_week,
        "IsWeekend": is_weekend,
        "Temperature": round(temperature, 1),
        "EnergyConsumption": round(power, 2)
    })

# 4. Turn our list into a beautiful Pandas DataFrame and save it as a CSV
df = pd.DataFrame(data)
df.to_csv("nit_delhi_campus_energy.csv", index=False)

print("🎉 Success! Your realistic dataset has been created and saved as 'nit_delhi_campus_energy.csv'!")
print(df.head()) # Show the first 5 rows