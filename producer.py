import pandas as pd
import json
import time
from kafka import KafkaProducer

df = pd.read_csv("data/creditcard.csv")
feature_cols = [f"V{i}" for i in range(1, 29)] + ["Amount"]

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

print("Sending transactions to Kafka... Press Ctrl+C to stop.")
for i, row in df[feature_cols].iterrows():
    payload = row.to_dict()
    payload["transaction_id"] = f"TXN_{i:05d}"
    producer.send("live-transactions", value=payload)
    print(f"Sent TXN_{i:05d} | Amount = {payload['Amount']:.2f}")
    time.sleep(0.5)

producer.flush()
print("All transactions sent.")