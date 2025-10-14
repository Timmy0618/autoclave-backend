from flask_restx import Namespace, Resource, fields, marshal_with
from controller.festo import create, read, read_multi, update, delete, get_currently_executing_info

festo_ns = Namespace('festo', description='Festo operations')

# Define response models
success_response = festo_ns.model('SuccessResponse', {
    'code': fields.Integer(description='Response code'),
    'msg': fields.String(description='Response message')
})

error_response = festo_ns.model('ErrorResponse', {
    'code': fields.Integer(description='Error code'),
    'msg': fields.String(description='Error message')
})

create_response = festo_ns.model('CreateResponse', {
    'code': fields.Integer(description='Response code'),
    'msg': fields.String(description='Response message'),
    'id': fields.Integer(description='Created Festo ID')
})

festo_list_response = festo_ns.model('FestoListResponse', {
    'code': fields.Integer(description='Response code'),
    'msg': fields.String(description='Response message'),
    'data': fields.List(fields.Nested(festo_ns.model('FestoItem', {
        'id': fields.Integer(description='Festo ID'),
        'name': fields.String(description='Festo name')
    })))
})

festo_response = festo_ns.model('FestoResponse', {
    'code': fields.Integer(description='Response code'),
    'msg': fields.String(description='Response message'),
    'data': fields.Nested(festo_ns.model('FestoDetail', {
        'id': fields.Integer(description='Festo ID'),
        'name': fields.String(description='Festo name'),
        'slave_id': fields.Integer(description='Slave ID'),
        'batch_number': fields.String(description='Batch number'),
        'warning_time': fields.Integer(description='Warning time')
    }))
})

executing_response = festo_ns.model('ExecutingResponse', {
    'code': fields.Integer(description='Response code'),
    'msg': fields.String(description='Response message'),
    'data': fields.Raw(description='Executing festo data')
})

# Define input models
festo_input = festo_ns.model('FestoInput', {
    'name': fields.String(required=True, description='Festo name'),
    'slaveId': fields.Integer(description='Slave ID'),
    'batchNumber': fields.String(description='Batch number'),
    'warningTime': fields.Integer(description='Warning time')
})

festo_update = festo_ns.model('FestoUpdate', {
    'name': fields.String(description='Festo name'),
    'slaveId': fields.Integer(description='Slave ID'),
    'batchNumber': fields.String(description='Batch number'),
    'warningTime': fields.Integer(description='Warning time')
})

@festo_ns.route('')
class FestoList(Resource):
    @festo_ns.doc('create_festo',
                  responses={
                      201: ('Festo created', create_response),
                      500: ('Database error', error_response)
                  })
    @festo_ns.expect(festo_input)
    def post(self):
        data = festo_ns.payload
        result, status = create(data)
        return result, status

    @festo_ns.doc('list_festos',
                  responses={
                      200: ('Success', festo_list_response),
                      500: ('Database error', error_response)
                  })
    def get(self):
        result, status = read_multi()
        return result, status

@festo_ns.route('/<int:festo_id>')
class Festo(Resource):
    @festo_ns.doc('get_festo',
                  responses={
                      200: ('Success', festo_response),
                      404: ('Festo not found', error_response),
                      500: ('Database error', error_response)
                  })
    def get(self, festo_id):
        result, status = read(festo_id)
        return result, status

    @festo_ns.doc('update_festo',
                  responses={
                      200: ('Success', success_response),
                      404: ('Festo not found', error_response),
                      500: ('Database error', error_response)
                  })
    @festo_ns.expect(festo_update)
    def patch(self, festo_id):
        data = festo_ns.payload
        result, status = update(festo_id, data)
        return result, status

    @festo_ns.doc('delete_festo',
                  responses={
                      200: ('Success', success_response),
                      404: ('Festo not found', error_response),
                      500: ('Database error', error_response)
                  })
    def delete(self, festo_id):
        result, status = delete(festo_id)
        return result, status

@festo_ns.route('/executing')
class FestoExecuting(Resource):
    @festo_ns.doc('get_executing_festo',
                  responses={
                      200: ('Success', executing_response),
                      500: ('Database error', error_response)
                  })
    def get(self):
        result, status = get_currently_executing_info()
        return result, status
