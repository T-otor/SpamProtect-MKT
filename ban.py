import sqlite3
from datetime import datetime
import paramiko
import time
import sys
import requests
api_key = "YOu_API_TOKEN_HERE"
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
    print(f"Reporting {ip} to AbuseIPDB... (not implemented)")
    # Message prédéfini pour le type de report
    if report_type == "spam":
        print(f"Report type: Spam - {ip} reported for spam activity.")
    elif report_type == "malware":
        print(f"Report type: Malware - {ip} reported for malware activity.")
    elif report_type == "phishing":
        print(f"Report type: Phishing - {ip} reported for phishing activity.")
    elif report_type == "ssh":
        print(f"Report type: SSH - {ip} reported for SSH brute force activity. Unban : https://unban-request.totor.systems")
        comment = f"Report type: SSH - {ip} reported for SSH brute force activity. Unban : https://unban-request.totor.systems"
        report_id = "22,18"
    
    # POST request to AbuseIPDB (not implemented)
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


mikrotik_host = "YOUR_MIKROTIK_IP"
mikrotik_user = "YOUR_USER_ON_MIKROTIK"
mikrotik_password = "YOUR_PASSWORD_ON_MIKROTIK"

setup_database()
add_ip_to_db(fail2ban_ip)
add_ip_to_mikrotik_ssh(fail2ban_ip, mikrotik_host, mikrotik_user, mikrotik_password)
abuseipdb_report(fail2ban_ip, report_type)
