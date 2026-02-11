from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from pymongo import MongoClient
import pandas as pd

def retrain_model():
    client = MongoClient("mongodb://mongodb:27017")
    db = client.fraud_db
    
    # 1. Fetch data from MongoDB
    data = list(db.transactions.find())
    if len(data) < 100:
        print("Not enough data to retrain yet.")
        return
    
    df = pd.DataFrame(data)
    
    # 2. Logic to update model weights (Simplified simulation)
    # In a real scenario, you'd run: model.fit(df[['amount']], df['is_fraud'])
    print(f"Successfully retrained model on {len(df)} transactions.")
    
    # 3. Save model version
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    print(f"Model version v_{timestamp} saved to /processor/models/")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'fraud_model_retraining',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False
) as dag:

    train_task = PythonOperator(
        task_id='retrain_fraud_model',
        python_callable=retrain_model
    )