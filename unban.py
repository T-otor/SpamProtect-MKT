import sqlite3
import time
import paramiko

DB_PATH = 'banned_ips.db'
UNBAN_THRESHOLD = 38600  # Seuil de débanissement en secondes ( 1 journée)
mikrotik_host = "YOUR_MIKROTIK_IP"
mikrotik_user = "YOUR_USER_ON_MIKROTIK"
mikrotik_password = "YOUR_PASSWORD_ON_MIKROTIK"

def unban_old_ips():
    now = int(time.time())
    threshold_time = now - UNBAN_THRESHOLD

    print(f"[DEBUG] Heure actuelle : {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(now))}")
    print(f"[DEBUG] Seuil de déban : {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(threshold_time))}")

    # Connexion DB
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Liste toutes les IP bannies pour info
    cursor.execute("SELECT ip, ban_time FROM banned_ips")
    all_bans = cursor.fetchall()
    if all_bans:
        print("[DEBUG] IP actuellement bannies :")
        for ip, ban_time in all_bans:
            print(f"    {ip} → banni à {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(ban_time)))}")

    else:
        print("[DEBUG] Aucune IP dans la base.")

    # Récupère celles à débannir
    cursor.execute("SELECT ip, ban_time FROM banned_ips WHERE ban_time < ?", (threshold_time,))
    old_bans = cursor.fetchall()

    if not old_bans:
        print("[INFO] Aucune IP à débannir.")
        conn.close()
        return

    # Supprime dans SQLite
    cursor.execute("DELETE FROM banned_ips WHERE ban_time < ?", (threshold_time,))
    conn.commit()
    conn.close()
    print(f"[INFO] {len(old_bans)} IP supprimée(s) de la base.")

    # Connexion SSH MikroTik
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(mikrotik_host, username=mikrotik_user, password=mikrotik_password)
        print("[DEBUG] Connexion SSH au MikroTik établie.")

        for ip, ban_time in old_bans:
            print(f"[INFO] Débannissement MikroTik pour {ip}")
            command = f"/ip firewall address-list remove [find address={ip} list=blacklist]"
            stdin, stdout, stderr = ssh.exec_command(command)

            error = stderr.read().decode().strip()
            if error:
                print(f"[ERREUR] MikroTik SSH pour {ip} : {error}")
            else:
                print(f"[OK] {ip} retirée de la blacklist MikroTik.")

        ssh.close()
        print("[DEBUG] Connexion SSH fermée.")

    except Exception as e:
        print(f"[ERREUR] Connexion SSH MikroTik échouée : {e}")
if __name__ == "__main__":
    unban_old_ips()


