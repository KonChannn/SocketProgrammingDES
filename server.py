
import socketio
import eventlet
from eventlet import wsgi

sio = socketio.Server()
app = socketio.WSGIApp(sio)

@sio.event
def connect(sid, environ):
    print(f'User connected: {sid}')
    sio.emit('message', {'msg': f'User {sid} has entered the chat!'}, to=sid)

@sio.event
def message(sid, data):
    print(f'Received message from {sid}: {data["msg"]}')
    sio.emit('message', {'msg': f'{sid}: {data["msg"]}'}, skip_sid=sid)

@sio.event
def disconnect(sid):
    print(f'User disconnected: {sid}')
    sio.emit('message', {'msg': f'User {sid} has left the chat.'})

if __name__ == '__main__':
    print("Chat server started on http://localhost:5000")
    wsgi.server(eventlet.listen(('', 5000)), app)
