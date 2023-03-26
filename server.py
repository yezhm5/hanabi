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
import room
from error_types import GameError, RoomError
from settings import reponse_status
from define import *

sio = socketio.AsyncServer(cors_allowed_origins='*')    # 跨域
app = web.Application()
sio.attach(app)


room = {}   # 记录每个房间对象
sid_room = {}   # 记录每个sid进入哪个房间

async def index(request):
    """Serve the client-side application."""
    with open('index.html') as f:
        return web.Response(text=f.read(), content_type='text/html')



@sio.event
def connect(sid, environ):
    print('connect ', sid)
    room.append(sid)


@sio.event
async def create_room(sid, data):
    try:
        room_name = data['room_name']
        holder_name = data['holder_name']
        if room.get(room_name) is None:
            room[room_name] = room(room_name, holder_name, sid)
            msg_data = {"code": reponse_status.success_status, "msg":"房间创建成功"}
            sid_room[sid] = room_name
            await sio.call("message", msg_data, sid=sid)
        else:
            raise RoomError(RoomError.ROOM_EXISTS)
    except GameError or RoomError as e:
        msg_data = {"code": e.code, "msg": e.msg}
        await sio.call("message", msg_data, sid=sid)
    except Exception as e:
        msg_data = {"code":reponse_status.error_status, "msg": str(e)}
        await sio.call("message", msg_data, sid=sid)


def send_room_msg(room_name, data, msg_type = "message"):
    for user_info in room[room_name].users:
        sid = user_info[0]
        if sid is not None:
            await sio.call(msg_type, data, sid)

def update_room_msg(room_name, data):
    for user_info in room[room_name].users:
        sid = user_info[0]
        if sid is not None:
            await sio.call("update", data, sid)

def send_game_info(room_name):
    room_object = room[room_name]
    game_object = room_object.game
    for playerid, user_info in room_object.player_connect:
        sid = user_info[0]
        if sid is not None:
            game_data = game_object.get_player_infomation(playerid)
            await sio.call("update", game_data, sid)

def delete_room_holder_leave(room_name):
    room_object = room[room_name]
    for user_info in room_object.users:
        sid = user_info[0]
        if sid_room.get(sid):
            del sid_room[sid]
        await sio.call('out', '房主离开，房间解散', sid)

    if room.get(room_name):
        del room[room_name]

def delete_room_disconnect(room_name):
    room_object = room[room_name]
    for playerid, user_info in room_object.player_connect.items():
        sid = user_info[0]
        if sid_room.get(sid):
            del sid_room[sid]
    if room.get(room_name):
        del room[room_name]

def player_disconnect(room_name, sid):
    del sid_room[sid]
    room_object = room[room_name]
    user_name = room_object.get_user_name(sid)
    response = {"code": reponse_status.success_status, "msg": f"玩家:{user_name} 失去了连接"}
    for playerid, user_info in room_object.player_connect:
        sid = user_info[0]
        if sid is not None:
            await sio.call("message", response, sid)

def player_reconnect(room_name, sid):
    sid_room[sid] = room_name
    room_object = room[room_name]
    user_name = room_object.get_user_name(sid)
    response = {"code": reponse_status.success_status, "msg": f"玩家:{user_name} 重新连接至游戏"}
    for playerid, user_info in room_object.player_connect:
        sid = user_info[0]
        if sid is not None:
            await sio.call("message", response, sid)

@sio.event
async def enter_room(sid, data):
    try:
        room_name = data["room_name"]
        user_name = data["user_name"]
        if room.get(room_name) is None:
            raise RoomError(RoomError.ROOM_NOT_EXISTS)
        else:
            room[room_name].enter_room(user_name, sid)
            sid_room[sid] = room_name
            msg_data = {
                "code": reponse_status.success_status,
                "msg": f"玩家{user_name}进入了房间"
            }
            send_room_msg(room_name, msg_data)
            update_data = {i:user_info[1] for i,user_info in enumerate(room[room_name].users)}
            update_room_msg(room_name, update_data)
    except GameError or RoomError as e:
        msg_data = {"code": e.code, "msg": e.msg}
        await sio.call("message", msg_data, sid=sid)
    except Exception as e:
        msg_data = {"code": reponse_status.error_status, "msg": str(e)}
        await sio.call("message", msg_data, sid=sid)


@sio.event
async def create_game(sid, data):
    '''
    房主开始游戏
    1.判断是否是房主
    2.开始游戏，集体发送游戏开始信息
    3.开始游戏，发送初始局面信息
    :param sid:
    :return:
    '''
    try:
        room_name = data["room_name"]
        if room.get(room_name) is None:
            raise RoomError(RoomError.ROOM_NOT_EXISTS)
        room_object = room["room_name"]
        if room_object.holderid != sid:
            raise RoomError(RoomError.NOT_HOLDER)
        
        game_type = data.get("game_type", NORMAL_GAME)
        tortime = data.get("tortime", 3)
        tiptime = data.get("tiptime", 8)
        
        room_object.create_game(game_type, tortime, tiptime)
        
        msg_data = {
            "code": reponse_status.success_status,
            "msg": "游戏开始"
        }
        send_room_msg(room_name, msg_data, msg_type="create_game")
        send_game_info(room_name)
    except GameError or RoomError as e:
        msg_data = {"code": e.code, "msg": e.msg}
        await sio.call("message", msg_data, sid=sid)
    except Exception as e:
        msg_data = {"code": reponse_status.error_status, "msg": str(e)}
        await sio.call("message", msg_data, sid=sid)

@sio.event
async def my_message(sid, data):
    print('message ', data)
    for pid in room:
        await sio.call("message", "一共n人", sid=pid)


@sio.event
async def reconnect(sid, data):
    try:
        room_name = data["room_name"]
        if room.get(room_name) is None:
            raise RoomError(RoomError.ROOM_NOT_EXISTS)
        else:
            room_object = room[room_name]
            playerid = data["playerid"]
            room_object.reconnect(sid, playerid)
            send_game_info(room_name)   # 给所有玩家重发游戏信息
    except GameError or RoomError as e:
        msg_data = {"code": e.code, "msg": e.msg}
        await sio.call("message", msg_data, sid=sid)
    except Exception as e:
        msg_data = {"code": reponse_status.error_status, "msg": str(e)}
        await sio.call("message", msg_data, sid=sid)


@sio.event
def disconnect(sid):
    '''
    1. 游戏未开始状态，删除该玩家
        1) 若该玩家是房主，直接解散房间
        2） 若该玩家不是房主，则移除玩家
    2. 游戏开始状态，发送离线信息，等待重连
    :param sid:
    :return:
    '''
    room_name = sid_room.get(sid)

    # 1. 未加入房间时，直接结束
    if room_name is None:
        return

    # 2. 加入房间后
    # sid_room表要删除对应的key
    room_object = room[room_name]
    if room_object.game_start is False:
        # 游戏未开始时，离开玩家若为房主则解散房间；否则移除玩家。
        if room_object.if_delete_room():
            delete_room_holder_leave(room_name)
            return
        else:
            room_object.leave_room(sid)
            del sid_room[sid]
            user_name = room_object.get_user_name(sid)
            msg_data = {
                "code": reponse_status.success_status,
                "msg": f"玩家{user_name}离开了房间"
            }
            send_room_msg(room_name, msg_data)
            update_data = {i: user_info[1] for i, user_info in enumerate(room[room_name].users)}
            update_room_msg(room_name, update_data)
            return
    else:
        # 游戏开始后，若单玩家掉线，需要等待。全部掉线则退出
        room_object.leave_room(sid)
        if room_object.if_delete_room():
            delete_room_disconnect(room_name)
        else:
            # 通知其他玩家该玩家掉线
            player_disconnect(room_name, sid)


@sio.event
async def turn_do(sid, data):
    try:
        do_type = data["do_type"]   # 操作类型，4种：color_tips, num_tips, drop_card, dis_card
        room_name = sid_room[sid]
        room_object = room[room_name]
        game = room_object.game
        playerid = room_object.get_playerid(sid)
        if playerid is None:
            raise RoomError(RoomError.PLAYERID_NOT_EXISTS)
        if do_type == "color_tips":
            replos = data["replos"]
            color = data["color"]
            game.color_tips(playerid, replos, color)
            msg = ""
        elif do_type == "num_tips":
            replos = data["replos"]
            num = data["num"]
            game.num_tips(playerid, replos, num)
            msg = ""
            pass
        elif do_type == "drop_card":
            card_replos = data["card_replos"]
            game.drop_card(playerid, card_replos)
            msg = ""
            pass
        elif do_type == "dis_card":
            card_replos = data["card_replos"]
            game.dis_card(playerid, card_replos)
            msg = ""
            pass
        else:
            raise GameError(GameError.DO_TYPE_NOT_EXISTS)

        send_room_msg(room_name, msg)
        send_game_info(room_name)   # 给所有玩家更新游戏信息
    except GameError or RoomError as e:
        msg_data = {"code": e.code, "msg": e.msg}
        await sio.call("message", msg_data, sid=sid)
    except Exception as e:
        msg_data = {"code": reponse_status.error_status, "msg": str(e)}
        await sio.call("message", msg_data, sid=sid)


# app.router.add_static('/static', 'static')
app.router.add_get('/', index)

if __name__ == '__main__':
    web.run_app(app, port=5000)
    # web.run_app(app)