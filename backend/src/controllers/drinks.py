import json

from flask import jsonify, request

from ..auth import requires_auth
from ..models import Drink


def drinks_controller(app):
    @app.route('/drinks', methods=['GET'])
    def get_drinks():
        try:
            return jsonify({
                "success": True,
                "drinks": [drink.short() for drink in Drink.query.all()]
            }), 200
        except Exception:
            return jsonify({
                "success": False,
                "message": "An Error Occurred"
            }), 500

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
    def patch_drinks(payload, id):
        try:
            data = dict(request.form or request.json or request.data)
            drink = Drink.query.filter(Drink.id == id).one_or_none()
            if drink is not None:
                if data.get('title'):
                    drink.title = data.get('title')
                if data.get('recipe'):
                    drink.recipe = json.dumps(data.get('recipe'))
                drink.update()
                return json.dumps({'success': True, 'drinks': [drink.long()]}), 200
            else:
                return json.dumps({
                    'success':
                        False,
                    'error':
                        'Drink not found to be edited'
                }), 404
        except Exception:
            return json.dumps({
                'success': False,
                'error': "An error occurred"
            }), 500

    @app.route('/drinks/<id>', methods=['DELETE'])
    @requires_auth('patch:drinks')
    def delete_drinks(payload, id):
        try:
            drink = Drink.query.filter(Drink.id == id).one_or_none()
            if drink is not None:
                drink.delete()
                return json.dumps({'success': True, 'drink': id}), 200
            else:
                return json.dumps({
                    'success':
                        False,
                    'error':
                        'Drink not found to be deleted'
                }), 404
        except Exception:
            return json.dumps({
                'success': False,
                'error': "An error occurred"
            }), 500
