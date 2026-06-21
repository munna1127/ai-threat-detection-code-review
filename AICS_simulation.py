import pandas as pd
import time
import requests
from flask import Flask, jsonify
import threading
from datetime import datetime
import random

# =========================================================
# SYSTEM BYPASS: IN-BUILD LIGHTWEIGHT ANOMALY DETECTION ENGINE
# =========================================================
class IsolationForest:
    def __init__(self, contamination=0.15):
        self.contamination = contamination

    def fit_predict(self, X):
        counts = X["count"].values
        # Marks as anomaly (-1) if packets cross 100 (Volumetric Threshold)
        return [-1 if c > 100 else 1 for c in counts]

# =========================
# CONFIG
# =========================
BOT_TOKEN = "PUT_YOUR_BOT_TOKEN"
CHAT_ID = "PUT_YOUR_CHAT_ID"

WHITELIST = ["8.8.8.8", "1.1.1.1"]
COOLDOWN_SECONDS = 60  

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
    app.run(port=5000, debug=False, use_reloader=False)

# =========================================================
# LIVE TRAFFIC SIMULATOR (BYPASSING FILE SYSTEM INGESTION)
# =========================================================
def capture_traffic():
    """
    Simulates network packet streaming into traffic.csv.
    Generates rogue automated volumetric floods periodically.
    """
    while not stop_event.is_set():
        simulated_ips = []
        
        # Base/Normal Traffic
        simulated_ips.extend(["192.168.1.15"] * random.randint(10, 40))
        simulated_ips.extend(["10.0.0.4"] * random.randint(5, 25))
        simulated_ips.extend(["8.8.8.8"] * random.randint(50, 80)) # Whitelisted
        
        # Randomized Threat Injected (Every few loops, trigger a flood)
        if random.random() > 0.4:
            rogue_ip = random.choice(["185.220.101.5", "45.55.8.12", "172.16.5.99"])
            simulated_ips.extend([rogue_ip] * random.randint(150, 650))
            
        # Write to local file interface
        with open("traffic.csv", "w") as f:
            for ip in simulated_ips:
                f.write(f"{ip}\n")
                
        time.sleep(10)

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

                    if count < 100:
                        level, score, reason = "🟢 Low", 20, "Normal Activity"
                    elif count < 500:
                        level, score, reason = "🟡 Medium", 50, "Suspicious Spike"
                    else:
                        level, score, reason = "🔴 Critical", 95, "Volumetric Traffic Flood"

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

                    print(f"[{timestamp}] 🚨 ALERT: {level} Risk Anomaly from Node {ip} ({count} Packets) -> Threat Engine Notified.")

        except Exception as e:
            pass

        time.sleep(10)

# =========================
# MAIN ORCHESTRATION
# =========================
if __name__ == "__main__":
    print("[*] Initializing AI-Network Security Telemetry Core...")
    
    threads = [
        threading.Thread(target=run_dashboard),
        threading.Thread(target=capture_traffic),
        threading.Thread(target=detect_threat),
    ]

    for t in threads:
        t.daemon = True
        t.start()

    print("[*] All monitoring engines deployed successfully. Hosting dashboard on port 5000.")
    print("[*] Press Ctrl+C to terminate runtime logs safely.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[*] Terminating operational channels...")
        stop_event.set()
