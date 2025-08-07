def calculate_risk_score(age, bmi, smoker, diabetic):
    age_contrib = 0.5 * age
    bmi_contrib = 0.8 * bmi
    smoke_contrib = 15.0 if smoker else 0.0
    diabetes_contrib = 20.0 if diabetic else 0.0

    total = age_contrib + bmi_contrib + smoke_contrib + diabetes_contrib
    return min(total, 100.0), {
        'Age': age_contrib,
        'BMI': bmi_contrib,
        'Smoking': smoke_contrib,
        'Diabetes': diabetes_contrib
    }

def calculate_qrisk_score(age, gender, ethnicity, smoker, bp_treated, diabetic, chol_hdl_ratio):
    base = 5.0 + 0.15 * age + 2.0 * chol_hdl_ratio
    if smoker:
        base += 5
    if bp_treated:
        base += 3
    if diabetic:
        base += 4
    if gender == "Male":
        base += 2
    if ethnicity == "South Asian":
        base += 3
    elif ethnicity == "Black":
        base += 2
    return min(base, 100.0)
