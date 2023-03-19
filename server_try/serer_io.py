import eventlet
import socketio

sio = socketio.Server()
app = socketio.WSGIApp(sio)

room = []


@sio.event
def connect(sid, environ):
    print('connect ', sid)
    room.append(sid)

@sio.event
def my_message(sid, data):
    print('message ', data)
    for pid in room:
        socketio.Server.send(sio, f"房间有{len(room)}个人", skip_sid=pid)
        sio.call("my_message", f"有人加入了，房间有{len(room)}个人", sid=pid)

@sio.event
def disconnect(sid):
    print('disconnect ', sid)
    room.remove(sid)
    for pid in room:
        sio.call("my_message", f"有人离开了，房间有{len(room)}个人", sid=pid)

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)
