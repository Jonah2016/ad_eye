import uuid

from flask import request, jsonify

from app import db
from app.api.channels.models import Channels


# ----------------------------------------------- #

# Query Object Methods => https://docs.sqlalchemy.org/en/14/orm/query.html#sqlalchemy.orm.Query
# Session Object Methods => https://docs.sqlalchemy.org/en/14/orm/session_api.html#sqlalchemy.orm.Session
# How to serialize SqlAlchemy MySQL Query to JSON => https://stackoverflow.com/a/46180522

def list_all_channels_controller():
    channel_data = Channels.query.all()
    # Convert the query results to a list of dictionaries
    response = [chan.toDict() for chan in channel_data]
    return jsonify(response)


def create_channel_controller():
    try:
        if request.form:
            request_form = request.form.to_dict()
        else:
            request_form = request.get_json()

        ch_id = str(uuid.uuid4())
        new_channel = Channels(
            ch_id=ch_id,
            ch_name=request_form.get('ch_name'),
            ch_number=request_form.get('ch_number'),
            ch_url=request_form.get('ch_url'),
            ch_record_dir=request_form.get('ch_record_dir'),
            ch_ip_address=request_form.get('ch_ip_address'),
            ch_port=request_form.get('ch_port'),
            ch_license=request_form.get('ch_license'),
            active_status=request_form.get('active_status'),
            modified=None,
            completed=None,
        )
        db.session.add(new_channel)
        db.session.commit()

        created_channel = Channels.query.filter_by(ch_id=ch_id).first()
        if created_channel is None:
            return jsonify({"error": "Failed to retrieve created channel record"}), 500

        response = created_channel.toDict()
        return jsonify(response)

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


def retrieve_channels_controller(ch_id):
    try:
        ch = Channels.query.filter_by(ch_id=ch_id).first()
        if ch is None:
            return jsonify({"error": "Channel record not found"}), 404

        response = ch.toDict()
        return jsonify(response)
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


def update_channel_controller(ch_id):
    try:
        if request.form:
            request_form = request.form.to_dict()
        else:
            request_form = request.get_json()

        ch = Channels.query.filter_by(ch_id=ch_id).first()
        if ch is None:
            return jsonify({"error": "Channel record not found"}), 404

        ch.ch_name = request_form['ch_name']
        ch.ch_number = request_form['ch_number']
        ch.ch_url = request_form['ch_url']
        ch.ch_record_dir = request_form['ch_record_dir']
        ch.ch_ip_address = request_form['ch_ip_address']
        ch.ch_port = request_form['ch_port']
        ch.ch_license = request_form['ch_license']
        ch.active_status = request_form['active_status']
        db.session.commit()

        updated_channel = Channels.query.filter_by(ch_id=ch_id).first()
        if updated_channel is None:
            return jsonify({"error": "Failed to retrieve updated channel record"}), 500

        response = updated_channel.toDict()
        return jsonify(response)

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


def delete_channel_controller(ch_id):
    Channels.query.filter_by(ch_id=ch_id).delete()
    db.session.commit()

    return 'Channel with Id "{}" deleted successfully!'.format(ch_id)
