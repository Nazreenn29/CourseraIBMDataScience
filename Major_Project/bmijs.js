function calculate() {
    let weight = document.getElementById('weight').value;
    let height = document.getElementById('height').value;
    
    document.getElementById('weight-val').textContent = `${weight} kg`;
    document.getElementById('height-val').textContent = `${height} cm`;

    // Calculate BMI
    let bmi = (weight / ((height / 100) * (height / 100))).toFixed(1);

    // Display the result
    document.getElementById('result').textContent = bmi;

    // Determine the category
    let category = '';
    if (bmi < 18.5) {
        category = 'Underweight';
    } else if (bmi >= 18.5 && bmi <= 24.9) {
        category = 'Normal weight';
    } else if (bmi >= 25 && bmi <= 29.9) {
        category = 'Overweight';
    } else {
        category = 'Obese';
    }
    document.getElementById('category').textContent = category;
}
