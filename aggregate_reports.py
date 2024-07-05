import os
import zipfile
import shutil
from configparser import ConfigParser
import subprocess
import glob
import platform
from pathlib import Path

config = ConfigParser()
config.read('../config.ini')

zip_file_path = Path(config.get('aggregate_reports', 'zip_location').strip('"'))
source_reports = Path(config.get('aggregate_reports', 'source_reports').strip('"'))
final_report_destination_path = Path(config.get('aggregate_reports', 'final_report_path').strip('"'))
old_final_report_file = Path(config.get('aggregate_reports', 'old_final_report_file').strip('"'))

zip_file_name = zip_file_path.stem
extracted_folder = Path.cwd() / zip_file_name
target_folder = extracted_folder / 'target'
jar_name = str(target_folder / 'unisciReportExcel-0.0.1-jarReportTest.jar')
surefire_reports_path = target_folder / 'surefire-reports'

def remove_old_report_file():
    old_report = extracted_folder / 'reportComplessivo'
    if old_report.exists():
        try:
            old_report.unlink()
        except Exception as e:
            print(f"Error while deleting file {old_report}: {e}")

def extract():
    try:
        old_extracted_folder = Path.cwd() / 'unisciReportExcel'
        if old_extracted_folder.exists():
            shutil.rmtree(old_extracted_folder)
    except Exception as e:
        print(f"Error while removing the folder: {e}")

    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(Path.cwd())

def open_target():
    target_folder.mkdir(parents=True, exist_ok=True)
    os.chdir(target_folder)

def remove_old_surefire_report_files():
    try:
        if not surefire_reports_path.exists():
            print(f"The folder '{surefire_reports_path}' does not exist.")
            return

        for file_path in surefire_reports_path.iterdir():
            if file_path.is_file():
                file_path.unlink()
    except Exception as e:
        print(f"Error while removing files: {e}")

def copy_reports():
    target_folder.mkdir(parents=True, exist_ok=True)
    file_list = glob.glob(f'{source_reports}/*.xls')
    for file_path in file_list:
        shutil.copy(file_path, surefire_reports_path)

def execute_jar():
    try:
        subprocess.run(['java', '-jar', jar_name, str(surefire_reports_path), 'reportComplessivo'], check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print("Error executing JAR file:")
        print("Command:", e.cmd)
        print("Return code:", e.returncode)
        print("Output:", e.output)
        print("Stderr:", e.stderr)

def copy_final_report():
    final_report = target_folder / 'reportComplessivo.xls'
    if final_report.exists():
        shutil.copy(final_report, final_report_destination_path)
    else:
        print(f"Error: {final_report} not found.")

def remove_old_final_report():
    if old_final_report_file.is_file():
        old_final_report_file.unlink()

extract()
open_target()
remove_old_report_file()
remove_old_surefire_report_files()
copy_reports()
execute_jar()
remove_old_final_report()
copy_final_report()
