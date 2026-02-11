import json
import os
from kafka import KafkaConsumer
from pymongo import MongoClient

consumer = KafkaConsumer(
    'transactions',
    bootstrap_servers=[os.getenv("KAFKA_BROKER", "broker:29092")],
    value_deserializer=lambda v: json.loads(v.decode('utf-8')),
    auto_offset_reset='earliest',
    group_id='fraud-detectors'
)

db = MongoClient(os.getenv("MONGO_URI", "mongodb://mongodb:27017")).fraud_db

for message in consumer:
    txn = message.value
    
    # Advanced Logic: Multi-factor Risk Scoring
    risk_score = 0
    if txn['amount'] > 8000: risk_score += 60
    if txn['type'] == 'wire_transfer': risk_score += 25
    if txn['device'] == 'Android' and txn['amount'] > 5000: risk_score += 15
    
    txn['risk_score'] = risk_score
    txn['is_fraud'] = risk_score >= 75 # Threshold for High Risk
    
    db.transactions.insert_one(txn)
    print(f"Processed {txn['id']} | Risk: {risk_score}")