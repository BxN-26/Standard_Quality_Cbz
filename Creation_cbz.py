import os
import zipfile
import shutil
from datetime import datetime

# Chemins vers les fichiers et répertoires
seven_zip_path = '/usr/bin/7z'  # Chemin vers 7-Zip sous Ubuntu
input_directory = os.path.expanduser('~/Documents/BDs/BD/')  # Répertoire de travail sous Ubuntu
log_file_path = os.path.join(input_directory, "process_log.txt")  # Chemin du fichier de log

# Statistiques
total_cbz_created = 0
total_errors = 0

# Fonction pour écrire dans le fichier de log avec horodatage
def log_message(message):
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Format de l'horodatage
        message = f"[{timestamp}] {message}"
        with open(log_file_path, "a") as log_file:
            log_file.write(message + "\n")
        print(message)
    except Exception as e:
        print_error(f"Erreur lors de l'écriture dans le log : {e}")

# Fonction pour imprimer des messages d'erreur en rouge
def print_error(message):
    error_message = f"\033[91m{message}\033[0m"  # Code ANSI pour rouge
    log_message(message)
    print(error_message)

# Étape 4 : Création des fichiers .cbz
def create_cbz_from_folder(folder_path, output_cbz):
    log_message(f"Création de CBZ à partir de : {folder_path}")
    image_files = sorted(
        [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    )

    if not image_files:
        print_error(f"Aucune image trouvée dans {folder_path}.")
        return  # Sortir si aucune image

    # Chemin de la première image
    first_image_path = os.path.join(folder_path, image_files[0])

    temp_zip = output_cbz.replace(".cbz", ".zip")

    try:
        with zipfile.ZipFile(temp_zip, 'w', zipfile.ZIP_DEFLATED) as cbz_zip:
            for image in image_files:
                image_path = os.path.join(folder_path, image)
                cbz_zip.write(image_path, arcname=image)

        os.rename(temp_zip, output_cbz)
        log_message(f"Fichier CBZ créé : {output_cbz}")
        global total_cbz_created
        total_cbz_created += 1

        # Copier la première image et la renommer avec le suffixe "-poster"
        poster_image_name = os.path.splitext(os.path.basename(output_cbz))[0] + "-poster.jpg"
        poster_image_path = os.path.join(os.path.dirname(output_cbz), poster_image_name)

        # Copier la première image
        shutil.copy(first_image_path, poster_image_path)
        log_message(f"Image poster créée : {poster_image_path}")

    except Exception as e:
        print_error(f"Erreur lors de la création de CBZ pour {folder_path} : {e}")
        global total_errors
        total_errors += 1

# Création des fichiers .cbz
log_message("Début de la création des fichiers .cbz...")

try:
    for subdir, _, files in os.walk(input_directory):
        if files:  # Si le répertoire contient des fichiers
            cbz_name = os.path.basename(subdir) + '.cbz'
            cbz_path = os.path.join(input_directory, cbz_name)
            create_cbz_from_folder(subdir, cbz_path)
except Exception as e:
    print_error(f"Erreur lors de la création des fichiers CBZ : {e}")
    total_errors += 1

# Étape 5 : Suppression des fichiers non JPG
log_message("Début de la suppression des fichiers non JPG...")

try:
    for subdir, _, files in os.walk(input_directory):
        for file in files:
            if not file.lower().endswith('.jpg') and not file.lower().endswith('.cbz'):
                os.remove(os.path.join(subdir, file))
                log_message(f"Fichier supprimé : {file}")
    log_message("Suppression des fichiers non JPG terminée.")
except Exception as e:
    print_error(f"Erreur lors de la suppression des fichiers non JPG : {e}")
    total_errors += 1

# Étape 6 : Suppression des répertoires de décompression
log_message("Début de la suppression des répertoires dans le répertoire d'entrée...")

# Récupérer tous les sous-répertoires dans input_directory
decompressed_dirs = [os.path.join(input_directory, d) for d in os.listdir(input_directory) if os.path.isdir(os.path.join(input_directory, d))]

for dir in decompressed_dirs:
    try:
        shutil.rmtree(dir)  # Supprimer le répertoire
        log_message(f"Répertoire supprimé : {dir}")
    except FileNotFoundError:
        print_error(f"Le répertoire {dir} n'a pas pu être trouvé.")
        log_message(f"Le répertoire {dir} n'a pas pu être trouvé.")
        total_errors += 1
    except PermissionError:
        print_error(f"Permission refusée pour supprimer le répertoire {dir}.")
        log_message(f"Permission refusée pour supprimer le répertoire {dir}.")
        total_errors += 1
    except Exception as e:
        print_error(f"Erreur lors de la suppression du répertoire {dir} : {e}")
        log_message(f"Erreur lors de la suppression du répertoire {dir} : {e}")
        total_errors += 1

# Affichage des statistiques
log_message("Statistiques finales :")
log_message(f"Total de fichiers CBZ créés : {total_cbz_created}")
log_message(f"Total d'erreurs : {total_errors}")

print("Appuyez sur une touche pour fermer la fenêtre...")
input()  # Pause avant de fermer la console
