from flask import Flask, request, render_template
import numpy as np
import pandas as pd
import pickle

app = Flask(__name__)
model = pickle.load(open('model.pickle', 'rb'))

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/predict_page")
def predict_page():
    return render_template('predict.html')

@app.route("/bmi")
def bmi_page():
    return render_template('bmi.html')

@app.route("/counsel")
def counsel_page():
    return render_template('counsel.html')

@app.route("/contact")
def contact_page():
    return render_template('contact.html')

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == "POST":
        gender_Male = int(request.form.get('gender', 0))
        age = int(request.form.get('age', 0))
        hypertension_1 = int(request.form.get('hypertension', 0))
        heart_disease_1 = int(request.form.get('heart_disease', 0))
        ever_married_Yes = int(request.form.get('ever_married', 0))
        work_type_Never_worked = 0
        work_type_Private = 0
        work_type_Self_employed = 0
        work_type_children = 0
        work = int(request.form.get('work_type', 0))
        if work == 1:
            work_type_Never_worked = 1
        elif work == 2:
            work_type_Private = 1
        elif work == 3:
            work_type_Self_employed = 1
        elif work == 4:
            work_type_children = 1

        Residence_type_Urban = int(request.form.get('residence_type', 0))
        avg_glucose_level = float(request.form.get('avg_glucose_level', 0.0))
        bmi = float(request.form.get('bmi', 0.0))
        smoking_status_formerly_smoked = 0
        smoking_status_never_smoked = 0
        smoking_status_smokes = 0
        smoking = int(request.form.get('smoking_status', 0))
        if smoking == 1:
            smoking_status_formerly_smoked = 1
        elif smoking == 2:
            smoking_status_never_smoked = 1
        elif smoking == 3:
            smoking_status_smokes = 1

        input_features = [age, avg_glucose_level, bmi, gender_Male, hypertension_1, heart_disease_1, ever_married_Yes,
                          work_type_Never_worked, work_type_Private, work_type_Self_employed, work_type_children,
                          Residence_type_Urban, smoking_status_formerly_smoked, smoking_status_never_smoked,
                          smoking_status_smokes]

        features_name = ['age', 'avg_glucose_level', 'bmi', 'gender_Male', 'hypertension_1', 'heart_disease_1',
                         'ever_married_Yes', 'work_type_Never_worked', 'work_type_Private', 'work_type_Self-employed',
                         'work_type_children', 'Residence_type_Urban', 'smoking_status_formerly smoked',
                         'smoking_status_never smoked', 'smoking_status_smokes']

        df = pd.DataFrame([input_features], columns=features_name)
        prediction = model.predict(df)[0]

        if prediction == 1:
            prediction_text = 'Patient has stroke risk'
        else:
            prediction_text = 'Congratulations, patient does not have stroke risk'

        return render_template('predict.html', prediction_text=prediction_text)

if __name__ == "__main__":
    app.run(debug=True)
