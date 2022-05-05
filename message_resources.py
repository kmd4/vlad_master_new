from flask import jsonify
from flask_restful import Resource, abort, Api, reqparse
from data import db_session
from data.messages import Messages


def abort_if_message_not_found(message_id):
    session = db_session.create_session()
    news = session.query(Messages).get(message_id)
    if not news:
        abort(404, message=f"Messages {message_id} not found")


class MessageResource(Resource):
    def get(self, message_id):
        abort_if_message_not_found(message_id)
        session = db_session.create_session()
        mes = session.query(Messages).get(message_id)
        return jsonify({'messages': mes.to_dict(
            only=('room', 'content', 'created_date', 'user_id'))})


class DialogsResourse(Resource):
    def get(self, room):
        session = db_session.create_session()
        mes = session.query(Messages).get(room).all()
        return jsonify({'messages': [item.to_dict(
            only=('created_date', 'content', 'user_id')) for item in mes]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        mes = Messages(
            room=args['room'],
            content=args['content'],
            user_id=args['user_id'],
            created_date=args['created_date'],
        )
        session.add(mes)
        session.commit()
        return jsonify({'success': 'OK'})


parser = reqparse.RequestParser()
parser.add_argument('room', required=True)
parser.add_argument('content', required=True)
parser.add_argument('created_date', required=True)
parser.add_argument('user_id', required=True, type=int)
