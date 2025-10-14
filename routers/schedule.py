from flask_restx import Namespace, Resource, fields, marshal_with
from controller.schedule import create, read, update, delete, update_detail, update_multi_detail

schedule_ns = Namespace('schedule', description='Schedule operations')

@schedule_ns.route('')
class ScheduleList(Resource):
    @schedule_ns.doc('create_schedule',
                     responses={
                         201: ('Success', schedule_ns.model('CreateResponse', {
                             'code': fields.Integer(description='Response code'),
                             'msg': fields.String(description='Response message'),
                             'id': fields.Integer(description='Created Schedule ID')
                         })),
                         404: ('Entity not found', schedule_ns.model('ErrorResponse', {
                             'code': fields.Integer(description='Error code'),
                             'msg': fields.String(description='Error message')
                         })),
                         500: ('Database error', schedule_ns.model('ErrorResponse', {
                             'code': fields.Integer(description='Error code'),
                             'msg': fields.String(description='Error message')
                         }))
                     })
    @schedule_ns.expect(schedule_ns.model('ScheduleInput', {
        'festoMainId': fields.Integer(required=True, description='Festo main ID'),
        'formulaId': fields.Integer(required=True, description='Formula ID'),
        'pid': fields.Integer(required=True, description='PID')
    }))
    def post(self):
        data = schedule_ns.payload
        result, status = create(data)
        return result, status

@schedule_ns.route('/<int:schedule_id>')
class Schedule(Resource):
    @schedule_ns.doc('get_schedule',
                     responses={
                         200: ('Success', schedule_ns.model('ScheduleResponse', {
                             'code': fields.Integer(description='Response code'),
                             'msg': fields.String(description='Response message'),
                             'data': fields.Nested(schedule_ns.model('ScheduleData', {
                                 'id': fields.Integer(description='Schedule ID'),
                                 'festoMainId': fields.Integer(description='Festo main ID'),
                                 'pidId': fields.Integer(description='PID ID'),
                                 'scheduleDetails': fields.List(fields.Nested(schedule_ns.model('ScheduleDetailItem', {
                                     'id': fields.Integer(description='Detail ID'),
                                     'pressure': fields.Float(description='Pressure'),
                                     'sequence': fields.Integer(description='Sequence'),
                                     'processTime': fields.Integer(description='Process time'),
                                     'timeStart': fields.String(description='Time start'),
                                     'timeEnd': fields.String(description='Time end'),
                                     'resetTimes': fields.Integer(description='Reset times')
                                 })))
                             }))
                         })),
                         404: ('Schedule not found', schedule_ns.model('ErrorResponse', {
                             'code': fields.Integer(description='Error code'),
                             'msg': fields.String(description='Error message')
                         })),
                         500: ('Database error', schedule_ns.model('ErrorResponse', {
                             'code': fields.Integer(description='Error code'),
                             'msg': fields.String(description='Error message')
                         }))
                     })
    def get(self, schedule_id):
        result, status = read(schedule_id)
        return result, status

    @schedule_ns.doc('update_schedule',
                     responses={
                         200: ('Success', schedule_ns.model('SuccessResponse', {
                             'code': fields.Integer(description='Response code'),
                             'msg': fields.String(description='Response message')
                         })),
                         404: ('Schedule not found', schedule_ns.model('ErrorResponse', {
                             'code': fields.Integer(description='Error code'),
                             'msg': fields.String(description='Error message')
                         })),
                         500: ('Database error', schedule_ns.model('ErrorResponse', {
                             'code': fields.Integer(description='Error code'),
                             'msg': fields.String(description='Error message')
                         }))
                     })
    @schedule_ns.expect(schedule_ns.model('ScheduleUpdate', {
        'festoMainId': fields.Integer(description='Festo main ID'),
        'pidId': fields.Integer(description='PID ID'),
        'formulaId': fields.Integer(description='Formula ID')
    }))
    def patch(self, schedule_id):
        data = schedule_ns.payload
        result, status = update(schedule_id, data)
        return result, status

    @schedule_ns.doc('delete_schedule',
                     responses={
                         200: ('Success', schedule_ns.model('SuccessResponse', {
                             'code': fields.Integer(description='Response code'),
                             'msg': fields.String(description='Response message')
                         })),
                         404: ('Schedule not found', schedule_ns.model('ErrorResponse', {
                             'code': fields.Integer(description='Error code'),
                             'msg': fields.String(description='Error message')
                         })),
                         500: ('Database error', schedule_ns.model('ErrorResponse', {
                             'code': fields.Integer(description='Error code'),
                             'msg': fields.String(description='Error message')
                         }))
                     })
    def delete(self, schedule_id):
        result, status = delete(schedule_id)
        return result, status

@schedule_ns.route('/detail/<int:schedule_detail_id>')
class ScheduleDetail(Resource):
    @schedule_ns.doc('update_schedule_detail',
                     responses={
                         200: ('Success', schedule_ns.model('SuccessResponse', {
                             'code': fields.Integer(description='Response code'),
                             'msg': fields.String(description='Response message')
                         })),
                         404: ('Schedule detail not found', schedule_ns.model('ErrorResponse', {
                             'code': fields.Integer(description='Error code'),
                             'msg': fields.String(description='Error message')
                         })),
                         500: ('Database error', schedule_ns.model('ErrorResponse', {
                             'code': fields.Integer(description='Error code'),
                             'msg': fields.String(description='Error message')
                         }))
                     })
    @schedule_ns.expect(schedule_ns.model('ScheduleDetailUpdate', {
        'pressure': fields.Float(description='Pressure'),
        'processTime': fields.Integer(description='Process time'),
        'sequence': fields.Integer(description='Sequence'),
        'status': fields.Integer(description='Status'),
        'checkPressure': fields.Integer(description='Check pressure'),
        'timeStart': fields.String(description='Time start'),
        'timeEnd': fields.String(description='Time end')
    }))
    def patch(self, schedule_detail_id):
        data = schedule_ns.payload
        result, status = update_detail(schedule_detail_id, data)
        return result, status

@schedule_ns.route('/detail')
class ScheduleDetailMulti(Resource):
    @schedule_ns.doc('update_schedule_detail_multi',
                     responses={
                         200: ('Success', schedule_ns.model('SuccessResponse', {
                             'code': fields.Integer(description='Response code'),
                             'msg': fields.String(description='Response message')
                         })),
                         404: ('Schedule detail not found', schedule_ns.model('ErrorResponse', {
                             'code': fields.Integer(description='Error code'),
                             'msg': fields.String(description='Error message')
                         })),
                         500: ('Database error', schedule_ns.model('ErrorResponse', {
                             'code': fields.Integer(description='Error code'),
                             'msg': fields.String(description='Error message')
                         }))
                     })
    @schedule_ns.expect(schedule_ns.model('ScheduleDetailMultiUpdate', {
        'details': fields.List(fields.Nested(schedule_ns.model('ScheduleDetailUpdateItem', {
            'id': fields.Integer(description='Detail ID'),
            'pressure': fields.Float(description='Pressure'),
            'processTime': fields.Integer(description='Process time'),
            'status': fields.Integer(description='Status'),
            'checkPressure': fields.Integer(description='Check pressure')
        })))
    }))
    def patch(self):
        data = schedule_ns.payload
        result, status = update_multi_detail(data)
        return result, status
