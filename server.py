from flask import Flask, request, jsonify
import room
from error_types import GameError
from settings import reponse_status

ROOMS = {}




app = Flask(__name__)

@app.route("/create_room/<room_name>", methods = ["POST"])
def create_room(room_name):
    try:
        params = request.get_json()
        ROOMS[room_name] = room.Room(room_name, params["holder_name"])
        holderid = ROOMS[room_name].holder
        return jsonify(
            {
                "code": reponse_status.success_status,
                "holderid": holderid
            }
        )
    except GameError as ge:
        return jsonify(
            {
                "code": ge.code,
                "msg": ge.msg
            }
        )
    except Exception as e:
        return jsonify({
            "code": reponse_status.error_status,
            "msg": str(e)
        })


