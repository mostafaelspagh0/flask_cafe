import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from database import db_drop_and_create_all, setup_db
from models import Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''


# db_drop_and_create_all()

## ROUTES


@app.route('/drinks', methods=['GET'])
def get_drinks():
    # try:
    return jsonify({
        "success": True,
        "drinks": [drink.short() for drink in Drink.query.all()]
    }), 200


# except Exception:
#     print(Exception.with_traceback())
#     return jsonify({
#         "success": False,
#         "message": "An Error Occurred"
#     }), 500


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def drinks_detail(payload):
    try:
        return json.dumps({
            'success':
                True,
            'drinks': [drink.long() for drink in Drink.query.all()]
        }), 200
    except Exception:
        return json.dumps({
            'success': False,
            'error': "An error occurred"
        }), 500


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    data = dict(request.form or request.json or request.data)
    drink = Drink(title=data.get('title'),
                  recipe=json.dumps(data.get('recipe')))
    try:
        drink.insert()
        return json.dumps({'success': True, 'drink': drink.long()}), 200
    except Exception:
        return json.dumps({
            'success': False,
            'error': "An error occurred"
        }), 500


@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def drinks(f, id):
    try:
        data = dict(request.form or request.json or request.data)
        drink = drink = Drink.query.filter(Drink.id == id).one_or_none()
        if drink:
            drink.title = data.get('title') if data.get(
                'title') else drink.title
            recipe = data.get('recipe') if data.get('recipe') else drink.recipe
            drink.recipe = recipe if type(recipe) == str else json.dumps(
                recipe)
            drink.update()
            return json.dumps({'success': True, 'drinks': [drink.long()]}), 200
        else:
            return json.dumps({
                'success':
                    False,
                'error':
                    'Drink #' + id + ' not found to be edited'
            }), 404
    except Exception:
        return json.dumps({
            'success': False,
            'error': "An error occurred"
        }), 500


@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('patch:drinks')
def patch_drinks(f, id):
    try:
        drink = drink = Drink.query.filter(Drink.id == id).one_or_none()
        if drink:
            drink.delete()
            return json.dumps({'success': True, 'drink': id}), 200
        else:
            return json.dumps({
                'success':
                    False,
                'error':
                    'Drink #' + id + ' not found to be deleted'
            }), 404
    except Exception:
        return json.dumps({
            'success': False,
            'error': "An error occurred"
        }), 500


## Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error
    }), error.status_code
