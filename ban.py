import sqlite3
from datetime import datetime
import paramiko
from dotenv import load_dotenv
import os
import time
import sys
import requests
load_dotenv()
api_key = os.getenv('API_KEY')
report_type_mapping = {
    "1": "DNS_Compromise",
    "2": "DNS_Poisoning",
    "3": "Fraud_Orders",
    "4": "DDoS_Attack",
    "5": "FTP_Brute-Force",
    "6": "Ping_of_Death",
    "7": "Phishing",
    "8": "Fraud_VoIP",
    "9": "Open_Proxy",
    "10": "Web_Spam",
    "11": "Email_Spam",
    "12": "Blog_Spam",
    "13": "VPN_IP",
    "14": "Port_Scan",
    "15": "Hacking",
    "16": "SQL_Injection",
    "17": "Spoofing",
    "18": "Brute-Force",
    "19": "Bad_Web_Bot",
    "20": "Exploited_Host",
    "21": "Web_App_Attack",
    "22": "SSH_Abuse",
    "23": "IoT_Targeted",
}

def setup_database():
    conn = sqlite3.connect('banned_ips.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS banned_ips (
            ip TEXT PRIMARY KEY,
            ban_time TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


def add_ip_to_db(ip):
    conn = sqlite3.connect('banned_ips.db')
    cursor = conn.cursor()
    now_ts = int(time.time())  # timestamp Unix en secondes
    cursor.execute('INSERT OR REPLACE INTO banned_ips (ip, ban_time) VALUES (?, ?)', (ip, now_ts))
    conn.commit()
    conn.close()

def add_ip_to_mikrotik_ssh(ip, mikrotik_host, mikrotik_user, mikrotik_password):
    command = f"/ip firewall address-list add address={ip} list=blacklist"
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(mikrotik_host, username=mikrotik_user, password=mikrotik_password)
        stdin, stdout, stderr = ssh.exec_command(command)
        error = stderr.read().decode()
        if error:
            print(f"Erreur SSH MikroTik: {error}")
        else:
            print(f"IP {ip} ajoutée à la blacklist MikroTik via SSH.")
        ssh.close()
    except Exception as e:
        print(f"Erreur lors de l'ajout de l'IP au MikroTik via SSH: {e}")

def abuseipdb_report(ip, report_type):
    # Placeholder for AbuseIPDB reporting logic
    report_id = None
    comment = ""

    if report_type in report_type_mapping:
        name, description = report_type_mapping[report_type]
        print(f"Report type: {name} - {ip} reported for {description}")
        comment = f"Report type: {name} - {ip} reported for {description}."
        report_id = report_type
    else:
        print(f"Unknown report type: {report_type}")

    print(f"Reporting {ip} to AbuseIPDB...")

    # POST request to AbuseIPDB
    url = "https://api.abuseipdb.com/api/v2/report"
    payload = {
        "ip": ip,
        "categories": report_id if report_id else "18",  # Default to 18 if not specified
        "comment": comment,
        "timestamp": datetime.now().astimezone().isoformat()
    }
    headers = {
        "Key": api_key,
        "Accept": "application/json"
    }
    try:
        response = requests.post(url, data=payload, headers=headers)
        if response.status_code == 200:
            print(f"AbuseIPDB report submitted for {ip}.")
        else:
            print(f"Failed to report to AbuseIPDB: {response.status_code} {response.text}")
    except Exception as e:
        print(f"Error reporting to AbuseIPDB: {e}")

# Exemple d'utilisation
if len(sys.argv) < 2:
    print("Usage: python ban.py <ip_address> [report_type]")
    sys.exit(1)

fail2ban_ip = sys.argv[1]
if not fail2ban_ip:
    print("No IP address provided.")
    sys.exit(1)

    # Récupère le type de report à faire dans AbuseIPDB (optionnel)
report_type = None
if len(sys.argv) > 2:
    report_type = sys.argv[2]


mikrotik_host = os.getenv('MIKROTIK_HOST')
mikrotik_user = os.getenv('MIKROTIK_USER')
mikrotik_password = os.getenv('MIKROTIK_PASSWORD')

setup_database()
add_ip_to_db(fail2ban_ip)
add_ip_to_mikrotik_ssh(fail2ban_ip, mikrotik_host, mikrotik_user, mikrotik_password)
abuseipdb_report(fail2ban_ip, report_type)
