import os
import shutil
import glob
from configparser import ConfigParser
from pathlib import Path
import platform

config = ConfigParser()
config.read('../config.ini')

cwd = Path.cwd()
output_dir = Path(config.get('get_all_results', 'output_dir').strip('"'))
base_folder = Path(config.get('get_all_results', 'base_folder').strip('"'))

# Gestione percorsi troppo lunghi su Windows
if platform.system() == "Windows":
    output_dir = Path(f"\\\\?\\{output_dir}")
    base_folder = Path(f"\\\\?\\{base_folder}")

def get_path_first_subfolder(folder):
    subfolders = [f for f in folder.iterdir() if f.is_dir()]
    if subfolders:
        return subfolders[0]

def examine_folders_in_directory(directory):
    # Verifica se il percorso specificato è una directory
    if not directory.is_dir():
        print(f"{directory} non è una directory valida.")
        return

    # Ottieni la lista dei percorsi completi delle cartelle contenute nella directory
    folders = [f for f in directory.iterdir() if f.is_dir()]

    # Array che conterrà i percorsi alla prima cartella contenuta in ogni elemento di "folders"
    first_subfolder_paths = []

    if folders:
        for folder in folders:
            first_subfolder_paths.append(get_path_first_subfolder(folder))

    for subfolder in first_subfolder_paths:
        if subfolder:
            if "TestSuite" in [item.name for item in subfolder.iterdir()]:
                xls_path = get_path_first_subfolder(subfolder / "TestSuite")
                file_list = glob.glob(f"{xls_path}/*.xls")
                for file in file_list:
                    copy_report(xls_path, file)
            else:
                print(f"Cartella TestSuite non trovata in {subfolder}")
        else:
            print(f"Trovata cartella priva di report")

def copy_report(source_path, file):
    if not output_dir.exists():
        output_dir.mkdir(parents=True)

    try:
        shutil.copy(source_path / file, output_dir)
    except Exception as e:
        print(f"Errore durante lo spostamento del file: {e}")

examine_folders_in_directory(base_folder)
