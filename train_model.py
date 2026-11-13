import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt

from sklearn.ensemble import IsolationForest
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    roc_curve
)
from sklearn.model_selection import train_test_split

from xgboost import XGBClassifier

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Bidirectional


# -----------------------
# Load data
# -----------------------
df = pd.read_csv("data/creditcard.csv")

feature_cols = [f"V{i}" for i in range(1, 29)] + ["Amount"]
X = df[feature_cols]
y = df["Class"]


# -----------------------
# Train Test Split
# -----------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)


# -----------------------
# 1. Isolation Forest
# -----------------------
print("Training Isolation Forest...")

iso_model = IsolationForest(contamination=0.01, random_state=42)
iso_model.fit(X_train)

iso_pred = iso_model.predict(X_test)
iso_pred = np.where(iso_pred == -1, 1, 0)

iso_acc = accuracy_score(y_test, iso_pred)
iso_precision = precision_score(y_test, iso_pred)
iso_recall = recall_score(y_test, iso_pred)
iso_f1 = f1_score(y_test, iso_pred)
iso_auc = roc_auc_score(y_test, iso_pred)

iso_fpr, iso_tpr, _ = roc_curve(y_test, iso_pred)

with open("model.pkl", "wb") as f:
    pickle.dump(iso_model, f)

print("IsolationForest saved as model.pkl")


# -----------------------
# 2. XGBoost
# -----------------------
print("Training XGBoost...")

xgb_model = XGBClassifier(
    n_estimators=100,
    max_depth=5,
    learning_rate=0.1,
    eval_metric='logloss'
)

xgb_model.fit(X_train, y_train)

xgb_pred = xgb_model.predict(X_test)
xgb_prob = xgb_model.predict_proba(X_test)[:,1]

xgb_acc = accuracy_score(y_test, xgb_pred)
xgb_precision = precision_score(y_test, xgb_pred)
xgb_recall = recall_score(y_test, xgb_pred)
xgb_f1 = f1_score(y_test, xgb_pred)
xgb_auc = roc_auc_score(y_test, xgb_prob)

xgb_fpr, xgb_tpr, _ = roc_curve(y_test, xgb_prob)

with open("xgboost_model.pkl", "wb") as f:
    pickle.dump(xgb_model, f)

print("XGBoost saved as xgboost_model.pkl")


# -----------------------
# 3. BiLSTM
# -----------------------
print("Training BiLSTM...")

X_train_lstm = np.array(X_train).reshape((X_train.shape[0], X_train.shape[1], 1))
X_test_lstm = np.array(X_test).reshape((X_test.shape[0], X_test.shape[1], 1))

bilstm_model = Sequential()
bilstm_model.add(Bidirectional(LSTM(64), input_shape=(X_train_lstm.shape[1], 1)))
bilstm_model.add(Dense(1, activation='sigmoid'))

bilstm_model.compile(
    loss='binary_crossentropy',
    optimizer='adam',
    metrics=['accuracy']
)

bilstm_model.fit(X_train_lstm, y_train, epochs=5, batch_size=64)

bilstm_prob = bilstm_model.predict(X_test_lstm)
bilstm_pred = (bilstm_prob > 0.5).astype(int)

bilstm_acc = accuracy_score(y_test, bilstm_pred)
bilstm_precision = precision_score(y_test, bilstm_pred)
bilstm_recall = recall_score(y_test, bilstm_pred)
bilstm_f1 = f1_score(y_test, bilstm_pred)
bilstm_auc = roc_auc_score(y_test, bilstm_prob)

bilstm_fpr, bilstm_tpr, _ = roc_curve(y_test, bilstm_prob)

bilstm_model.save("bilstm_model.h5")

print("BiLSTM saved as bilstm_model.h5")


# -----------------------
# Metrics Print
# -----------------------
print("\n==== Metrics Comparison ====")

print("\nIsolation Forest")
print("Accuracy:", iso_acc)
print("Precision:", iso_precision)
print("Recall:", iso_recall)
print("F1:", iso_f1)
print("AUC:", iso_auc)

print("\nXGBoost")
print("Accuracy:", xgb_acc)
print("Precision:", xgb_precision)
print("Recall:", xgb_recall)
print("F1:", xgb_f1)
print("AUC:", xgb_auc)

print("\nBiLSTM")
print("Accuracy:", bilstm_acc)
print("Precision:", bilstm_precision)
print("Recall:", bilstm_recall)
print("F1:", bilstm_f1)
print("AUC:", bilstm_auc)


# -----------------------
# Accuracy Graph
# -----------------------
models = ['IsolationForest', 'XGBoost', 'BiLSTM']
accuracy = [iso_acc, xgb_acc, bilstm_acc]

plt.figure()
plt.bar(models, accuracy)
plt.title("Model Accuracy Comparison")
plt.ylabel("Accuracy")
plt.savefig("accuracy_comparison.png")


# -----------------------
# ROC Curve
# -----------------------
plt.figure()

plt.plot(iso_fpr, iso_tpr, label=f'IsolationForest AUC={iso_auc:.3f}')
plt.plot(xgb_fpr, xgb_tpr, label=f'XGBoost AUC={xgb_auc:.3f}')
plt.plot(bilstm_fpr, bilstm_tpr, label=f'BiLSTM AUC={bilstm_auc:.3f}')

plt.plot([0,1],[0,1],'k--')
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC Curve Comparison")
plt.legend()

plt.savefig("roc_curve.png")
plt.show()

print("Graphs saved: accuracy_comparison.png, roc_curve.png")