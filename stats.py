import os
import sys

def format_taille(octets):
    ko = octets / 1024
    if ko < 1024:
        return f"{ko:.2f} Ko"
    mo = ko / 1024
    return f"{mo:.2f} Mo"

def main():
    if len(sys.argv) < 2:
        print("Usage : python3 stats.py /chemin/vers/dossier")
        sys.exit(1)

    racine = sys.argv[1]

    if not os.path.isdir(racine):
        print("Erreur : ce n'est pas un dossier valide.")
        sys.exit(1)

    total_taille = 0
    total_fichiers = 0
    tailles_dossiers = {}
    plus_gros_fichier = None
    plus_grosse_taille = 0

    for dossier_courant, sous_dossiers, fichiers in os.walk(racine):
        taille_dossier = 0

        for f in fichiers:
            chemin_f = os.path.join(dossier_courant, f)
            try:
                taille_f = os.path.getsize(chemin_f)
            except OSError:
                continue

            taille_dossier += taille_f
            total_taille += taille_f
            total_fichiers += 1

            if taille_f > plus_grosse_taille:
                plus_grosse_taille = taille_f
                plus_gros_fichier = chemin_f

        tailles_dossiers[dossier_courant] = taille_dossier

    print(f"Dossier analysé : {racine}")
    print(f"Nombre total de fichiers : {total_fichiers}")
    print(f"Taille totale : {format_taille(total_taille)}")
    print()

    print("Taille par dossier :")
    for dossier, taille in sorted(tailles_dossiers.items(), key=lambda x: x[1], reverse=True):
        print(f"- {dossier} : {format_taille(taille)}")

    if plus_gros_fichier:
        print()
        print("Fichier le plus volumineux :")
        print(f"- {plus_gros_fichier} ({format_taille(plus_grosse_taille)})")

if __name__ == "__main__":
    main()