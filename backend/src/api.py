from flask import Flask, request, jsonify
from flask_cors import CORS

from .database import setup_db
from .controllers import drinks_controller, error_handling

app = Flask(__name__)
setup_db(app)
CORS(app)

## add controllers
drinks_controller(app)
error_handling(app)
