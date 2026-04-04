import streamlit as st
import numpy as np
import pickle
import os

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Prediksi Risiko Maternal",
    page_icon="🏥",
    layout="wide",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }
.stApp { background-color: #F0F4F8; }
#MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Load Model ────────────────────────────────────────────────────────────────
@st.cache_resource
def load_model():
    path = os.path.join(os.path.dirname(__file__), "best_model_final.pkl")
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return pickle.load(f)

data = load_model()

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🏥 Sistem Prediksi Risiko Maternal")
st.caption("Maternal Risk Assessment · Model: GradientBoosting · Fokus: Maximize Recall High Risk")
st.divider()

if data is None:
    st.error("⚠️ File `best_model_final.pkl` tidak ditemukan. Pastikan ada di folder yang sama dengan `app.py`.")
    st.stop()

model     = data['model']
threshold = data['threshold']

# ── Layout ────────────────────────────────────────────────────────────────────
col_form, col_result = st.columns([1, 1], gap="large")

# ══════════════════════════════════════════════════════════════════════════════
# FORM
# ══════════════════════════════════════════════════════════════════════════════
with col_form:
    st.subheader("📋 Data Pasien Ibu Hamil")
    st.markdown("**🫀 Tanda Vital**")

    c1, c2 = st.columns(2)
    with c1:
        age = st.number_input(
            "Usia (tahun) · 10–60",
            min_value=10, max_value=60,
            value=None, step=1,
            placeholder="Masukkan usia",
        )
    with c2:
        heart_rate = st.number_input(
            "Detak Jantung (bpm) · 40–200",
            min_value=40, max_value=200,
            value=None, step=1,
            placeholder="Masukkan detak jantung",
        )

    c3, c4 = st.columns(2)
    with c3:
        systolic = st.number_input(
            "Sistolik (mmHg) · 50–250",
            min_value=50, max_value=250,
            value=None, step=1,
            placeholder="Masukkan sistolik",
        )
    with c4:
        diastolic = st.number_input(
            "Diastolik (mmHg) · 30–180",
            min_value=30, max_value=180,
            value=None, step=1,
            placeholder="Masukkan diastolik",
        )

    c5, c6 = st.columns(2)
    with c5:
        body_temp = st.number_input(
            "Suhu Tubuh (°F) · 95.0–108.0",
            min_value=95.0, max_value=108.0,
            value=None, step=0.1, format="%.1f",
            placeholder="Masukkan suhu tubuh",
        )
    with c6:
        bmi = st.number_input(
            "BMI (kg/m²) · 10.0–60.0",
            min_value=10.0, max_value=60.0,
            value=None, step=0.1, format="%.1f",
            placeholder="Masukkan BMI",
        )

    st.markdown("**📁 Riwayat Klinis**")
    prev_comp = st.selectbox("Riwayat Komplikasi Sebelumnya", ["Tidak", "Ya"]) == "Ya"

    st.warning("⚠️ **PERHATIAN:** Sistem ini adalah alat bantu skrining awal. Bukan pengganti diagnosis dokter.")

    # Cek semua field sudah diisi
    all_filled = all(v is not None for v in [age, heart_rate, systolic, diastolic, body_temp, bmi])

    predict_btn = st.button(
        "🔍 Prediksi Risiko",
        use_container_width=True,
        type="primary",
        disabled=not all_filled,
    )

# ══════════════════════════════════════════════════════════════════════════════
# RESULT
# ══════════════════════════════════════════════════════════════════════════════
with col_result:
    if predict_btn and all_filled:

        if diastolic >= systolic:
            st.error("⚠️ Diastolik tidak boleh lebih besar atau sama dengan Sistolik.")
            st.stop()

        # Derived features
        MAP            = (systolic + 2 * diastolic) / 3
        pulse_pressure = systolic - diastolic
        is_fever       = 1 if body_temp > 100.4 else 0

        # Input array — urutan sesuai feature_names model
        # ['Age', 'Systolic BP', 'Diastolic', 'BMI', 'Heart Rate',
        #  'Pulse Pressure', 'MAP', 'Previous Complications', 'Is_Fever']
        X = np.array([[
            age, systolic, diastolic, bmi, heart_rate,
            pulse_pressure, MAP, int(prev_comp), is_fever,
        ]])

        # Predict dengan custom threshold 0.42
        proba     = model.predict_proba(X)[0]
        prob_high = proba[1]
        prob_low  = proba[0]
        is_high   = prob_high >= threshold

        # ── Risk Banner ───────────────────────────────────────────────────────
        st.subheader("📊 Hasil Prediksi")

        if is_high:
            st.error("## ⚠️ HIGH RISK — Risiko Tinggi Terdeteksi")
            st.markdown("Pasien memerlukan **pemantauan ketat** dan evaluasi segera oleh tenaga medis.")
        else:
            st.success("## ✅ LOW RISK — Risiko Rendah")
            st.markdown("Kondisi pasien dalam batas aman. Tetap lanjutkan **pemantauan rutin antenatal**.")

        # ── Probability Metrics ───────────────────────────────────────────────
        m1, m2 = st.columns(2)
        m1.metric("Probabilitas High Risk", f"{prob_high * 100:.1f}%")
        m2.metric("Probabilitas Low Risk",  f"{prob_low  * 100:.1f}%")

    else:
        st.info("👈 Lengkapi data pasien di sebelah kiri, lalu klik **Prediksi Risiko**.")

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.caption("© 2025 Sistem Prediksi Risiko Maternal · Hanya untuk keperluan klinis terotorisasi · SYS v2.0.0")