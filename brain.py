import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
import joblib

# 1. Open the History Book
print("📖 Loading the campus energy dataset...")
df = pd.read_csv("nit_delhi_campus_energy.csv")

# 2. Separate the Clues (X) from the Answers (y)
X = df[["Hour", "Month", "DayOfWeek", "IsWeekend", "Temperature"]]
y = df["EnergyConsumption"]

# 3. Split into Study Data (80%) and Exam Data (20%)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Create the AI Brain (The Random Forest)
print("🤖 Teaching the AI brain patterns (this might take a few seconds)...")
brain = RandomForestRegressor(n_estimators=100, random_state=42)

# Start the studying process!
brain.fit(X_train, y_train)

# 5. Grade the Exam!
print("📝 Testing the AI brain with hidden questions...")
guesses = brain.predict(X_test)

# Calculate the average mistake size (Mean Absolute Error)
score = mean_absolute_error(y_test, guesses)
print(f"🎯 Exam Finished! On average, the AI's guesses are off by only {round(score, 2)} kWh!")

# 6. Save the Brain to a File (Like freezing its smart state)
joblib.dump(brain, "campus_energy_brain.pkl")
print("💾 Success! The trained brain has been saved as 'campus_energy_brain.pkl'.")