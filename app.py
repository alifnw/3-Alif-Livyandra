import streamlit as st
import pickle
import pandas as pd

st.set_page_config(page_title="Prediksi Risiko Ibu Hamil", page_icon="🩺", layout="centered")

st.title("🩺 SISTEM PREDIKSI RISIKO KESEHATAN IBU HAMIL")
st.subheader("Clinical Scoring System + Machine Learning")
st.markdown("---")

# Load Model
@st.cache_resource
def load_model():
    with open("best_model_final.pkl", "rb") as f:
        return pickle.load(f)

payload = load_model()
model = payload["model"]
feature_names = payload["feature_names"]
threshold = payload.get("threshold", 0.40)

st.subheader("📋 Masukkan Data Ibu Hamil")

col1, col2 = st.columns(2)

with col1:
    age = st.number_input("Usia (tahun)", min_value=15, max_value=50, value=None, placeholder="Masukkan usia")
    systolic = st.number_input("Sistolik (mmHg)", min_value=80, max_value=200, value=None, placeholder="Masukkan sistolik")
    diastolic = st.number_input("Diastolik (mmHg)", min_value=50, max_value=120, value=None, placeholder="Masukkan diastolik")
    bmi = st.number_input("BMI (kg/m²)", min_value=15.0, max_value=45.0, value=None, step=0.1, placeholder="Masukkan BMI")

with col2:
    heart_rate = st.number_input("Detak Jantung (bpm)", min_value=50, max_value=150, value=None, placeholder="Masukkan detak jantung")
    body_temp = st.number_input("Suhu Tubuh (°F)", min_value=95.0, max_value=105.0, value=None, step=0.1, placeholder="Masukkan suhu tubuh")
    prev_complications = st.selectbox("Riwayat Komplikasi Sebelumnya", [0, 1],
                                      format_func=lambda x: "Ya" if x == 1 else "Tidak")

# Hitung fitur tambahan
pulse_pressure = systolic - diastolic if systolic is not None and diastolic is not None else 0
map_value = (systolic + 2 * diastolic) / 3 if systolic is not None and diastolic is not None else 0
is_fever = 1 if body_temp is not None and body_temp > 99 else 0

score = 0
prediction = None
prob = 0.0
scoring_table = None

if st.button("🔍 Prediksi Risiko", type="primary", use_container_width=True):
    if None in [age, systolic, diastolic, bmi, heart_rate, body_temp]:
        st.warning("Mohon isi semua data terlebih dahulu!")
    else:
        input_df = pd.DataFrame([{
            'Age': age,
            'Systolic BP': systolic,
            'Diastolic': diastolic,
            'BMI': bmi,
            'Heart Rate': heart_rate,
            'Body Temp': body_temp,
            'Pulse Pressure': pulse_pressure,
            'MAP': map_value,
            'Is_Fever': is_fever,
            'Previous Complications': prev_complications
        }])[feature_names]

        prob = model.predict_proba(input_df)[0][1]
        prediction = 1 if prob >= threshold else 0

        # Hitung Clinical Score
        score = 0
        if prev_complications == 1: score += 5
        if bmi >= 30: score += 4
        elif bmi >= 25: score += 2
        if systolic >= 140: score += 4
        if diastolic >= 90: score += 3
        if map_value >= 105: score += 3
        if heart_rate >= 90: score += 2
        if age >= 35: score += 2
        if pulse_pressure >= 60: score += 2
        if is_fever == 1: score += 1

        # Buat tabel scoring
        scoring_table = {
            "Faktor Risiko": ["Riwayat Komplikasi Sebelumnya", "BMI", "Sistolik", "Diastolik", "MAP",
                             "Detak Jantung", "Usia", "Pulse Pressure", "Demam"],
            "Kondisi Saat Ini": [
                "Ya" if prev_complications == 1 else "Tidak",
                f"{bmi:.1f} kg/m²",
                f"{systolic} mmHg",
                f"{diastolic} mmHg",
                f"{map_value:.1f} mmHg",
                f"{heart_rate} bpm",
                f"{age} tahun",
                f"{pulse_pressure} mmHg",
                "Ya" if is_fever == 1 else "Tidak"
            ],
            "Skor": [
                5 if prev_complications == 1 else 0,
                4 if bmi >= 30 else 2 if bmi >= 25 else 0,
                4 if systolic >= 140 else 0,
                3 if diastolic >= 90 else 0,
                3 if map_value >= 105 else 0,
                2 if heart_rate >= 90 else 0,
                2 if age >= 35 else 0,
                2 if pulse_pressure >= 60 else 0,
                1 if is_fever == 1 else 0
            ]
        }

# ====================== TAMPILKAN HASIL ======================
if prediction is not None:
    st.markdown("---")
    st.subheader("📊 Hasil Prediksi")

    if prediction == 1:
        st.error("**HIGH RISK**")
        st.metric("Total Clinical Score", f"{score}/25", "Risiko Tinggi")
        st.warning("⚠️ Segera rujuk ke fasilitas kesehatan tingkat lanjut")
    else:
        st.success("**LOW RISK**")
        st.metric("Total Clinical Score", f"{score}/25", "Risiko Rendah")

    st.subheader("Clinical Scoring Breakdown")
    st.dataframe(pd.DataFrame(scoring_table), use_container_width=True, hide_index=True)

    st.caption("**Total Skor ≥ 8 = High Risk** | **Total Skor < 8 = Low Risk**")

st.caption("WARNING : Sistem ini adalah alat bantu skrining awal. Bukan pengganti diagnosis dokter.")