import os
import subprocess
import glob
import shutil
import zipfile
import time
import re
import concurrent.futures
import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageOps
import cv2
import numpy as np
from tqdm import tqdm

# Chemins vers les exécutables
seven_zip_path = '/usr/bin/7z'
unrar_path = '/usr/bin/unrar'

# Interface graphique avec Tkinter
root = tk.Tk()
root.title("Traitement d'Images BD")
root.geometry("500x300")

selected_directory = tk.StringVar()
resize_option = tk.StringVar(value="BD")

# Fonction pour choisir un répertoire
def select_directory():
    folder_selected = filedialog.askdirectory(title="Sélectionnez le dossier de traitement")
    if folder_selected:
        selected_directory.set(folder_selected)

def start_processing():
    global input_directory
    input_directory = selected_directory.get()
    if not input_directory:
        print("Aucun dossier sélectionné. Fin du programme.")
        return
    root.quit()
    root.destroy()

# Interface utilisateur
frame = ttk.Frame(root, padding="10")
frame.pack(fill=tk.BOTH, expand=True)

ttk.Label(frame, text="Sélectionnez un dossier :").pack()
entry = ttk.Entry(frame, textvariable=selected_directory, width=50)
entry.pack()

ttk.Button(frame, text="Parcourir", command=select_directory).pack()

# Sélection de la résolution
ttkradio1 = ttk.Radiobutton(frame, text="BD (2480x3508)", variable=resize_option, value="BD")
ttkradio1.pack()
ttkradio2 = ttk.Radiobutton(frame, text="Comic/Manga (1800x2880)", variable=resize_option, value="Manga")
ttkradio2.pack()

# Bouton de démarrage
ttk.Button(frame, text="Lancer le traitement", command=start_processing).pack()

root.mainloop()

resize_dimensions = (2480, 3508) if resize_option.get() == "BD" else (1800, 2880)

log_file_path = os.path.join(input_directory, "process_log.txt")
total_images_processed = 0
total_errors = 0

def log_message(message):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file_path, "a", encoding='utf-8') as log_file:
        log_file.write(f"[{timestamp}] {message}\n")
    print(f"[{timestamp}] {message}")

def remove_white_borders(img):
    img_gray = img.convert("L")
    np_image = np.array(img_gray)
    _, thresh = cv2.threshold(np_image, 240, 255, cv2.THRESH_BINARY)
    coords = cv2.findNonZero(255 - thresh)
    if coords is not None:
        x, y, w, h = cv2.boundingRect(coords)
        img = img.crop((x, y, x + w, y + h))
    return img

def process_image(input_file_path):
    global total_images_processed, total_errors
    try:
        with Image.open(input_file_path) as img:
            img = remove_white_borders(img)
            # Si l'image est en paysage (largeur > hauteur), on inverse les dimensions
            if img.width > img.height:
                target_dimensions = (resize_dimensions[1], resize_dimensions[0])
            else:
                target_dimensions = resize_dimensions
            img = img.resize(target_dimensions, Image.LANCZOS)
            img = img.convert("RGB")
            output_file_path = os.path.splitext(input_file_path)[0] + '.jpg'
            img.save(output_file_path, 'JPEG', dpi=(300, 300))
            log_message(f"Fichier sauvegardé : {output_file_path}")
            total_images_processed += 1
    except Exception as e:
        log_message(f"Erreur lors du traitement de l'image {input_file_path} : {e}")
        total_errors += 1

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
    log_message(f"Erreur lors de la décompression : {e}")
    total_errors += 1

log_message("Début du traitement des images...")
try:
    image_files = [os.path.join(subdir, file) for subdir, _, files in os.walk(input_directory) for file in files if file.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"))]
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(process_image, image_files)
    log_message("Traitement des images terminé.")
except Exception as e:
    log_message(f"Erreur lors du traitement des images : {e}")
    total_errors += 1

log_message("Début de la suppression des fichiers non JPG...")
try:
    for subdir, _, files in os.walk(input_directory):
        for file in files:
            if not file.lower().endswith('.jpg'):
                os.remove(os.path.join(subdir, file))
    log_message("Suppression terminée.")
except Exception as e:
    log_message(f"Erreur lors de la suppression : {e}")
    total_errors += 1

log_message(f"Total d'images traitées : {total_images_processed}")
log_message(f"Total d'erreurs : {total_errors}")

