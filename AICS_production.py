import subprocess
import pandas as pd
import time
import requests
from sklearn.ensemble import IsolationForest
from flask import Flask, jsonify
import threading
from datetime import datetime

# =========================
# CONFIG
# =========================
BOT_TOKEN = "PUT_YOUR_BOT_TOKEN"
CHAT_ID = "PUT_YOUR_CHAT_ID"

WHITELIST = ["8.8.8.8", "1.1.1.1"]
COOLDOWN_SECONDS = 300  # 5 دقائق

# =========================
# GLOBALS
# =========================
alerts = []
last_alert_time = {}
ip_history = {}

stop_event = threading.Event()

# =========================
# TELEGRAM
# =========================


def send_alert(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass


# =========================
# DASHBOARD
# =========================
app = Flask(__name__)


@app.route("/")
def dashboard():
    return jsonify(alerts)


def run_dashboard():
    app.run(port=5000)

# =========================
# TRAFFIC CAPTURE (NO TOUCH)
# =========================


def capture_traffic():
    while not stop_event.is_set():
        subprocess.run(
            "tshark -i 4 -a duration:10 -T fields -e ip.src > traffic.csv",
            shell=True
        )
        time.sleep(1)

# =========================
# RISK LOGIC
# =========================


def calculate_risk(count, trend_up):
    if count < 100:
        return "🟢 Low", 20, "Normal Activity"
    elif count < 500:
        return "🟡 Medium", 50, "Suspicious Spike"
    elif count < 1000:
        return "🟠 High", 75, "Possible Scan/Flood"
    else:
        return "🔴 Critical", 95, "Traffic Flood"

# =========================
# THREAT DETECTION
# =========================


def detect_threat():
    model = IsolationForest(contamination=0.15)

    while not stop_event.is_set():
        try:
            df = pd.read_csv("traffic.csv", names=["ip"])
            traffic = df["ip"].value_counts().reset_index()
            traffic.columns = ["ip", "count"]

            if traffic.empty:
                time.sleep(10)
                continue

            traffic["threat"] = model.fit_predict(traffic[["count"]])

            for _, row in traffic.iterrows():
                ip = row["ip"]
                count = row["count"]

                if ip in WHITELIST:
                    continue

                prev = ip_history.get(ip, 0)
                trend_up = count > prev
                ip_history[ip] = count

                if row["threat"] == -1:
                    now = time.time()
                    last = last_alert_time.get(ip, 0)

                    if now - last < COOLDOWN_SECONDS:
                        continue

                    level, score, reason = calculate_risk(count, trend_up)
                    if trend_up:
                        score += 5
                        reason += " + Rising Trend"

                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    msg = (
                        f"🚨 Threat Detected\n"
                        f"Time: {timestamp}\n"
                        f"IP: {ip}\n"
                        f"Packets: {count}\n"
                        f"Risk Level: {level}\n"
                        f"Risk Score: {score}/100\n"
                        f"Type: {reason}"
                    )

                    alerts.append(msg)
                    send_alert(msg)
                    last_alert_time[ip] = now

                    with open("threats.log", "a") as f:
                        f.write(msg + "\n\n")

        except Exception as e:
            print("Detection error:", e)

        time.sleep(10)


# =========================
# MAIN
# =========================
if __name__ == "__main__":
    threads = [
        threading.Thread(target=run_dashboard),
        threading.Thread(target=capture_traffic),
        threading.Thread(target=detect_threat),
    ]

    for t in threads:
        t.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_event.set()
        for t in threads:
            t.join()
  
