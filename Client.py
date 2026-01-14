import socket
import os
import sys

HOST = "127.0.0.1"
PORT = 5000

def afficher_progression(recu, total, prefix=""):
    if total == 0:
        return
    pourcentage = recu / total
    bar_length = 30
    filled = int(pourcentage * bar_length)
    bar = "█" * filled + "-" * (bar_length - filled)
    sys.stdout.write(f"\r{prefix}[{bar}] {int(pourcentage * 100)}%")
    sys.stdout.flush()

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    print("Connecté au serveur.")

    os.makedirs("downloads", exist_ok=True)

    while True:
        cmd = input("Commande : ")
        client_socket.send(cmd.encode())

        # exit
        if cmd == "exit":
            break

        # ls
        if cmd == "ls":
            reponse = client_socket.recv(4096).decode()
            print(reponse)
            continue

        # dl <nom>
        if cmd.startswith("dl "):
            nom = cmd[3:]

            taille = client_socket.recv(1024).decode()

            if taille == "ERROR":
                print("Le fichier n'existe pas sur le serveur.")
                continue

            taille = int(taille)
            print(f"Téléchargement de {nom} ({taille} octets)")

            contenu = b""
            recu = 0

            while recu < taille:
                chunk = client_socket.recv(1024)
                if not chunk:
                    break
                contenu += chunk
                recu += len(chunk)
                afficher_progression(recu, taille, prefix="Download ")

            print()

            chemin = os.path.join("downloads", nom)
            with open(chemin, "wb") as f:
                f.write(contenu)

            print(f"Fichier sauvegardé dans downloads/{nom}")
            continue

        # ul <nom>
        if cmd.startswith("ul "):
            nom = cmd[3:]

            if not os.path.exists(nom):
                print("Le fichier n'existe pas sur le client.")
                continue

            # Attendre READY ou ERROR
            reponse = client_socket.recv(1024).decode()

            if reponse == "ERROR":
                print("Le serveur refuse l'upload (fichier déjà existant ?).")
                continue

            # Lire le fichier
            with open(nom, "rb") as f:
                contenu = f.read()

            taille = len(contenu)
            taille_bytes = str(taille).encode()

            # Envoyer la taille
            client_socket.send(taille_bytes)

            print(f"Upload de {nom} ({taille} octets)")
            envoyes = 0
            offset = 0
            chunk_size = 1024

            # Envoyer le contenu avec barre de progression
            while offset < taille:
                chunk = contenu[offset:offset + chunk_size]
                client_socket.send(chunk)
                offset += len(chunk)
                envoyes += len(chunk)
                afficher_progression(envoyes, taille, prefix="Upload   ")

            print()

            # Attendre confirmation
            confirmation = client_socket.recv(1024).decode()
            if confirmation == "OK":
                print(f"Fichier {nom} envoyé et confirmé par le serveur.")
            else:
                print("Problème lors de la confirmation du serveur.")
            continue

        # cmd <instruction_shell>
        if cmd.startswith("cmd "):
            # 1. recevoir la taille
            taille_bytes = client_socket.recv(1024)
            taille = int(taille_bytes.decode())

            # 2. recevoir la sortie complète
            recu = 0
            sortie_bytes = b""
            while recu < taille:
                chunk = client_socket.recv(1024)
                if not chunk:
                    break
                sortie_bytes += chunk
                recu += len(chunk)

            sortie = sortie_bytes.decode()
            print("Sortie de la commande :")
            print(sortie)
            continue

        # autres commandes
        reponse = client_socket.recv(4096).decode()
        print(reponse)

    client_socket.close()

if __name__ == "__main__":
    main()