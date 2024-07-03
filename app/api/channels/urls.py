from flask import request, Blueprint

channels_bp = Blueprint('channels', __name__)

from app.api.channels.controllers import (delete_channel_controller, update_channel_controller,
                                          retrieve_channels_controller, create_channel_controller,
                                          list_all_channels_controller)


@channels_bp.route("/channels", methods=['GET', 'POST'])
def list_create_channels():
    if request.method == 'GET': return list_all_channels_controller()
    if request.method == 'POST':
        return create_channel_controller()
    else:
        return 'Method is Not Allowed'


@channels_bp.route("/channels/<ch_id>", methods=['GET', 'PUT', 'DELETE'])
def retrieve_update_destroy_channel(ch_id):
    if request.method == 'GET': return retrieve_channels_controller(ch_id)
    if request.method == 'PUT': return update_channel_controller(ch_id)
    if request.method == 'DELETE':
        return delete_channel_controller(ch_id)
    else:
        return 'Method is Not Allowed'

