from flask_restx import Namespace, Resource, fields, marshal_with
from controller.user import login

user_ns = Namespace('user', description='User operations')

# Define response models
success_response = user_ns.model('SuccessResponse', {
    'code': fields.Integer(description='Response code'),
    'msg': fields.String(description='Response message')
})

error_response = user_ns.model('ErrorResponse', {
    'code': fields.Integer(description='Error code'),
    'msg': fields.String(description='Error message')
})

login_response = user_ns.model('LoginResponse', {
    'code': fields.Integer(description='Response code'),
    'msg': fields.String(description='Response message'),
    'data': fields.Nested(user_ns.model('LoginData', {
        'accessToken': fields.String(description='JWT access token')
    }))
})

login_input = user_ns.model('UserLogin', {
    'name': fields.String(required=True, description='Username'),
    'password': fields.String(required=True, description='Password')
})

@user_ns.route('/login')
class UserLogin(Resource):
    @user_ns.doc('user_login',
                 responses={
                     200: ('Success', login_response),
                     401: ('Invalid credentials', error_response),
                     500: ('Internal server error', error_response)
                 })
    @user_ns.expect(login_input)
    def post(self):
        data = user_ns.payload
        result, status = login(data)
        return result, status
