import pika
import json
import db
import config

def process_message(ch, method, properties, body):
    data = json.loads(body)
    print("Data received:", data)  # Print the data received
    orientdb_client = db.connect_orientdb()
    if method.routing_key == 'patient_list':
        db.insert_patient_data(orientdb_client, data)
        # print("patient_data_inserted")
    elif method.routing_key == 'hospital_list':
        db.insert_hospital_data(orientdb_client, data)
        # print("hospital_list_inserted")
    elif method.routing_key == 'vax_list':
        db.insert_vaccination_data(orientdb_client, data)
        # print("vax_list_inserted")
    orientdb_client.db_close()

# RabbitMQ connection parameters
username = config.RABBITMQ_USERNAME
password = config.RABBITMQ_PASSWORD
hostname = config.RABBITMQ_HOST
virtualhost = '10'

def start_consumer():
    # Set up RabbitMQ connection
    credentials = pika.PlainCredentials(username, password)
    parameters = pika.ConnectionParameters(host=hostname, virtual_host=virtualhost, credentials=credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    # Declare the exchange
    exchange_name_1 = 'patient_list'  # Use the same exchange name as in the producer
    channel.exchange_declare(exchange=exchange_name_1, exchange_type='topic')

    # Create the queues and bind them to the exchange with the routing keys
    for queue_name, routing_key in [('patient_queue', 'patient_list'), ('hospital_queue', 'hospital_list'), ('vaccination_queue', 'vax_list')]:
        channel.queue_declare(queue=queue_name)
        channel.queue_bind(exchange=exchange_name_1, queue=queue_name, routing_key=routing_key)
        channel.basic_consume(queue=queue_name, on_message_callback=process_message, auto_ack=True)

    exchange_name_2 = 'hospital_list'  # Use the same exchange name as in the producer
    channel.exchange_declare(exchange=exchange_name_2, exchange_type='topic')

       # Create the queues and bind them to the exchange with the routing keys
    for queue_name, routing_key in [('patient_queue', 'patient_list'), ('hospital_queue', 'hospital_list'), ('vaccination_queue', 'vax_list')]:
        channel.queue_declare(queue=queue_name)
        channel.queue_bind(exchange=exchange_name_2, queue=queue_name, routing_key=routing_key)
        channel.basic_consume(queue=queue_name, on_message_callback=process_message, auto_ack=True)
    
    exchange_name_3 = 'vax_list'  # Use the same exchange name as in the producer
    channel.exchange_declare(exchange=exchange_name_3, exchange_type='topic')
     # Create the queues and bind them to the exchange with the routing keys
    for queue_name, routing_key in [('patient_queue', 'patient_list'), ('hospital_queue', 'hospital_list'), ('vaccination_queue', 'vax_list')]:
        channel.queue_declare(queue=queue_name)
        channel.queue_bind(exchange=exchange_name_3, queue=queue_name, routing_key=routing_key)
        channel.basic_consume(queue=queue_name, on_message_callback=process_message, auto_ack=True)


    print("Consumer is now waiting for data from the queues...")

    # Start consuming data
    channel.start_consuming()

