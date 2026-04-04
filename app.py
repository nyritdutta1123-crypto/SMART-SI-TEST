# --- Core Libraries ---
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- Page Config ---
st.set_page_config(page_title="SMART-SI Insulin Calculator", page_icon="💉", layout="centered")

st.title("🧬 Personalized Diabetes Therapy")
st.subheader("💉 SMART-SI Personalized Insulin Calculator")

# -----------------------------------
# Model Data (Hidden)
# -----------------------------------

time_data = np.array([0,10,20,30,40,50,60,70,80,90])
glucose_base = np.array([90, 120, 150, 160, 140, 110, 90, 85, 80, 90])
insulin_base = np.array([0,0,1,2,2,1.5,1,0.5,0.2,0])
meal_base = np.array([0,40,60,50,30,20,10,5,0,0])

k1 = 0.01
hypoglycemia_threshold = 70
safe_glucose_threshold = 80   # 🔥 NEW SAFETY LIMIT

# -----------------------------------
# Function to compute SI
# -----------------------------------

def calculate_SI(glucose_series, insulin_series, meal_series, time_series):
    dGdt = np.gradient(glucose_series, time_series)
    SI_values = []

    for i in range(len(time_series)):
        I = insulin_series[i]
        if I > 0:
            SI = (-dGdt[i] - k1 * glucose_series[i] + meal_series[i]) / I
            SI_values.append(SI)

    return np.median(SI_values) if SI_values else 0

# -----------------------------------
# USER INPUT
# -----------------------------------

st.header("Enter Patient Data")

name = st.text_input("Patient Name:")

glucose_input = st.number_input(
    "Current Glucose Level (mg/dL):",
    min_value=0.0,
    value=120.0
)

meal_input = st.number_input(
    "Upcoming Meal Carbs (grams):",
    min_value=0.0,
    value=50.0
)

# -----------------------------------
# PERSONALIZATION
# -----------------------------------

glucose_personal = glucose_base * (glucose_input / 120)
meal_personal = meal_base * (meal_input / 50)

SI_personal = calculate_SI(glucose_personal, insulin_base, meal_personal, time_data)

st.sidebar.success(f"Personalized Insulin Sensitivity (SI): {round(SI_personal,4)}")
st.sidebar.info("Smart-SI test by Nyrit and Rittika")

# -----------------------------------
# INSULIN DOSE CALCULATION (WITH SAFETY)
# -----------------------------------

dGdt_now = (glucose_input - 100) / 10

if glucose_input < safe_glucose_threshold:
    dose = 0   # 🔥 SAFETY OVERRIDE
else:
    if SI_personal > 0:
        dose = (-dGdt_now - k1 * glucose_input + meal_input) / SI_personal
    else:
        dose = 0

dose = max(0, dose)

# -----------------------------------
# HYPOGLYCEMIA DETECTION
# -----------------------------------

hypo_times = []
hypo_values = []

for i in range(len(glucose_personal)):
    if glucose_personal[i] < hypoglycemia_threshold:
        hypo_times.append(time_data[i])
        hypo_values.append(glucose_personal[i])

hypoglycemia_predicted = len(hypo_times) > 0

# -----------------------------------
# OUTPUT
# -----------------------------------

if st.button("Calculate Insulin Dose 💉"):

    st.success("Personalized Result")

    # 🔥 Show warning if low glucose
    if glucose_input < safe_glucose_threshold:
        st.error("🚨 Glucose is too low! Insulin NOT recommended.")
    else:
        st.metric("Recommended Insulin Dose (units)", round(dose, 2))

    st.info(f"""
    🔬 Based on:
    - Personalized SI: {round(SI_personal,4)}
    - Glucose: {glucose_input} mg/dL
    - Meal: {meal_input} g
    """)

    # Hypoglycemia alert
    if hypoglycemia_predicted:
        st.warning("⚠️ Hypoglycemia Risk Detected!")
        for t, g in zip(hypo_times, hypo_values):
            st.write(f"At {t} minutes → Glucose = {round(g,2)} mg/dL")
    else:
        st.success("✅ No Hypoglycemia Risk Detected")

    # -----------------------------------
    # Plot
    # -----------------------------------

    st.subheader("Personalized Glucose Response Curve")

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(time_data, glucose_personal, marker='o')

    ax.axhline(y=hypoglycemia_threshold, linestyle='--', label="Hypoglycemia Threshold")

    for t, g in zip(hypo_times, hypo_values):
        ax.plot(t, g, 'rx', markersize=10)

    ax.set_title(f"Glucose Response for {name if name else 'Patient'}")
    ax.set_xlabel("Time (minutes)")
    ax.set_ylabel("Glucose Level (mg/dL)")
    ax.grid(True)
    ax.legend()

    st.pyplot(fig)
    plt.close(fig)

# -----------------------------------
# Disclaimer
# -----------------------------------

st.caption("⚠️ This is a research prototype. Not for clinical use.")
