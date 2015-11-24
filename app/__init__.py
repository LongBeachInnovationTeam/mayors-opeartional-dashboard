from flask import Flask

# Define the WSGI application object
app = Flask(__name__)

# Import a module / component using its blueprint handler variable
from app.go_lb.controllers import go_lb

# Register blueprint(s)
app.register_blueprint(go_lb, url_prefix='/')