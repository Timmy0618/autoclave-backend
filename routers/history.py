from flask_restx import Namespace, Resource, fields, marshal_with
from controller.history import get_unique_batch_numbers, get_batch_records_csv, get_festo_history

history_ns = Namespace('history', description='History operations')

# Define response models
success_response = history_ns.model('SuccessResponse', {
    'code': fields.Integer(description='Response code'),
    'msg': fields.String(description='Response message')
})

error_response = history_ns.model('ErrorResponse', {
    'code': fields.Integer(description='Error code'),
    'msg': fields.String(description='Error message')
})

history_response = history_ns.model('HistoryResponse', {
    'code': fields.Integer(description='Response code'),
    'msg': fields.String(description='Response message'),
    'data': fields.Raw(description='History data')
})

batch_response = history_ns.model('BatchResponse', {
    'code': fields.Integer(description='Response code'),
    'msg': fields.String(description='Response message'),
    'data': fields.List(fields.String, description='List of batch numbers')
})

# Define input models
history_input = history_ns.model('HistoryInput', {
    'batchNumber': fields.String(required=True, description='Batch number'),
    'startTime': fields.String(required=True, description='Start time'),
    'endTime': fields.String(required=True, description='End time'),
    'type': fields.String(required=True, description='Time type (hour/minute)')
})

export_input = history_ns.model('ExportInput', {
    'startTime': fields.String(required=True, description='Start time'),
    'endTime': fields.String(required=True, description='End time'),
    'batchNumber': fields.String(required=True, description='Batch number')
})

@history_ns.route('/')
class HistoryList(Resource):
    @history_ns.doc('get_history',
                    responses={
                        200: ('Success', history_response),
                        500: ('Database error', error_response)
                    })
    @history_ns.expect(history_input)
    def get(self):
        data = history_ns.payload
        result, status = get_festo_history(data)
        return result, status

@history_ns.route('/batch')
class HistoryBatch(Resource):
    @history_ns.doc('get_batch_numbers',
                    responses={
                        200: ('Success', batch_response),
                        500: ('Database error', error_response)
                    })
    def get(self):
        result, status = get_unique_batch_numbers()
        return result, status

@history_ns.route('/export')
class HistoryExport(Resource):
    @history_ns.doc('export_csv',
                    description='Export batch records as CSV file',
                    responses={
                        500: ('Database error', error_response)
                    })
    @history_ns.expect(export_input)
    @history_ns.produces(['text/csv'])
    def post(self):
        data = history_ns.payload
        return get_batch_records_csv(data)
