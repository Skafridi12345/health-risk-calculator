import streamlit as st
import pandas as pd
import io
from risk_model import calculate_risk_score, calculate_qrisk_score
from report_generator import generate_pdf

# Page config
st.set_page_config(page_title="Health Risk Calculator", layout="centered")

st.title("🧠 Health Risk Calculator")
st.write("This app estimates health risk levels using basic inputs. Includes a general risk model and a simplified QRISK model.")

# Tabs
tab1, tab2 = st.tabs(["🩺 General Risk", "📈 QRISK (Simplified)"])

# --- TAB 1: General Risk Calculator ---
with tab1:
    st.subheader("General Risk Score")

    st.sidebar.header("Input Parameters (General)")

    age = st.sidebar.slider("Age", 18, 100, 30)
    bmi = st.sidebar.slider("BMI", 15.0, 45.0, 22.0)
    smoker = st.sidebar.radio("Do you smoke?", ["No", "Yes"]) == "Yes"
    diabetic = st.sidebar.radio("Are you diabetic?", ["No", "Yes"]) == "Yes"

    if 'general_history' not in st.session_state:
        st.session_state.general_history = []

    if st.button("🧮 Calculate General Risk"):
        score, breakdown = calculate_risk_score(age, bmi, smoker, diabetic)

        score_color = "green" if score < 30 else "orange" if score < 70 else "red"
        st.markdown(f"### 📊 Risk Score: <span style='color:{score_color}; font-weight:bold;'>{score:.1f}</span> / 100", unsafe_allow_html=True)

        st.dataframe(pd.DataFrame({
            "Risk Factor": breakdown.keys(),
            "Contribution": breakdown.values()
        }).style.format({"Contribution": "{:.1f}"}))

        st.session_state.general_history.append({
            "Model": "General",
            "Age": age,
            "BMI": bmi,
            "Smoker": smoker,
            "Diabetic": diabetic,
            "Score": round(score, 1)
        })

# --- TAB 2: QRISK (Simplified) ---
with tab2:
    st.subheader("QRISK-style Score")

    st.sidebar.header("Input Parameters (QRISK)")

    age2 = st.sidebar.slider("QRISK Age", 25, 84, 40)
    gender = st.sidebar.selectbox("Gender", ["Male", "Female"])
    ethnicity = st.sidebar.selectbox("Ethnicity", ["White", "South Asian", "Black", "Other"])
    smoker2 = st.sidebar.radio("Smoker?", ["No", "Yes"]) == "Yes"
    bp_treated = st.sidebar.radio("On BP medication?", ["No", "Yes"]) == "Yes"
    diabetic2 = st.sidebar.radio("Diabetic?", ["No", "Yes"]) == "Yes"
    chol_hdl_ratio = st.sidebar.slider("Cholesterol/HDL Ratio", 2.0, 8.0, 4.5)

    if 'qrisk_history' not in st.session_state:
        st.session_state.qrisk_history = []

    if st.button("📈 Calculate QRISK"):
        score2 = calculate_qrisk_score(age2, gender, ethnicity, smoker2, bp_treated, diabetic2, chol_hdl_ratio)

        st.markdown(f"### 🩺 Estimated QRISK Score: **{score2:.1f}%** 10-year risk")

        st.session_state.qrisk_history.append({
            "Model": "QRISK",
            "Age": age2,
            "Gender": gender,
            "Ethnicity": ethnicity,
            "Smoker": smoker2,
            "BP meds": bp_treated,
            "Diabetic": diabetic2,
            "Chol/HDL Ratio": chol_hdl_ratio,
            "Score": round(score2, 1)
        })

# --- Common History Export ---
st.divider()

if st.session_state.general_history or st.session_state.qrisk_history:
    st.subheader("📊 Session History")
    all_data = st.session_state.general_history + st.session_state.qrisk_history
    df_all = pd.DataFrame(all_data)
    st.dataframe(df_all)

    # CSV export
    csv = io.StringIO()
    df_all.to_csv(csv, index=False)
    st.download_button("📥 Download All Results as CSV", data=csv.getvalue(),
                       file_name="all_risk_scores.csv", mime="text/csv")

    # PDF export
    latest = all_data[-1]
    if st.button("🖨️ Export Last Result as PDF"):
        filename = generate_pdf(latest)
        with open(filename, "rb") as f:
            st.download_button("📄 Download PDF Report", f, file_name=filename, mime="application/pdf")
