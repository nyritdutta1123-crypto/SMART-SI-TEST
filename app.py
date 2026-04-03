# --- Core Libraries ---
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- Page Config ---
st.set_page_config(page_title="SMART-SI Insulin Calculator", page_icon="💉", layout="centered")

st.title("Personalized Diabetes Therapy")
st.subheader("💉 SMART-SI Insulin Calculator")

# -----------------------------------
# Hidden Model Data (acts as base physiology)
# -----------------------------------

time_data = np.array([0,10,20,30,40,50,60,70,80,90])
glucose_base = np.array([90, 120, 150, 160, 140, 110, 90, 85, 80, 90])
insulin_base = np.array([0,0,1,2,2,1.5,1,0.5,0.2,0])
meal_base = np.array([0,40,60,50,30,20,10,5,0,0])

k1 = 0.01
hypoglycemia_threshold = 70

# -----------------------------------
# DYNAMIC SI FUNCTION
# -----------------------------------

def calculate_dynamic_SI(glucose_series, insulin_series, meal_series, time_series):
    
    SI = np.zeros_like(glucose_series)
    
    # Physiological parameters
    a = 0.02
    b = 0.0003
    S0 = 0.01
    
    SI[0] = S0
    
    for i in range(1, len(time_series)):
        dSI = -a*(SI[i-1] - S0) + b*glucose_series[i-1]
        SI[i] = SI[i-1] + dSI
        
    return SI

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
# PERSONALIZATION LOGIC
# -----------------------------------

glucose_personal = glucose_base * (glucose_input / 120)
meal_personal = meal_base * (meal_input / 50)

# Dynamic SI
SI_series = calculate_dynamic_SI(glucose_personal, insulin_base, meal_personal, time_data)
SI_current = SI_series[-1]

st.sidebar.success(f"Current Dynamic SI: {round(SI_current,4)}")
st.sidebar.info("Smart-SI test by Nyrit")

# -----------------------------------
# ✅ CLINICALLY CORRECT DOSE MODEL
# -----------------------------------

# Base clinical parameters
ICR_base = 12   # grams per 1 unit insulin
ISF = 50        # mg/dL drop per unit

# Adjust ICR using dynamic SI
ICR_dynamic = ICR_base / (1 + 5*(SI_current - 0.01))

# Meal insulin
meal_dose = meal_input / ICR_dynamic

# Correction insulin (only if glucose high)
correction = max(0, (glucose_input - 110) / ISF)

# Final dose
dose = meal_dose + correction

# Safety clamp (important)
dose = max(0, min(dose, 15))

# -----------------------------------
# HYPOGLYCEMIA PREDICTION
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

    st.metric("Recommended Insulin Dose (units)", round(dose, 2))

    st.info(f"""
    🔬 Based on:
    - Dynamic SI: {round(SI_current,4)}
    - ICR (adjusted): {round(ICR_dynamic,2)}
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
    # Glucose Plot
    # -----------------------------------

    st.subheader("Personalized Glucose Response Curve")

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(time_data, glucose_personal, marker='o', linestyle='-')
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
    # Dynamic SI Plot
    # -----------------------------------

    st.subheader("Dynamic Insulin Sensitivity Over Time")

    fig2, ax2 = plt.subplots(figsize=(10, 5))

    ax2.plot(time_data, SI_series, marker='o')
    ax2.set_title("Time-Varying Insulin Sensitivity")
    ax2.set_xlabel("Time (minutes)")
    ax2.set_ylabel("Insulin Sensitivity")
    ax2.grid(True)

    st.pyplot(fig2)
    plt.close(fig2)

# -----------------------------------
# Disclaimer
# -----------------------------------

st.caption("⚠️ This is a research prototype. Not for clinical use.")
