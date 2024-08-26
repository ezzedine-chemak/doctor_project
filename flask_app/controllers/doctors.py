from flask import render_template,redirect,session,request, flash
from flask_app import app
from flask_app.models.doctor import Doctor

from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/log')
def log():
    return render_template('log_reg.html')

@app.route('/register',methods=['POST'])
def register():

    if not Doctor.validate_register(request.form):
        return redirect('/log')
    data ={ 
        "first_name": request.form['first_name'],
        "last_name": request.form['last_name'],
        "email": request.form['email'],
        "number": request.form['number'],
        "address": request.form['address'],
        "speciality": request.form['speciality'],
        "password": bcrypt.generate_password_hash(request.form['password'])
    }
    doctor_id = Doctor.save(data)
    session['doctor_id'] = doctor_id
    return redirect('/dashboard')

@app.route('/login',methods=['POST'])
def login():
    doctor = Doctor.get_by_email(request.form)

    if not doctor:
        flash("Invalid Email","login")
        return redirect('/log')
    if not bcrypt.check_password_hash(doctor.password, request.form['password']):
        flash("Invalid Password","login")
        return redirect('/log')
    session['doctor_id'] = doctor.doctor_id
    return redirect('/dashboard')


@app.route('/dashboard')
def dashboard():
    if 'doctor_id' not in session:
        return redirect('/logout')
    data ={
        'doctor_id': session['doctor_id']
    }
    
    return render_template("dashboard.html",doctor=Doctor.get_by_id(data))


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/log') 