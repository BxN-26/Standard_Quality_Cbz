import os
import subprocess
import glob
from PIL import Image
import shutil
import zipfile
import time
import re
import concurrent.futures
import tkinter as tk
from tkinter import filedialog
from tqdm import tqdm

# Chemins vers les exécutables
seven_zip_path = '/usr/bin/7z'
unrar_path = '/usr/bin/unrar'

# Ouvrir une boîte de dialogue pour choisir le répertoire de traitement
root = tk.Tk()
root.withdraw()
input_directory = filedialog.askdirectory(title="Sélectionnez le dossier de traitement")
if not input_directory:
    print("Aucun dossier sélectionné. Fin du programme.")
    exit()

log_file_path = os.path.join(input_directory, "process_log.txt")

total_images_processed = 0
total_errors = 0

def clean_message(message):
    return re.sub(r'[^\x00-\x7F]+', '?', message)

def log_message(message):
    try:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        message = f"[{timestamp}] {clean_message(message)}"
        with open(log_file_path, "a", encoding='utf-8', errors='replace') as log_file:
            log_file.write(message + "\n")
        print(message)
    except Exception as e:
        print_error(f"Erreur lors de l'écriture dans le log : {e}")

def print_error(message):
    error_message = f"\033[91m{message}\033[0m"
    log_message(message)
    print(error_message)

def process_image(input_file_path, resize_dimensions):
    global total_images_processed, total_errors
    try:
        with Image.open(input_file_path) as img:
            width, height = img.size
            target_dimensions = (resize_dimensions[1], resize_dimensions[0]) if width > height else resize_dimensions
            log_message(f"Taille cible : {target_dimensions[0]}x{target_dimensions[1]}")
            img = img.resize(target_dimensions, Image.Resampling.LANCZOS)
            img = img.convert("RGB")
            output_file_path = os.path.splitext(input_file_path)[0] + '.jpg'
            img.save(output_file_path, 'JPEG', dpi=(300, 300))
            log_message(f"Fichier sauvegardé : {output_file_path}")
            total_images_processed += 1
    except Exception as e:
        print_error(f"Erreur lors du traitement de l'image {input_file_path} : {e}")
        total_errors += 1

print("Choisissez la taille de redimensionnement :")
print("1. BD (2480x3508)")
print("2. Comic/Manga (1800x2880)")
choice = input("Entrez votre choix (1 ou 2) : ")
resize_dimensions = (2480, 3508) if choice == '1' else (1800, 2880) if choice == '2' else exit()

log_message("Début de la décompression des fichiers...")
try:
    for filepath in glob.glob(os.path.join(input_directory, '*.cbz')) + glob.glob(os.path.join(input_directory, '*.zip')):
        output_subdirectory = os.path.join(input_directory, os.path.splitext(os.path.basename(filepath))[0])
        os.makedirs(output_subdirectory, exist_ok=True)
        result = subprocess.run([seven_zip_path, 'x', filepath, f'-o{output_subdirectory}', '-y'], check=False)
        if result.returncode == 0:
            os.remove(filepath)
    
    for filepath in glob.glob(os.path.join(input_directory, '*.cbr')) + glob.glob(os.path.join(input_directory, '*.rar')):
        output_subdirectory = os.path.join(input_directory, os.path.splitext(os.path.basename(filepath))[0])
        os.makedirs(output_subdirectory, exist_ok=True)
        result = subprocess.run([unrar_path, 'x', filepath, output_subdirectory], check=False)
        if result.returncode == 0:
            os.remove(filepath)
    
    log_message("Décompression terminée.")
except Exception as e:
    print_error(f"Erreur lors de la décompression : {e}")
    total_errors += 1

log_message("Début du traitement des images...")
try:
    image_files = [os.path.join(subdir, file) for subdir, _, files in os.walk(input_directory) for file in files if file.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"))]
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        list(tqdm(executor.map(lambda file: process_image(file, resize_dimensions), image_files), total=len(image_files), desc="Traitement des images"))
    
    log_message("Traitement des images terminé.")
except Exception as e:
    print_error(f"Erreur lors de la boucle de traitement des images : {e}")
    total_errors += 1

log_message("Début de la suppression de tous les fichiers sauf les JPG...")
try:
    for subdir, _, files in os.walk(input_directory):
        for file in files:
            if not file.lower().endswith('.jpg'):
                file_path = os.path.join(subdir, file)
                os.remove(file_path)
                log_message(f"Fichier supprimé : {file_path}")
    log_message("Suppression terminée.")
except Exception as e:
    print_error(f"Erreur lors de la suppression des fichiers non JPG : {e}")
    total_errors += 1

log_message("Statistiques finales :")
log_message(f"Total d'images traitées : {total_images_processed}")
log_message(f"Total d'erreurs : {total_errors}")

print("Appuyez sur une touche pour fermer la fenêtre...")
input()

