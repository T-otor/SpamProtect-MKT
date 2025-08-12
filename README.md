# SpamProtect-MKT
SpamProtect, Mikrotik SSH Version

# Prérequies :
- Requests
- time
- paramiko
- sys
- sqlite3
- dotenv

# Configuration :
## Accès et clé API
Il vous faut mettre votre clé API AbuseIPDB ainsi quue l'accès à votre mikrotik (en SSH) dans chaque fichier (ban.py et unban.py) 

## Configuration du blocage sur le firewall Mikrotik
Sur votre Mikrotik, configuré une règle de Firewall avec "chain : **forward**" et la source adresse liste : **blacklist**

Vous avez le choix de drop ou de reject avec la raison (drop est mieux car cela évite du traffic sortant inutile)
# Utilisation
## BAN.PY
L'outil s'execute de la sorte pour bannir une IP : 
```ban.py <IP> <Raison>```
La liste des raisons est ci-dessous : 

- ssh 
- phising
- malware
- spam

Le script record dans le fichier banned_ips.db (SQLITE) l'ip et la date du bannissement.

## UBAN.PY
Vous pouvez executer ce screen avec une tache cron toute les 10 minutes afin de débannir les IPs après le délais que vous avez configurer.
Par défaut, l'ip est bloqué 24h, vous avez le choix de le modifier à votre convenance en modifiant la variable **UNBAN_THRESHOLD**

# Déployer le script sur Fail2ban (Exemple sur une jail SSH)
## Configuration de l'action
Pour déployer le script sur un Fail2ban, il faut créer un fichier et en modifier un.
Il faut déjà créer l'action qui va être déclenché par la jail.
Allez dans ``` /etc/fail2ban/action.d ``` pour créer un fichier de conf. Exemple : "spamprotect-ssh.conf"
Collez-y ce script : 
```
[Definition]

# Action start
actionstart =

# Action stop
actionstop =

# Action check
actioncheck =

# Action ban
actionban = /usr/bin/python3 /script/ban.py <ip> "SSH"

# Action unban
actionunban =

[Init]

# Option:  name
# Notes.:  Name of the action
# Values:  TEXT
#
name = spamprotect-ssh
```

## Modification de la jail SSH

Modifier votre jail pour y ajouter cette ligne :

```action = spam-protect-ssh```

Et redémarrer votre fail2ban :

```sudo systemctl restart fail2ban```

Pour vérifier que la jail à bien été pris en compte :
