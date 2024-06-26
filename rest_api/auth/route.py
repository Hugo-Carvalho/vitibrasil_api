import json, re
from flask import request, jsonify
from flask_restx import Resource, fields
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required
)
from rest_api.swagger import api
from rest_api.auth.models.user import User

@api.doc(description="Este endpoint realiza o cadastro de usuarios na base")
class Singup(Resource):
    @api.expect(api.model('Singup', {
        'username': fields.String(required=True, description='Nome do usuário'),
        'email': fields.String(required=True, description='E-mail do usuário'),
        'password': fields.String(required=True, description='Senha do usuário')
    }))
    @api.response(200, 'Success', api.model('SingupPostSuccess', {
        'message': fields.String(description='Mensagem de retorno')
    }))
    @api.response(400, 'BadRequest', api.model('SingupPostBadRequest', {
        'message': fields.String(description='Mensagem de retorno')
    }))
    def post(self):
        data = json.loads(request.data)
        username = data['username']
        email = data['email']
        password = data['password']

        r = re.compile(r'^[\w-]+@(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$')

        if not r.match(email):
            return jsonify({'message': 'Formato de e-mail inválido'}), 400

        # Searching user by username and email
        current_user = User.find_by_username(username)
        if current_user:
            return jsonify({'message': f'O usuário com username {username} já existe'}), 400
        
        current_user = User.find_by_email(email)
        if current_user:
            return jsonify({'message': f'O usuário com e-mail {email} já existe'}), 400
            
        user = User(
            username=username, 
            email=email,
            password=password,
        )

        User.save(user)

        return jsonify({'message': 'Usuario criado'})

@api.doc(description="Este endpoint realiza o login do usuario")
class Login(Resource):
    @api.response(200, 'Success', api.model('LoginGetSuccess', {
        'email': fields.String(description='E-mail logado'),
        'username': fields.String(description='Username logado')
    }))
    @api.response(500, 'Error', api.model('LoginGetError', {
        'message': fields.String(description='Mensagem de erro')
    }))
    @api.doc(security='Bearer')
    @jwt_required()
    def get(self):
        try:
            # Searching user by email
            current_user = User.query.filter_by(email=get_jwt_identity()).first()
            return {
                "email": current_user.email,
                "username": current_user.username,
            }
        except Exception as e:
            return jsonify({'message': str(e)}), 500

    @api.expect(api.model('Login', {
        'email': fields.String(required=True, description='E-mail do usuário'),
        'password': fields.String(required=True, description='Senha do usuário')
    }))
    @api.response(200, 'Success', api.model('LoginPostSuccess', {
        'token': fields.String(description='Token de autenticação')
    }))
    @api.response(400, 'BadRequest', api.model('LoginPostBadRequest', {
        'message': fields.String(description='Mensagem de retorno')
    }))
    def post(self):
        data = json.loads(request.data)
        email = data['email']

        r = re.compile(r'^[\w-]+@(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$')

        if not r.match(email):
            return jsonify({'message': 'Formato de e-mail inválido'}), 400

        # Searching user by email
        current_user = User.find_by_email(email)
            
        if not current_user:
            return jsonify({'message': f'O usuário com e-mail {email} não existe'}), 400
            
        # user exists, comparing password and hash
        if User.verify_hash(data['password'], current_user.password):
            # generating access token and refresh token
            access_token = create_access_token(identity=email)
        
            return {
                'token': access_token
            }

        else:
            return jsonify({'message': 'Senha invalida!'}), 400
