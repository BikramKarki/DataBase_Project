# DataBase_Project
# Application-to-support-COVID-19-management

## Details
The requirement for the final project was to develop a application that should provide real-time reporting, alerting, contact tracing, hospital, and state status in the state of Kentucky. There were specifically four functions required for the project viz. 1) Application Management Functions (MF1
and MF2), 2) Real Time Reporting functions (RTR1 and RTR 2) 3) Contact Tracing Functions(CT 1 and CT 2)and 3) Logic and Operational Functions (OF1 and OF2). Our team Team AABI has developed this real time reporting application as per the requirement set for the project. We have used Python Programming Language for the application and the choice of Database technology is OrientDB and MongoDB.

We chose to go with the OrientDB and MongoDB because since we were looking to implement a
non-traditional database system for our project which required realtime reporting and faster
querying. Furthermore, OrientDB enables ease of access to the database while still being adequate for sophisticated applications like this project because it supports key-value stores and has a query language similar to SQL. Along with parallelism, durability, and other features, OrientDB also fully supports ACID, and its Python API, pyorient, makes implementation much simpler. Mongodb stores data in json-like documents, which can be nested and have a variety of data types. It is a Schema less  database, which means that it does not enforce a strict schema or structure for data storage.
For that reason we have used MongoDB for hospital and vaccination data

We used two parallel processes using multiprocessing library viz. 1) rabbit process
that continuously listens to the patient record data that is being fed to the server; 2) sending
process is for the webserver and apis that provide the RTR and stores them to database and
it also includes the RealTime process that continuously updates the database system and
checks for the alerts based on the growth of number of cases according to zipcodes.

## Final Comments
After testing our application using the apis, we found that the application we have developed, is performing very efficiently and elegant in handling and managing the flow of patient data in real time. This could offer the solutions to assist in both the reporting and management of healthcare in relation to the COVID-19 pandemic. Our application also provides real-time reporting and alerting of case growth on zipcode basis and also develops the statewide alert if at least five zipcodes are in alert state. In addition to that the application also offers logic to route patients to appropriate facilities using proper apis, they can provide summarized patient status per hospital and for all hospitals as well. Status includes counts for in-patients, icu patients, and patients on ventilators, along with percentage vaccinated. It also provides data about the group of people who have come in contact with the patients through the report and the same events they have attended.
