from flask_app import app
from flask_app.controllers import doctors, tests

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
