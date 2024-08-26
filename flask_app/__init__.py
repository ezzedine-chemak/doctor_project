from flask import Flask

app = Flask(__name__)

app.secret_key = "ezzdhldjfne5555"
app.config['UPLOAD_FOLDER'] = 'flask_app/static/uploads'
