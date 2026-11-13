# Real-Time Fraud Detection System

A beginner-level ML project that detects fraudulent transactions in real time using Kafka, Isolation Forest, and FastAPI.

---

## How It Works

```
CSV File → Producer → Kafka → Consumer → Rules + ML Model → SQLite → Dashboard
```

1. Producer reads the dataset row by row and sends each transaction to Kafka
2. Consumer picks it up, runs a rules check (high amount?) then an ML check
3. Result (LEGITIMATE or SUSPICIOUS) is saved to a local database
4. Dashboard shows the results in your browser

---

## Project Structure

```
fraud-detection/
├── data/
│   └── creditcard.csv       ← download from Kaggle (link below)
├── train_model.py           ← trains and saves the ML model
├── producer.py              ← sends transactions to Kafka
├── consumer.py              ← detects fraud and saves results
├── dashboard.py             ← web API to view results
└── requirements.txt
```

---

## Requirements

- Python 3.10+
- Java 11+ (needed for Kafka)
- macOS with Homebrew (or Linux)

---

## Setup (Do This Once)

### 1. Get the dataset

Download `creditcard.csv` from Kaggle:
https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud

Put it in the `data/` folder.

### 2. Install Kafka

```bash
brew install kafka
```

### 3. Install Python packages

```bash
pip install -r requirements.txt
```

---

## Running the Project

You need **4 terminals** open at the same time.

### Terminal 1 — Start Kafka

```bash
brew services start zookeeper
brew services start kafka
```

Create the topic (only once):

```bash
kafka-topics --create --topic live-transactions --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
```

### Terminal 2 — Train the model

```bash
python train_model.py
```

Wait for: `Model trained and saved to model.pkl`
Run this only once before starting the consumer.

### Terminal 3 — Start the consumer

```bash
python consumer.py
```

It will wait silently. That is normal — it is listening for transactions.

### Terminal 4 — Start the producer

```bash
python producer.py
```

Switch to Terminal 3. You will see output like:

```
TXN_00001 | Amount: 45.20  | LEGITIMATE
TXN_00002 | Amount: 12500.00 | SUSPICIOUS (Rule: High Amount)
TXN_00003 | Amount: 9.99   | SUSPICIOUS (ML)
```

### Terminal 5 (optional) — Start the dashboard

```bash
uvicorn dashboard:app --reload
```

Open your browser:

| URL | What you see |
|-----|-------------|
| http://localhost:8000/ | Last 20 transactions |
| http://localhost:8000/suspicious | Only suspicious ones |

---

## Detection Logic

The consumer checks each transaction in two stages:

**Stage 1 — Rules Engine**
- If `Amount > 10000` → immediately marked SUSPICIOUS

**Stage 2 — ML Model (Isolation Forest)**
- If the transaction passes the rules check, it goes through the ML model
- Isolation Forest scores it: `-1` means anomaly (SUSPICIOUS), `1` means normal (LEGITIMATE)

---

## Tech Stack

| Component | Tool |
|-----------|------|
| Message Queue | Apache Kafka |
| ML Model | Scikit-Learn Isolation Forest |
| Database | SQLite |
| Web Dashboard | FastAPI |
| Data Processing | Pandas |
| Dataset | Kaggle Credit Card Fraud |

---

## Stopping Everything

```bash
brew services stop kafka
brew services stop zookeeper
```

Press `Ctrl+C` in any terminal to stop a running script.