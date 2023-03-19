# from aiohttp import web
# import socketio
#
# sio = socketio.AsyncServer(async_mode='sanic', cors_allowed_origins='*')
# app = web.Application()
# sio.attach(app)
#
# room = []
#
# async def index(request):
#     """Serve the client-side application."""
#     with open('index.html') as f:
#         return web.Response(text=f.read(), content_type='text/html')
#
#
# @sio.event
# def connect(sid, environ):
#     print('connect ', sid)
#     room.append(sid)
#
# @sio.event
# def my_message(sid, data):
#     print('message ', data)
#     for pid in room:
#         socketio.Server.send(sio, f"房间有{len(room)}个人", skip_sid=pid)
#         sio.call("my_message", f"有人加入了，房间有{len(room)}个人", sid=pid)
#
# @sio.event
# def disconnect(sid):
#     print('disconnect ', sid)
#     room.remove(sid)
#     for pid in room:
#         sio.call("my_message", f"有人离开了，房间有{len(room)}个人", sid=pid)
#
#
# # app.router.add_static('/static', 'static')
# # app.router.add_get('/', index)
#
# if __name__ == '__main__':
#     web.run_app(app)



from aiohttp import web
import socketio

sio = socketio.AsyncServer(cors_allowed_origins='*')    # 跨域
app = web.Application()
sio.attach(app)


room = []

async def index(request):
    """Serve the client-side application."""
    with open('index.html') as f:
        return web.Response(text=f.read(), content_type='text/html')



@sio.event
def connect(sid, environ):
    print('connect ', sid)
    room.append(sid)

@sio.event
async def my_message(sid, data):
    print('message ', data)
    for pid in room:
        await sio.call("message", "一共n人", sid=pid)

@sio.event
def disconnect(sid):
    print('disconnect ', sid)
    room.remove(sid)
    for pid in room:
        sio.call("my_message", f"有人离开了，房间有{len(room)}个人", sid=pid)

# app.router.add_static('/static', 'static')
app.router.add_get('/', index)

if __name__ == '__main__':
    web.run_app(app, port=5000)
    # web.run_app(app)