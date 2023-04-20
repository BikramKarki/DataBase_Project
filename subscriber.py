#!/usr/bin/env python
import pika
import sys
import json
import db
import config
username = 'team_10'
password = 'myPassCS505'
hostname = 'vbu231.cs.uky.edu'
virtualhost = '10'

credentials = pika.PlainCredentials(username, password)
parameters = pika.ConnectionParameters(hostname, 5672, virtualhost, credentials)

connection = pika.BlockingConnection(parameters)
channel = connection.channel()

# Create MongoDB connection and collections
mongo_db = db.connect_mongodb()
mongodb_db = mongo_db[config.MONGODB_DB_NAME]
hospital_data_collection, vax_data_collection = db.create_collections(mongodb_db)

def create_channel_binding(exchange_name, binding_key='#'):
    channel.exchange_declare(exchange=exchange_name, exchange_type='topic')

    result = channel.queue_declare('', exclusive=True)
    queue_name = result.method.queue

    channel.queue_bind(
        exchange=exchange_name, queue=queue_name, routing_key=binding_key)
    
    return queue_name

# Create channels and bindings for patient_list, hospital_list, and vax_list exchanges
patient_list_queue = create_channel_binding('patient_list')
hospital_list_queue = create_channel_binding('hospital_list')
vax_list_queue = create_channel_binding('vax_list')

print(' [*] Waiting for logs. To exit press CTRL+C')

def callback_patient(ch, method, properties, body):
    # print(" [x] %r:%r" % (method.routing_key, body))
    data = json.loads(body)
    print("Inserting patient")
    orientdb_client = db.connect_orientdb()
    db.insert_patient_data(orientdb_client, data);

    
    
def callback_hospital(ch, method, properties, body):
    data = json.loads(body)
    print("inserting hospital")
    db.insert_hospital_data(hospital_data_collection, data)
   

def callback_vax(ch, method, properties, body):
    data = json.loads(body)
    print("inserting vax")
    db.insert_vax_data(vax_data_collection, data)
    
channel.basic_consume(
    queue=patient_list_queue, on_message_callback=callback_patient, auto_ack=True)
channel.basic_consume(
    queue=hospital_list_queue, on_message_callback=callback_hospital, auto_ack=True)
channel.basic_consume(
    queue=vax_list_queue, on_message_callback=callback_vax, auto_ack=True)

channel.start_consuming()
