#  NIT Delhi Smart Grid: Cyber-Physical Energy Management System (EMS)

An enterprise-grade, data-driven Digital Twin and load forecasting application tailored specifically for the infrastructure assets of the National Institute of Technology, Delhi (NIT Delhi). The system utilizes an ensemble Machine Learning core to predict real-time electrical loads and flags grid anomalies based on localized environmental states and institutional schedules.

---

##  System Architecture & Logic Matrix

This application moves beyond standard predictive regression by embedding a **cyber-physical layer** directly over the AI inference engine. The system models seven distinct infrastructure nodes using custom-tailored load profiles and structural heuristics:

1. **Administrative Block:** Configured with a centralized HVAC footprint. Incorporates a baseline override dropping load parameters to a quiescent state (`0.15x`) on weekends and off-peak hours when core chillers deactivate.
2. **Academic Block:** Models a newly constructed facility tracking active professor cabins and library operations. Features a localized macro-modifier switch that simulates severe load surges (`+1.2x`) during mid-semester and end-semester examination blocks due to 24/7 student cramming sessions.
3. **Sagar Residency:** Tracks faculty housing (4 BHK complex) utilizing a domestic load profile that dynamically spikes during standard morning and evening residential hours.
4. **Hostel Infrastructure (Shivalik, Yamuna, Dhauladhar):** Implements a high-density residential matrix scaling consumption linearly against vertical building floors. Automatically transitions into low-occupancy states during standard lecture hours (`0.5x`) and surges during late-night cycles.
5. **Mini Campus:** Models lecture complex operations, enforcing an aggressive environmental conservation logic that cuts parasitic power draw down to base emergency levels when classes close.

---

##  Machine Learning Engine

* **Algorithm:** Ensemble Random Forest Regressor (100 parallel Decision Trees).
* **Feature Vector:** `[Hour, Month, DayOfWeek, IsWeekend, Temperature]`
* **Model Evaluation Metrics:** Mean Absolute Error (MAE) of **8.86 kWh** against test datasets.
* **Storage Optimization:** Leverages `joblib` zlib compression layer (`compress=3`) to optimize memory foot-print and satisfy git object constraints without sacrificing floating-point calculation accuracy.

---

##  Relational Telemetry Layer (SQL)

To ensure enterprise observability and maintain audit trails, the application implements an automated transaction logging loop:
* Every user interaction, slider manipulation, timestamp, and resulting AI model inference is automatically captured.
* Data persistence is handled via an integrated **SQLite database abstraction layer**, logging active transaction records to `grid_telemetry.db`.
* A real-time observability log window is exposed at the base of the UI mimicking standard production dashboard telemetry systems (e.g., Azure Monitor, Datadog).

---

##  Tech Stack & Frameworks

* **Core Language:** Python 3.10+
* **Data Processing:** Pandas, NumPy
* **Predictive Compute:** Scikit-Learn, Joblib
* **User Interface:** Streamlit (Forced to responsive wide-screen topology with custom Times New Roman typography stylesheets)
* **Storage Backend:** SQLite3 Relational Engine
