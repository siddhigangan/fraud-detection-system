import json
import time
import random
import uuid
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers=['broker:29092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Mock Data Arrays
cities = [
    {"name": "Mumbai", "lat": 19.076, "lon": 72.877},
    {"name": "Nagpur", "lat": 21.145, "lon": 79.088},
    {"name": "New York", "lat": 40.712, "lon": -74.006},
    {"name": "London", "lat": 51.507, "lon": -0.127},
    {"name": "Dubai", "lat": 25.204, "lon": 55.270}
]
devices = ["Android", "iOS", "Windows", "MacOS"]

while True:
    city_data = random.choice(cities)
    data = {
        "id": str(uuid.uuid4())[:8],
        "amount": round(random.uniform(50, 12000), 2),
        "type": random.choice(['transfer', 'withdrawal', 'payment', 'wire_transfer']),
        "city": city_data["name"],
        "lat": city_data["lat"],
        "lon": city_data["lon"],
        "device": random.choice(devices),
        "timestamp": time.time()
    }
    producer.send('transactions', data)
    time.sleep(random.uniform(0.5, 1.5))