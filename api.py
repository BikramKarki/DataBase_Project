import db
import config
import pyorient
import pymongo
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


def get_zip_alert_list(client):
   pass

def get_state_alert_status(client):
    pass
def get_confirmed_contacts(client, mrn):
    result = client.query(f"SELECT contact_list FROM Patient WHERE patient_mrn = '{mrn}'")
    if result:
        return result[0].contact_list
    else:
        return []


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


def get_patient_status(client, hospital_id):
    query = f"SELECT patient_status, COUNT(*) as count FROM HospitalPatient WHERE hospital_id = {hospital_id} GROUP BY patient_status"
    results = client.query(query)

    patient_status = {
        "in-patient_count": 0,
        "in-patient_vax": 0,
        "icu-patient_count": 0,
        "icu_patient_vax": 0,
        "patient_vent_count": 0,
        "patient_vent_vax": 0
    }

    for result in results:
        status = result.patient_status
        count = result.count

        if status == 1:
            patient_status["in-patient_count"] = count
        elif status == 2:
            patient_status["icu-patient_count"] = count
        elif status == 3:
            patient_status["patient_vent_count"] = count

    # Calculate the percentages of vaccinated patients for each patient category
    # You might need to adjust this query based on your data schema
    query = f"""
    SELECT patient_status, COUNT(*) as vax_count
    FROM HospitalPatient
    WHERE hospital_id = {hospital_id} AND patient_mrn IN (SELECT patient_mrn FROM Vaccination)
    GROUP BY patient_status
    """
    results = client.query(query)

    for result in results:
        status = result.patient_status
        count = result.vax_count

        if status == 1:
            patient_status["in-patient_vax"] = count / patient_status["in-patient_count"]
        elif status == 2:
            patient_status["icu_patient_vax"] = count / patient_status["icu-patient_count"]
        elif status == 3:
            patient_status["patient_vent_vax"] = count / patient_status["patient_vent_count"]

    return patient_status

def get_all_patient_status(client):
    query = "SELECT patient_status, COUNT(*) as count FROM HospitalPatient GROUP BY patient_status"
    results = client.query(query)

    patient_status = {
        "in-patient_count": 0,
        "in-patient_vax": 0,
        "icu-patient_count": 0,
        "icu_patient_vax": 0,
        "patient_vent_count": 0,
        "patient_vent_vax": 0
    }

    for result in results:
        status = result.patient_status
        count = result.count

        if status == 1:
            patient_status["in-patient_count"] = count
        elif status == 2:
            patient_status["icu-patient_count"] = count
        elif status == 3:
            patient_status["patient_vent_count"] = count

    # Calculate the percentages of vaccinated patients for each patient category
    # You might need to adjust this query based on your data schema
    query = """
    SELECT patient_status, COUNT(*) as vax_count
    FROM HospitalPatient
    WHERE patient_mrn IN (SELECT patient_mrn FROM Vaccination)
    GROUP BY patient_status
    """
    results = client.query(query)

    for result in results:
        status = result.patient_status
        count = result.vax_count

        if status == 1:
            patient_status["in-patient_vax"] = count / patient_status["in-patient_count"]
        elif status == 2:
            patient_status["icu_patient_vax"] = count / patient_status["icu-patient_count"]
        elif status == 3:
            patient_status["patient_vent_vax"] = count / patient_status["patient_vent_count"]

    return patient_status

