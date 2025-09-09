
from flask_socketio import join_room, leave_room, Namespace


from flask_socketio import Namespace, join_room, leave_room


def createSocketManager(socketio):

    class Phase1Namespace(Namespace):
        def on_join(self, data):
            print('joining room', data)
            join_room(data['room'])

        def on_leave(self, data):
            print('leaving room', data)
            leave_room(data['room'])

    class Phase2Namespace(Namespace):
        def on_join(self, data):
            print('joining room', data)
            join_room(data['room'])

        def on_leave(self, data):
            print('leaving room', data)
            leave_room(data['room'])

    socketio.on_namespace(Phase1Namespace('/phase1'))
    socketio.on_namespace(Phase2Namespace('/phase2'))
