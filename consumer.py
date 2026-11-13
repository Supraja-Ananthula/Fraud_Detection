import json
import sqlite3
import pickle
import pandas as pd
from kafka import KafkaConsumer

with open("model.pkl", "rb") as f:
    model = pickle.load(f)

conn = sqlite3.connect("results.db")
conn.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        transaction_id TEXT,
        amount REAL,
        status TEXT
    )
""")
conn.commit()

feature_cols = [f"V{i}" for i in range(1, 29)] + ["Amount"]

consumer = KafkaConsumer(
    "live-transactions",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda v: json.loads(v.decode("utf-8"))
)

print("Listening for transactions... Press Ctrl+C to stop.")
for msg in consumer:
    data = msg.value
    txn_id = data["transaction_id"]
    amount = data["Amount"]

    if amount > 10000:
        status = "SUSPICIOUS (Rule: High Amount)"
    else:
        row = pd.DataFrame([[data[c] for c in feature_cols]], columns=feature_cols)
        score = model.predict(row)[0]
        if score == -1:
            status = "SUSPICIOUS (ML)"
        else:
            status = "LEGITIMATE"

    print(f"{txn_id} | Amount: {amount:.2f} | {status}")
    conn.execute("INSERT INTO transactions VALUES (?, ?, ?)", (txn_id, amount, status))
    conn.commit()