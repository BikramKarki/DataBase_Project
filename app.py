from flask import Flask, jsonify, request
from db import (connect_orientdb, create_database, insert_patient_data,
                connect_mongodb, create_collections)
import consumer
import api
app = Flask(__name__)
orientdb_client = connect_orientdb()
# Management Functions
@app.route('/api/getteam', methods=['GET'])
def get_team():
    return jsonify(api.get_team_info())

@app.route('/api/reset', methods=['GET'])
def reset():
    reset_result = api.reset_database()
    return jsonify(reset_result)

@app.route('/api/zipalertlist', methods=['GET'])
def zip_alert_list():
    # Implement function: get_zip_alert_list(client)
    ziplist = api.get_zip_alert_list(client)
    return jsonify({"ziplist": ziplist})

@app.route('/api/alertlist', methods=['GET'])
def alert_list():
    # Implement function: get_state_alert_status(client)
    state_status = api.get_state_alert_status(client)
    return jsonify({"state_status": state_status})

@app.route('/api/getconfirmedcontacts/<mrn>', methods=['GET'])
def get_confirmed_contacts_route(mrn):
    # Implement function: get_confirmed_contacts(client, mrn)
    contactlist = api.get_confirmed_contacts(orientdb_client, mrn)
    return jsonify({"contactlist": contactlist})

@app.route('/api/getpossiblecontacts/<mrn>', methods=['GET'])
def get_possible_contacts_route(mrn):
    # Implement function: get_possible_contacts(client, mrn)
    contactlist = api.get_possible_contacts(orientdb_client, mrn)
    return jsonify({"contactlist": contactlist})

@app.route('/api/getpatientstatus/<hospital_id>', methods=['GET'])
def get_patient_status_route(hospital_id):
    # Implement function: get_patient_status(client, hospital_id)
    patient_status = get_patient_status(client, hospital_id)
    return jsonify(patient_status)

@app.route('/api/getpatientstatus', methods=['GET'])
def get_all_patient_status_route():
    # Implement function: get_all_patient_status(client)
    patient_status = get_all_patient_status(client)
    return jsonify(patient_status)

if __name__ == "__main__":
    # orientdb_client = connect_orientdb()
    create_database(orientdb_client)
    mongo_db = connect_mongodb()
    hospital_data_collection, vax_data_collection = create_collections(mongo_db) 
    app.run(host="0.0.0.0", port=8000)    
    orientdb_client.db_close()
