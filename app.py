import io
import numpy as np
import pandas as pd
import streamlit as st
from risk_model import calculate_risk_score, calculate_qrisk_score
from report_generator import generate_pdf

# ---------- Page config ----------
st.set_page_config(
    page_title="Health Risk Calculator",
    page_icon="🧠",
    layout="wide"
)

# ---------- Header / Hero ----------
st.markdown(
    """
    <div style="padding: 1.2rem; border-radius: 12px; background: linear-gradient(135deg,#f0f4ff,#ffffff); border:1px solid #e6ebff;">
      <h1 style="margin:0;">🧠 Health Risk Calculator</h1>
      <p style="margin-top:.5rem; font-size:1.05rem;">
        Estimate your risk using simple inputs. Includes a general risk model and a simplified QRISK-style calculator, plus
        clear explanations, healthy ranges, and a “what-if” explorer.
      </p>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------- Init session state ----------
if "general_history" not in st.session_state:
    st.session_state.general_history = []
if "qrisk_history" not in st.session_state:
    st.session_state.qrisk_history = []

# ---------- Tabs ----------
tab1, tab2, tab3, tab4 = st.tabs([
    "🩺 General Risk",
    "📈 QRISK (Simplified)",
    "🧪 What-If Explorer",
    "📚 Info & References",
])

# ========== TAB 1: General Risk ==========
with tab1:
    st.subheader("General Risk Score")

    cols = st.columns([1, 1, 1])
    with cols[0]:
        age = st.number_input(
            "Age",
            min_value=18, max_value=100, value=35, step=1,
            help="Your age in years.",
            key="age_general"
        )
    with cols[1]:
        bmi = st.number_input(
            "BMI",
            min_value=15.0, max_value=60.0, value=24.5, step=0.1,
            help="Body Mass Index. 18.5–24.9 is generally considered healthy.",
            key="bmi_general"
        )
    with cols[2]:
        smoker = st.selectbox(
            "Smoker?",
            ["No", "Yes"], index=0,
            key="smoker_general"
        ) == "Yes"
        diabetic = st.selectbox(
            "Diabetic?",
            ["No", "Yes"], index=0,
            key="diabetic_general"
        ) == "Yes"

    if st.button("🧮 Calculate General Risk", use_container_width=True, key="calc_general_btn"):
        score, breakdown = calculate_risk_score(age, bmi, smoker, diabetic)

        # Two-column result layout
        c1, c2 = st.columns([1, 1])
        with c1:
            score_color = "green" if score < 30 else "orange" if score < 70 else "red"
            st.markdown(
                f"### 📊 Risk Score: <span style='color:{score_color};font-weight:700'>{score:.1f}</span> / 100",
                unsafe_allow_html=True
            )
            st.progress(min(int(score), 100))
            if score < 30:
                st.success("Low risk")
            elif score < 70:
                st.warning("Moderate risk")
            else:
                st.error("High risk")

        with c2:
            st.markdown("### ✅ What this means")
            if score < 30:
                st.write("• Keep doing what works: balanced diet, regular activity, and routine checkups.")
            elif score < 70:
                st.write("• Consider lifestyle tweaks (nutrition, activity, weight management) and discuss screening with a clinician.")
            else:
                st.write("• Please consider a clinical review. Address smoking, weight, and glucose management with a professional.")

        st.markdown("### 🧮 Contribution Breakdown")
        df_breakdown = pd.DataFrame({
            "Risk Factor": list(breakdown.keys()),
            "Contribution": list(breakdown.values())
        }).sort_values("Contribution", ascending=False)
        st.dataframe(df_breakdown.style.format({"Contribution": "{:.1f}"}), use_container_width=True)

        with st.expander("ℹ️ Healthy ranges & quick tips"):
            st.markdown(
                """
                - **BMI**: 18.5–24.9 (consider a nutrition & activity plan if above range)  
                - **Smoking**: Not smoking is strongly associated with lower long-term risk  
                - **Blood sugar (diabetes)**: Aim for good glycaemic control per clinician advice  
                - **General**: Sleep, stress, and regular checkups matter more than people think  
                """
            )

        # Log history
        st.session_state.general_history.append({
            "Model": "General",
            "Age": age,
            "BMI": bmi,
            "Smoker": smoker,
            "Diabetic": diabetic,
            "Score": round(score, 1)
        })

# ========== TAB 2: QRISK (Simplified) ==========
with tab2:
    st.subheader("QRISK-style Score (Simplified)")

    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        age2 = st.number_input(
            "Age",
            min_value=25, max_value=84, value=45, step=1,
            key="age_qrisk"
        )
        gender = st.selectbox("Gender", ["Male", "Female"], key="gender_qrisk")
    with c2:
        ethnicity = st.selectbox("Ethnicity", ["White", "South Asian", "Black", "Other"], key="ethnicity_qrisk")
        bp_treated = st.selectbox("On BP medication?", ["No", "Yes"], key="bp_qrisk") == "Yes"
    with c3:
        smoker2 = st.selectbox("Smoker?", ["No", "Yes"], key="smoker_qrisk") == "Yes"
        diabetic2 = st.selectbox("Diabetic?", ["No", "Yes"], key="diabetic_qrisk") == "Yes"

    chol_hdl_ratio = st.slider(
        "Cholesterol / HDL Ratio",
        2.0, 8.0, 4.5, 0.1,
        help="A common lipid risk indicator used in many calculators.",
        key="chol_ratio_qrisk"
    )

    if st.button("📈 Calculate QRISK (Simplified)", use_container_width=True, key="calc_qrisk_btn"):
        score2 = calculate_qrisk_score(age2, gender, ethnicity, smoker2, bp_treated, diabetic2, chol_hdl_ratio)

        left, right = st.columns([1, 1])
        with left:
            st.markdown(f"### 🩺 Estimated 10-year risk: **{score2:.1f}%**")
            bar_val = int(min(score2, 100))
            st.progress(bar_val)
            if score2 < 10:
                st.success("Low 10-year risk (<10%)")
            elif score2 < 20:
                st.warning("Moderate 10-year risk (10–20%)")
            else:
                st.error("High 10-year risk (≥20%)")

        with right:
            st.markdown("### 🧭 Actions you can consider")
            st.write(
                "- Review blood pressure and lipids with your clinician\n"
                "- Consider smoking cessation support if applicable\n"
                "- Nutrition, activity, and weight management can significantly reduce risk"
            )

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

# ========== TAB 3: What-If Explorer ==========
with tab3:
    st.subheader("What-If Explorer")
    st.write("See how the **General** risk score changes with different ages and BMI values (holding smoking/diabetes fixed).")

    w_cols = st.columns([1, 1, 1, 1])
    with w_cols[0]:
        base_age = st.number_input("Base Age", 18, 100, 40, key="whatif_age")
    with w_cols[1]:
        base_bmi = st.number_input("Base BMI", 15.0, 60.0, 27.0, step=0.1, key="whatif_bmi")
    with w_cols[2]:
        base_smoker = st.selectbox("Smoker (fixed)", ["No", "Yes"], key="whatif_smoker") == "Yes"
    with w_cols[3]:
        base_diabetic = st.selectbox("Diabetic (fixed)", ["No", "Yes"], key="whatif_diabetic") == "Yes"

    # Generate curves
    ages = np.arange(18, 101, 1)
    scores_by_age = [calculate_risk_score(a, base_bmi, base_smoker, base_diabetic)[0] for a in ages]

    bmis = np.arange(15.0, 45.1, 0.5)
    scores_by_bmi = [calculate_risk_score(base_age, b, base_smoker, base_diabetic)[0] for b in bmis]

    c_age, c_bmi = st.columns(2)
    with c_age:
        st.markdown("**Risk vs Age** (BMI fixed)")
        df_age = pd.DataFrame({"Age": ages, "Risk Score": scores_by_age}).set_index("Age")
        st.line_chart(df_age, height=260, use_container_width=True)

    with c_bmi:
        st.markdown("**Risk vs BMI** (Age fixed)")
        df_bmi = pd.DataFrame({"BMI": bmis, "Risk Score": scores_by_bmi}).set_index("BMI")
        st.line_chart(df_bmi, height=260, use_container_width=True)

# ========== TAB 4: Info & References ==========
with tab4:
    st.subheader("Information, Limitations & References")

    with st.expander("What is QRISK (in general terms)?", expanded=False):
        st.write(
            "QRISK-type tools estimate 10-year cardiovascular risk using demographics, clinical history, and lipid levels. "
            "This app includes a simplified version for demonstration only."
        )

    with st.expander("What is Cholesterol/HDL Ratio?"):
        st.write(
            "It’s total cholesterol divided by HDL (the ‘good’ cholesterol). Higher ratios typically indicate higher risk."
        )

    with st.expander("Limitations"):
        st.write(
            "• This app is a demonstration and **not a medical device**.\n"
            "• It uses simplified logic and may not reflect your personal clinical risk.\n"
            "• Always seek professional medical advice for diagnosis or treatment."
        )

    st.markdown("### References & Further Reading")
    st.markdown(
        """
        - NHS resources on cardiovascular risk and prevention  
        - NICE guidance on lipid modification and cardiovascular risk assessment  
        - Public information from respected health systems (e.g., academic hospitals, national health services)  
        - Primary literature on risk factors and prevention strategies  
        """.strip()
    )

# ========== Footer: History + Export ==========
st.markdown("---")
st.subheader("📊 Session History & Export")
all_data = st.session_state.general_history + st.session_state.qrisk_history
if all_data:
    df_all = pd.DataFrame(all_data)
    st.dataframe(df_all, use_container_width=True)

    # CSV export
    csv_buf = io.StringIO()
    df_all.to_csv(csv_buf, index=False)
    st.download_button(
        "📥 Download All Results (CSV)",
        data=csv_buf.getvalue(),
        file_name="all_risk_scores.csv",
        mime="text/csv",
        key="download_csv_btn"
    )

    # PDF export (last record)
    latest = all_data[-1]
    if st.button("🖨️ Export Last Result as PDF", key="export_pdf_btn"):
        filename = generate_pdf(latest)
        with open(filename, "rb") as f:
            st.download_button(
                "📄 Download PDF Report",
                f,
                file_name=filename,
                mime="application/pdf",
                key="download_pdf_btn"
            )

st.caption("© 2025 — Educational demo only. Not for clinical use.")
