import os
import zipfile
import shutil
from configparser import ConfigParser
import subprocess
import glob

config = ConfigParser()
config.read('../config.ini')

zip_file_path = config.get('aggregate_reports', 'zip_location').strip('"')
source_reports = config.get('aggregate_reports', 'source_reports').strip('"')
final_report_destination_path = config.get('aggregate_reports', 'final_report_path').strip('"')
old_final_report_file = config.get('aggregate_reports', 'old_final_report_file').strip('"')

zip_file_name = os.path.splitext(os.path.basename(zip_file_path))[0]
extracted_folder = os.path.join(os.getcwd(), zip_file_name)
target_folder = os.path.join(extracted_folder, 'target')
jar_name = os.path.join(target_folder, 'unisciReportExcel-0.0.1-jarReportTest.jar')
surefire_reports_path=os.path.join(target_folder, 'surefire-reports')
final_report_path=os.path.join(target_folder, 'reportComplessivo.xls')

def remove_old_report_file():
    old_report = os.path.join(extracted_folder, 'reportComplessivo')
    if os.path.exists(old_report):
        try:
            os.remove(old_report)
        except:
            print("Error while deleting file: ", old_report)

def extract():
    try:
        old_exracted_folder=os.path.join(os.getcwd(), 'unisciReportExcel')
        if os.path.exists(old_exracted_folder):
            shutil.rmtree(old_exracted_folder)
    except Exception as e:
        print(f"Si è verificato un errore durante l'eliminazione della cartella: {e}")

    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(os.getcwd())

def open_target():
    os.makedirs(target_folder, exist_ok=True)
    os.chdir(target_folder)

def remove_old_surefire_report_files():
    try:
        if not os.path.exists(surefire_reports_path):
            print(f"La cartella '{surefire_reports_path}' non esiste.")
            return

        for filename in os.listdir(surefire_reports_path):
            file_path = os.path.join(surefire_reports_path, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
    except Exception as e:
        print(f"Si è verificato un errore durante la rimozione dei file: {e}")

def copy_reports():
    os.makedirs(target_folder, exist_ok=True)
    fileList = glob.glob(f'{source_reports}/*.xls')
    for filePath in fileList:
        shutil.copy(filePath, surefire_reports_path)

def execute_jar():
    subprocess.run(['java', '-jar', jar_name, surefire_reports_path, 'reportComplessivo'], check=True, capture_output=True)

def copy_final_report():
    shutil.copy(final_report_path, final_report_destination_path)

def remove_old_final_report():
    if os.path.isfile(old_final_report_file):
        os.remove(old_final_report_file)

extract()
open_target()
remove_old_report_file()
remove_old_surefire_report_files()
copy_reports()
execute_jar()
remove_old_final_report()
copy_final_report()