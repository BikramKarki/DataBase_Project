import db
import config
import pyorient
import pymongo
import json

def get_team_info():
    team_info = {
        "team_name": "AABI",
        "team_member_sids": [12312761, 12628964],
        "app_status_code": 1
    }
    return team_info
import pyorient
import config
import pymongo

def reset_database():
    # OrientDB configuration
    dbname = config.ORIENTDB_DB_NAME
    login = config.ORIENTDB_USERNAME
    password = config.ORIENTDB_PASSWORD

    # MongoDB configuration
    mongodb_uri = config.MONGODB_URI
    mongodb_db_name = config.MONGODB_DB_NAME

    # Connect to OrientDB
    client_orientdb = pyorient.OrientDB("localhost", 2424)
    session_id = client_orientdb.connect(login, password)

    # Connect to MongoDB
    client_mongodb = pymongo.MongoClient(mongodb_uri)

    try:
        # Check if OrientDB database exists
        if client_orientdb.db_exists(dbname):
            # Open the database
            client_orientdb.db_open(dbname, login, password)

            # Delete data from the Patient class
            client_orientdb.command("DELETE VERTEX Patient")
        else:
            # If the database doesn't exist, create it
            db.create_database(client_orientdb)

        # Reset MongoDB database
        client_mongodb.drop_database(mongodb_db_name)

        return {"reset_status_code": 1}
    except Exception as e:
        print(f"Error while resetting databases: {e}")
        return {"reset_status_code": 0}
    finally:
        client_orientdb.close()
        client_mongodb.close()

def get_zip_alert_list():
    orientdb_client = db.connect_orientdb()

    # Query to get the latest batch_id
    latest_batch_id = orientdb_client.query("SELECT max(batch_id) as max_batch_id FROM Patient")[0].oRecordData['max_batch_id']

    # Check if there are at least 2 batches to compare
    if latest_batch_id < 1:
        return jsonify(ziplist=[])

    # Get the patient count per zipcode for the last two batches
    patient_count_last_two_batches = orientdb_client.query(f"""
        SELECT patient_zipcode, batch_id, count(*) as patient_count
        FROM Patient
        WHERE batch_id >= {latest_batch_id - 1} AND patient_status = 1
        GROUP BY patient_zipcode, batch_id
    """)

    count_new_batch = 0
    count_old_batch = 0
    new_batch_zipcodes = set()
    for entry in patient_count_last_two_batches:
        # zipcode = entry.oRecordData['patient_zipcode']
        batch_id = entry.oRecordData['batch_id']
        count = entry.oRecordData['patient_count']
        zipcode = entry.oRecordData['patient_zipcode']
        if batch_id == latest_batch_id:
            new_batch_zipcodes.add(zipcode)
            count_new_batch += 1
        else:
            count_old_batch += 1
    return list(new_batch_zipcodes)
    # if count_old_batch * 2 <= count_new_batch:
    #     return list(new_batch_zipcodes)
    # else:
    #     return []


def get_alert_status():
    # Get the list of zipcodes in alert status
    ziplist = get_zip_alert_list()

    # Check if there are at least five zipcodes in alert status
    state_status = 1 if len(ziplist) >= 5 else 0

    return state_status




def get_confirmed_contacts(client, mrn):
    # Get the contact list for the patient with the given MRN
    result = client.query(f"SELECT contact_list FROM Patient WHERE patient_mrn = '{mrn}'")
    if result:
        contact_list = result[0].contact_list
    else:
        return []

    # Get the MRNs of the patients where the given patient is in their contact list
    other_patients_with_given_mrn = client.query(f"SELECT patient_mrn FROM Patient WHERE '{mrn}' IN contact_list")

    # Add the MRNs of these patients to the contact_list
    for patient in other_patients_with_given_mrn:
        other_patient_mrn = patient.patient_mrn
        if other_patient_mrn not in contact_list:
            contact_list.append(other_patient_mrn)

    return contact_list



def get_possible_contacts(client, mrn):
    events = client.query(f"SELECT event_list FROM Patient WHERE patient_mrn = '{mrn}'")
    if events:
        event_list = events[0].event_list
        contacts = []
        for event_id in event_list:
            attendees = client.query(f"SELECT patient_mrn FROM Patient WHERE event_list CONTAINS '{event_id}'")
            contacts.append({event_id: [attendee.patient_mrn for attendee in attendees if attendee.patient_mrn != mrn]})
        return contacts
    else:
        return []


def get_patient_status(mongo_client, hospital_id):
    hospital_data_collection = mongo_client[config.MONGODB_DB_NAME]["HospitalData"]
    vax_data_collection = mongo_client[config.MONGODB_DB_NAME]["VaxData"]
    print(hospital_id)
    pipeline = [
    {"$match": {"hospital_id": hospital_id}},
    {"$group": {
        "_id": "$patient_status",
        "count": {"$sum": 1},
        "patients": {"$push": "$patient_mrn"}
    }},
    {"$project": {
        "patient_status": "$_id",
        "count": 1,
        "patients": 1,
        "_id": 0
    }}
    ]


    hospital_summary = list(hospital_data_collection.aggregate(pipeline))
    summary = {1: {"count": 0, "vax": 0}, 2: {"count": 0, "vax": 0}, 3: {"count": 0, "vax": 0}}
    print(hospital_summary)
    for item in hospital_summary:
        # print(item)
        status = item["patient_status"]
        count = item["count"]
        patients = item["patients"]

        vax_count = vax_data_collection.count_documents({"patient_mrn": {"$in": patients}})
        vax_rate = vax_count / count if count > 0 else 0

        summary[status]["count"] = count
        summary[status]["vax"] = vax_rate

    return summary

def get_all_patient_status(mongo_client):
    hospital_data_collection = mongo_client[config.MONGODB_DB_NAME]["HospitalData"]
    vax_data_collection = mongo_client[config.MONGODB_DB_NAME]["VaxData"]
    
    pipeline = [
        {
            "$group": {
                "_id": "$patient_status",
                "count": {"$sum": 1},
                "patients": {"$push": "$patient_mrn"}
            }
        }
    ]
    summary = hospital_data_collection.aggregate(pipeline)

    result = {1: {"count": 0, "vax": 0}, 2: {"count": 0, "vax": 0}, 3: {"count": 0, "vax": 0}}

    for item in summary:
        status = item["_id"]
        count = item["count"]
        patients = item["patients"]

        vax_count = vax_data_collection.count_documents({"patient_mrn": {"$in": patients}})
        vax_rate = round(vax_count / count, 2) if count > 0 else 0

        result[status]["count"] = count
        result[status]["vax"] = vax_rate

    return result







