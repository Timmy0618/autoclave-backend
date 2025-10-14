from flask_restx import Namespace, Resource, fields, marshal_with
from controller.formula import create, read, read_multi, update, delete

formula_ns = Namespace('formula', description='Formula operations')

# Define response models
success_response = formula_ns.model('SuccessResponse', {
    'code': fields.Integer(description='Response code'),
    'msg': fields.String(description='Response message')
})

error_response = formula_ns.model('ErrorResponse', {
    'code': fields.Integer(description='Error code'),
    'msg': fields.String(description='Error message')
})

create_response = formula_ns.model('CreateResponse', {
    'code': fields.Integer(description='Response code'),
    'msg': fields.String(description='Response message'),
    'data': fields.Nested(formula_ns.model('FormulaData', {
        'id': fields.Integer(description='Created Formula ID'),
        'name': fields.String(description='Formula name')
    }))
})

formula_list_response = formula_ns.model('FormulaListResponse', {
    'code': fields.Integer(description='Response code'),
    'msg': fields.String(description='Response message'),
    'data': fields.List(fields.Nested(formula_ns.model('FormulaItem', {
        'id': fields.Integer(description='Formula ID'),
        'name': fields.String(description='Formula name'),
        'createTime': fields.String(description='Create time'),
        'updateTime': fields.String(description='Update time')
    })))
})

formula_response = formula_ns.model('FormulaResponse', {
    'code': fields.Integer(description='Response code'),
    'msg': fields.String(description='Response message'),
    'data': fields.Nested(formula_ns.model('FormulaDetail', {
        'id': fields.Integer(description='Formula ID'),
        'name': fields.String(description='Formula name'),
        'details': fields.List(fields.Nested(formula_ns.model('FormulaDetailItem', {
            'sequence': fields.Integer(description='Sequence'),
            'pressure': fields.Float(description='Pressure'),
            'processTime': fields.Integer(description='Process time')
        })))
    }))
})

# Define input models
formula_input = formula_ns.model('FormulaInput', {
    'name': fields.String(required=True, description='Formula name'),
    'detail': fields.List(fields.Nested(formula_ns.model('FormulaDetailInput', {
        'pressure': fields.Float(description='Pressure'),
        'process_time': fields.Integer(description='Process time')
    })))
})

formula_update = formula_ns.model('FormulaUpdate', {
    'name': fields.String(description='Formula name'),
    'detail': fields.List(fields.Nested(formula_ns.model('FormulaDetailUpdate', {
        'pressure': fields.Float(description='Pressure'),
        'processTime': fields.Integer(description='Process time')
    })))
})

@formula_ns.route('')
class FormulaList(Resource):
    @formula_ns.doc('create_formula',
                    responses={
                        201: ('Formula created', create_response),
                        500: ('Database error', error_response)
                    })
    @formula_ns.expect(formula_input)
    def post(self):
        data = formula_ns.payload
        result, status = create(data)
        return result, status

    @formula_ns.doc('list_formulas',
                    responses={
                        200: ('Success', formula_list_response),
                        500: ('Database error', error_response)
                    })
    def get(self):
        result, status = read_multi()
        return result, status

@formula_ns.route('/<int:formula_id>')
class Formula(Resource):
    @formula_ns.doc('get_formula',
                    responses={
                        200: ('Success', formula_response),
                        404: ('Formula not found', error_response),
                        500: ('Database error', error_response)
                    })
    def get(self, formula_id):
        result, status = read(formula_id)
        return result, status

    @formula_ns.doc('update_formula',
                    responses={
                        200: ('Success', success_response),
                        404: ('Formula not found', error_response),
                        500: ('Database error', error_response)
                    })
    @formula_ns.expect(formula_update)
    def patch(self, formula_id):
        data = formula_ns.payload
        result, status = update(formula_id, data)
        return result, status

    @formula_ns.doc('delete_formula',
                    responses={
                        200: ('Success', success_response),
                        404: ('Formula not found', error_response),
                        500: ('Database error', error_response)
                    })
    def delete(self, formula_id):
        result, status = delete(formula_id)
        return result, status
