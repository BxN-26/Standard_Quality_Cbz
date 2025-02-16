import os
import subprocess

def convert_pdf_to_images(input_dir, output_dir):
    """
    Convertit tous les fichiers PDF d'un répertoire en images JPG de haute qualité
    et les stocke dans des répertoires individuels portant le même nom que chaque fichier PDF.
    
    :param input_dir: Répertoire contenant les fichiers PDF
    :param output_dir: Répertoire où stocker les images converties
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(input_dir, filename)
            folder_name = os.path.splitext(filename)[0]
            pdf_output_dir = os.path.join(output_dir, folder_name)
            
            if not os.path.exists(pdf_output_dir):
                os.makedirs(pdf_output_dir)
            
            output_pattern = os.path.join(pdf_output_dir, folder_name + "-%03d.jpg")
            
            command = [
                "convert",
                "-density", "300",  # Haute qualité (DPI élevé)
                pdf_path,
                "-quality", "100",  # Meilleure qualité JPG
                output_pattern
            ]
            
            try:
                subprocess.run(command, check=True)
                print(f"Conversion réussie : {pdf_path} -> {pdf_output_dir}")
            except subprocess.CalledProcessError as e:
                print(f"Erreur lors de la conversion de {pdf_path}: {e}")

if __name__ == "__main__":
    # Les chemins doivent être entre guillemets.
    input_directory = "/home/serveur/Documents/BDs/pdfs/"  # Répertoire de travail sous Ubuntu
    output_directory = "/home/serveur/Documents/BDs/pdfs/Sortie/"  # Répertoire de sortie
    
    convert_pdf_to_images(input_directory, output_directory)

