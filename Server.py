import socket
import os

HOST = "127.0.0.1"
PORT = 5000

DOSSIER_SERVEUR = "Server_Files"
DOSSIER_UPLOADS = "uploads"

def main():
    # Création des dossiers si besoin
    os.makedirs(DOSSIER_SERVEUR, exist_ok=True)
    os.makedirs(DOSSIER_UPLOADS, exist_ok=True)

    serveur_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serveur_socket.bind((HOST, PORT))
    serveur_socket.listen(1)

    print(f"Serveur en écoute sur {HOST}:{PORT}...")
    conn, addr = serveur_socket.accept()
    print(f"Client connecté depuis {addr}")

    while True:
        data = conn.recv(1024)
        if not data:
            break

        commande = data.decode().strip()
        print("Commande reçue :", commande)

        # exit
        if commande == "exit":
            conn.send("Au revoir".encode())
            break

        # ls
        if commande == "ls":
            fichiers = os.listdir(DOSSIER_SERVEUR)
            reponse = "\n".join(fichiers)
            conn.send(reponse.encode())
            continue

        # dl <nom>
        if commande.startswith("dl "):
            nom = commande[3:]
            chemin = os.path.join(DOSSIER_SERVEUR, nom)

            if not os.path.exists(chemin):
                conn.send("ERROR".encode())
                continue

            with open(chemin, "rb") as f:
                contenu = f.read()

            taille = str(len(contenu)).encode()

            conn.send(taille)
            conn.send(contenu)

            print(f"Fichier envoyé : {nom}")
            continue

        # ul <nom>
        if commande.startswith("ul "):
            nom = commande[3:]
            chemin = os.path.join(DOSSIER_UPLOADS, nom)

            # Ne pas écraser un fichier existant
            if os.path.exists(chemin):
                conn.send("ERROR".encode())
                continue

            # On indique au client qu'on est prêt
            conn.send("READY".encode())

            # Recevoir la taille
            taille_bytes = conn.recv(1024)
            taille = int(taille_bytes.decode())

            # Recevoir le contenu
            contenu = b""
            recu = 0
            while recu < taille:
                chunk = conn.recv(1024)
                if not chunk:
                    break
                contenu += chunk
                recu += len(chunk)

            # Sauvegarder
            with open(chemin, "wb") as f:
                f.write(contenu)

            print(f"Fichier reçu : {nom} ({taille} octets)")

            # Confirmation au client
            conn.send("OK".encode())
            continue

        # cmd <instruction_shell>
        if commande.startswith("cmd "):
            instruction = commande[4:]  # tout ce qui suit "cmd "

            # Exécuter la commande shell
            try:
                sortie = os.popen(instruction).read()
            except Exception as e:
                sortie = f"Erreur lors de l'exécution : {e}\n"

            # Encoder et envoyer taille + contenu
            sortie_bytes = sortie.encode()
            taille = str(len(sortie_bytes)).encode()

            conn.send(taille)
            conn.send(sortie_bytes)
            continue

        # commande inconnue
        conn.send("Commande inconnue".encode())

    conn.close()
    serveur_socket.close()

if __name__ == "__main__":
    main()