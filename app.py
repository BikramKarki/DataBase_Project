from flask import Flask, jsonify, request
from db import (connect_orientdb, create_database, insert_patient_data,
                connect_mongodb, create_collections)
import api

app = Flask(__name__)
orientdb_client = connect_orientdb()
mongo_db = connect_mongodb()
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
    ziplist = api.get_zip_alert_list()
    return jsonify({"ziplist": ziplist})

@app.route('/api/alertlist', methods=['GET'])
def alert_list():
    state_status = api.get_alert_status()
    return jsonify(state_status=state_status)

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
    patient_status = api.get_patient_status(mongo_db, hospital_id)
    return jsonify({
        "in-patient_count": patient_status[1]["count"],
        "in-patient_vax": patient_status[1]["vax"],
        "icu-patient_count": patient_status[2]["count"],
        "icu_patient_vax": patient_status[2]["vax"],
        "patient_vent_count": patient_status[3]["count"],
        "patient_vent_vax": patient_status[3]["vax"],
    })

@app.route('/api/getpatientstatus', methods=['GET'])
def get_all_patient_status_route():
    patient_status = api.get_all_patient_status(mongo_db)
    return jsonify({
        "in-patient_count": patient_status[1]["count"],
        "in-patient_vax": patient_status[1]["vax"],
        "icu-patient_count": patient_status[2]["count"],
        "icu_patient_vax": patient_status[2]["vax"],
        "patient_vent_count": patient_status[3]["count"],
        "patient_vent_vax": patient_status[3]["vax"],
    })

if __name__ == "__main__":
    # orientdb_client = connect_orientdb()
    create_database(orientdb_client)
    hospital_data_collection, vax_data_collection = create_collections(mongo_db) 
    app.run(host="0.0.0.0", port=9999)    
    orientdb_client.db_close()
