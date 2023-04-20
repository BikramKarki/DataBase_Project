import pyorient
import config
import pymongo
import json
# docker run -d --name mongodb -p 27017:27017 -e MONGO_INITDB_ROOT_USERNAME=root -e MONGO_INITDB_ROOT_PASSWORD=rootpwd mongo:latest
def connect_mongodb():
    mongo_client = pymongo.MongoClient(config.MONGODB_URI)
    mongo_db = mongo_client[config.MONGODB_DB_NAME]
    return mongo_client

def create_collections(mongo_db):
    # Create the HospitalData collection
    hospital_data_collection = mongo_db["HospitalData"]

    # Create the VaxData collection
    vax_data_collection = mongo_db["VaxData"]

    return hospital_data_collection, vax_data_collection

def insert_hospital_data(collection, payload):
    try:
        for data in payload:
            if 'hospital_id' not in data or 'patient_mrn' not in data or 'patient_name' not in data or 'patient_status' not in data:
                print("Incomplete hospital data, skipping.")
                continue
            # print(f"Inserting hospital data: {data}")
            collection.insert_one(data)
    except Exception as e:
        print(f"Error while inserting hospital data: {e}")


def insert_vax_data(collection, payload):
    try:
        for data in payload:
            if 'vaccination_id' not in data or 'patient_mrn' not in data or 'patient_name' not in data:
                print("Incomplete vaccination data, skipping.")
                continue
            # print(f"Inserting vax data: {data}")
            collection.insert_one(data)
    except Exception as e:
        print(f"Error while inserting vaccination data: {e}")

def create_mongodb_database(client):
    # Create collections for Hospital and Vaccination data
    hospital_collection = client[config.MONGODB_DB_NAME]["hospital_data"]
    vaccination_collection = client[config.MONGODB_DB_NAME]["vaccination_data"]

def connect_orientdb():
    client = pyorient.OrientDB(config.ORIENTDB_HOST, config.ORIENTDB_PORT)
    client.connect(config.ORIENTDB_USERNAME, config.ORIENTDB_PASSWORD)
    
    # Open the database
    if client.db_exists(config.ORIENTDB_DB_NAME, pyorient.STORAGE_TYPE_PLOCAL):
        print("database exist")
        client.db_open(config.ORIENTDB_DB_NAME, config.ORIENTDB_USERNAME, config.ORIENTDB_PASSWORD)
    else:
        print("Database does not exist. Creating the database...")
        create_database(client)
        client.db_open(config.ORIENTDB_DB_NAME, config.ORIENTDB_USERNAME, config.ORIENTDB_PASSWORD)

    return client


def create_database(client):
    # Check if the database exists, create it if it doesn't
    if not client.db_exists(config.ORIENTDB_DB_NAME, pyorient.STORAGE_TYPE_PLOCAL):
        client.db_create(config.ORIENTDB_DB_NAME, pyorient.DB_TYPE_GRAPH, pyorient.STORAGE_TYPE_PLOCAL)
    
    # Switch to the created database
    open_db = client.db_open(config.ORIENTDB_DB_NAME, config.ORIENTDB_USERNAME, config.ORIENTDB_PASSWORD)
    create_schema(client)

def create_schema(client):
    print("Creating schema...")
    # Create the Patient class
    if not client.command("SELECT FROM ( SELECT expand( classes ) FROM metadata:schema ) WHERE name = 'Patient'"):
        client.command("CREATE CLASS Patient EXTENDS V")
        client.command("CREATE PROPERTY Patient.testing_id INTEGER")
        client.command("CREATE PROPERTY Patient.patient_mrn STRING")
        client.command("CREATE PROPERTY Patient.patient_name STRING")
        client.command("CREATE PROPERTY Patient.patient_zipcode INTEGER")
        client.command("CREATE PROPERTY Patient.patient_status INTEGER")
        client.command("CREATE PROPERTY Patient.contact_list EMBEDDEDLIST STRING")
        client.command("CREATE PROPERTY Patient.event_list EMBEDDEDLIST STRING")



def insert_patient_data(client, payload):
    try:
        for data in payload:
            if 'testing_id' not in data or 'patient_mrn' not in data or 'patient_name' not in data or \
               'patient_zipcode' not in data or 'patient_status' not in data or \
               'contact_list' not in data or 'event_list' not in data:
                print("Incomplete patient data, skipping.")
                continue
            # print(client)
            client.command(f"""
            INSERT INTO Patient
            SET testing_id = {data['testing_id']},
                patient_mrn = '{data['patient_mrn']}',
                patient_name = '{data['patient_name']}',
                patient_zipcode = {data['patient_zipcode']},
                patient_status = {data['patient_status']},
                contact_list = {json.dumps(data['contact_list'])},
                event_list = {json.dumps(data['event_list'])}
            """)
    except Exception as e:
        print(f"Error while inserting patient data: {e}")


