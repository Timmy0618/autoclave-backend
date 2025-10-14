from flask_restx import Namespace, Resource, fields, marshal_with
from controller.history import get_unique_batch_numbers, get_batch_records_csv, get_festo_history

history_ns = Namespace('history', description='History operations')

@history_ns.route('')
class History(Resource):
    @history_ns.doc('get_history',
                    responses={
                        200: ('Success', history_ns.model('HistoryResponse', {
                            'code': fields.Integer(description='Response code'),
                            'msg': fields.String(description='Response message'),
                            'data': fields.Raw(description='History data')
                        })),
                        500: ('Database error', history_ns.model('ErrorResponse', {
                            'code': fields.Integer(description='Error code'),
                            'msg': fields.String(description='Error message')
                        }))
                    })
    @history_ns.expect(history_ns.model('HistoryInput', {
        'batchNumber': fields.String(required=True, description='Batch number'),
        'startTime': fields.String(required=True, description='Start time'),
        'endTime': fields.String(required=True, description='End time'),
        'type': fields.String(required=True, description='Time type (hour/minute)')
    }))
    def post(self):
        data = history_ns.payload
        result, status = get_festo_history(data)
        return result, status

@history_ns.route('/batch')
class HistoryBatch(Resource):
    @history_ns.doc('get_batch_numbers',
                    responses={
                        200: ('Success', history_ns.model('BatchResponse', {
                            'code': fields.Integer(description='Response code'),
                            'msg': fields.String(description='Response message'),
                            'data': fields.List(fields.String, description='List of batch numbers')
                        })),
                        500: ('Database error', history_ns.model('ErrorResponse', {
                            'code': fields.Integer(description='Error code'),
                            'msg': fields.String(description='Error message')
                        }))
                    })
    def get(self):
        result, status = get_unique_batch_numbers()
        return result, status

@history_ns.route('/export')
class HistoryExport(Resource):
    @history_ns.doc('export_csv',
                    responses={
                        200: ('Success', 'CSV file download'),
                        500: ('Database error', history_ns.model('ErrorResponse', {
                            'code': fields.Integer(description='Error code'),
                            'msg': fields.String(description='Error message')
                        }))
                    })
    @history_ns.expect(history_ns.model('ExportInput', {
        'startTime': fields.String(required=True, description='Start time'),
        'endTime': fields.String(required=True, description='End time'),
        'batchNumber': fields.String(required=True, description='Batch number')
    }))
    def post(self):
        data = history_ns.payload
        return get_batch_records_csv(data)
