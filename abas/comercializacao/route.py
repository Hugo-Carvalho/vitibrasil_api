from flask import jsonify
from flask_jwt_extended import jwt_required
from flask_restx import Resource
from swagger import api

class Comercializacao(Resource):
    @api.doc(security='Bearer')
    @jwt_required()
    def get(self):
        return jsonify({'message': 'Comercialização'})