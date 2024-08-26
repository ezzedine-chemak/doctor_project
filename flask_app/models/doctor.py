from flask_app.config.mysqlconnection import connectToMySQL
import re
from flask import flash

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class Doctor:
    db = "doctors"
    def __init__(self, data):
        self.doctor_id = data['doctor_id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.number = data['number']
        self.address = data['address']
        self.speciality = data['speciality']
        self.password = data['password']

    @classmethod
    def save(cls, data):
        query = "INSERT INTO doctors (first_name,last_name,email,number,address,speciality,password) VALUES(%(first_name)s,%(last_name)s,%(email)s,%(number)s,%(address)s,%(speciality)s,%(password)s)"
        return connectToMySQL(cls.db).query_db(query, data)

    @classmethod
    def get_by_email(cls, data):
        query = "SELECT * FROM doctors WHERE email = %(email)s;"
        results = connectToMySQL(cls.db).query_db(query, data)   
        if len(results) < 1:
            return False
        return cls(results[0])

    @classmethod
    def get_by_id(cls, data):
        query = "SELECT * FROM doctors WHERE doctor_id = %(doctor_id)s;"
        results = connectToMySQL(cls.db).query_db(query, data)
        if results:
            return cls(results[0])
        return None

    @staticmethod
    def validate_register(doctor):
        is_valid = True
        if len(doctor['first_name']) < 3:
            flash("First name must be at least 3 characters", "register")
            is_valid = False
        if len(doctor['last_name']) < 3:
            flash("Last name must be at least 3 characters", "register")
            is_valid = False
        if not EMAIL_REGEX.match(doctor['email']):
            flash("Invalid Email", "register")
            is_valid = False
        if Doctor.get_by_email({'email': doctor['email']}):
            flash("Email already taken", "register")
            is_valid = False
        if len(doctor['password']) < 8:
            flash("Password must be at least 8 characters", "register")
            is_valid = False
        if doctor['password'] != doctor['confirm']:
            flash("Passwords don't match", "register")
            is_valid = False
        return is_valid
