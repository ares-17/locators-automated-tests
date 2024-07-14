import os
import glob
import shutil
import subprocess
from datetime import datetime
import requests
import json
from configparser import ConfigParser
import time
import zipfile
import sys
from pathlib import Path
import platform

config = ConfigParser()
config.read('../config.ini')

current_date = datetime.today().strftime('%d_%m_%Y_%H_%M')

project_location = Path(config.get('general', 'project_location').strip('"'))
cloned_project_path = Path(config.get('execute_all_tests', 'cloned_project_path').strip('"'))
owner = config.get('execute_all_tests', 'owner').strip('"')
repo = config.get('execute_all_tests', 'repo').strip('"')
old_locators_path = Path(config.get('execute_all_tests', 'old_locators_path').strip('"'))
github_actions_path = Path(config.get('execute_all_tests', 'github_actions_path').strip('"'))

pom_files = [Path(item.strip().strip('"')) for item in config.get('execute_all_tests', 'pom_files').split(',')]
actions_files = [Path(item.strip().strip('"')) for item in config.get('execute_all_tests', 'actions_files').split(',')]
tags = [item.strip().strip('"') for item in config.get('execute_all_tests', 'tags').split(',')]

created_tags = []

def run_script(script):
    subprocess.run(script, shell=True, check=True, stdout=subprocess.DEVNULL)

def clean_workspace():
    run_script(f"git reset --hard origin/master")
    run_script(f"git checkout master")

def update_pom():
    for file in pom_files:
        with open(file, "rt") as fin:
            data = fin.read()
            # update chrome driver to 5.7.0
            data = data.replace('<version>4.0.0</version>', '<version>5.7.0</version>')
        
        with open(file, "wt") as fout:
            fout.write(data)

def update_action_files():
    for file in actions_files:
        file_path = file.resolve()
        if file_path.exists():
            with open(file_path, "rt") as fin:
                data = fin.read()
                data = data.replace('HookTestRepo', repo)
                data = data.replace('Tesi-StrumentoGenerale', repo)
            
            with open(file_path, "wt") as fout:
                fout.write(data)
        else:
            print(f"Il file {file} non esiste.")

def remove_old_locators():
    fileList = old_locators_path.glob("*.java")
    for filePath in fileList:
        try:
            filePath.unlink()
        except Exception as e:
            print(f"Error while deleting file {filePath}: {e}")

def add_new_locators():
    fileList = project_location.glob('test_cases/*.java')
    for filePath in fileList:
        shutil.copy(filePath, old_locators_path)

def create_branch(tag_name):
    branch = f"{tag_name}_branch_{current_date}"
    run_script(f"git checkout -b {branch} tags/{tag_name}")
    return branch

def commit_push_branch(branch):
    run_script("git add .")
    run_script(f'git commit -m "Auto created commit at {current_date}"')
    run_script(f"git push -u origin {branch}")

def create_github_release(tag_name, branch):
    name = f"{tag_name}_test_release"
    body = f"Automatic release creation on {current_date}"
    new_tag_name = f"{tag_name}_{current_date}"
    created_tags.append(new_tag_name)

    command = [
        "gh", "api",
        "--method", "POST",
        "-H", "Accept: application/vnd.github+json",
        "-H", "X-GitHub-Api-Version: 2022-11-28",
        f"/repos/{owner}/{repo}/releases",
        "-f", f"tag_name={new_tag_name}",
        "-f", f"target_commitish={branch}",
        "-f", f"name={name}",
        "-f", f"body={body}",
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        response = json.loads(result.stdout)
        if response:
            print("Release creata con successo!")
            print("ID della release:", response["id"])
        else:
            print("Creazione della release fallita")
    except subprocess.CalledProcessError as e:
        print("Errore durante la creazione della release su GitHub:")
        print(e)

def copy_github_actions():
    fileList = Path('.github/workflows').glob('*.yml')
    for filePath in fileList:
        try:
            filePath.unlink()
        except Exception as e:
            print(f"Error while deleting file {filePath}: {e}")

    fileList = github_actions_path.glob('*.yml')
    for filePath in fileList:
        shutil.copy(filePath, Path('.github/workflows/'))

def remove_old_tests():
    test_suite_path = Path("TestSuite")
    try:
        if test_suite_path.exists():
            shutil.rmtree(test_suite_path)
    except OSError as e:
        print(f"Errore durante la rimozione della cartella TestSuite: {e}")

def download_releases():
    base_url = f"https://github.com/{owner}/{repo}/archive/refs/tags/"
    output_dir = project_location / "release_download"

    # per percorsi troppo lunghi su windows
    if platform.system() == "Windows":
        output_dir = Path(f"\\\\?\\{output_dir}")

    if not output_dir.exists():
        output_dir.mkdir(parents=True)

    for tag_name in created_tags:
        release_url = base_url + tag_name + ".zip"
        output_zip_path = output_dir / f"{tag_name}.zip"
        output_extract_path = output_dir / f"{tag_name}"

        # Scarica la release e salvala nella cartella di output
        response = requests.get(release_url)
        if response.status_code == 200:
            with open(output_zip_path, 'wb') as f:
                f.write(response.content)
            print(f"[{tag_name}]: Release {tag_name} scaricata con successo.")

            # Estrai il contenuto dello zip
            try:
                with zipfile.ZipFile(output_zip_path, 'r') as zip_ref:
                    zip_ref.extractall(output_extract_path)
                print(f"[{tag_name}]: Contenuto della release {tag_name} estratto con successo.")
            except Exception as e:
                print(f"[{tag_name}]: Errore durante l'estrazione della release {tag_name}: {e}")

            # Elimina lo zip dopo l'estrazione
            output_zip_path.unlink()
        else:
            print(f"[{tag_name}]: Errore durante il download della release {tag_name}: {response.status_code}")

def wait_for_actions_completion():
    base_url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs"
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }
    time.sleep(30)
    while True:
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        all_completed = all(run["status"] in ["completed", "cancelled", "skipped"] for run in data["workflow_runs"])
        if all_completed:
            print("Tutte le GitHub Actions sono completate --------------")
            break
        else:
            time.sleep(30)

def tag_contain_k(tag):
    return True if 'k' in tag else False

def call_k_trigger_action(branch_name):
    run_script(f"gh workflow run mainOnPush.yml --ref {branch_name}")

os.chdir(cloned_project_path)
clean_workspace()

for tag in tags:
    print(f"INIT [{tag}] ----------------")
    print(f"[{tag}]: init branch")
    branch_name = create_branch(tag)
    print(f"[{tag}]: update pom")
    update_pom()
    print(f"[{tag}]: update action files")
    update_action_files()
    print(f"[{tag}]: removing old locators")
    remove_old_locators()
    print(f"[{tag}]: adding new locators")
    add_new_locators()
    print(f"[{tag}]: copying GitHub actions")
    copy_github_actions()
    print(f"[{tag}]: removing older tests")
    remove_old_tests()
    print(f"[{tag}]: commit and push")
    commit_push_branch(branch_name)

    if tag_contain_k(tag):
        call_k_trigger_action(branch_name)
        continue

    print(f"[{tag}]: creating release")
    create_github_release(tag, branch_name)
    print(f"[{tag}]: end tag\n\n")

print(f"WAITING FOR ACTIONS TO COMPLETE ----------------")
# wait for mainOnPush.yml action for "k" tags
wait_for_actions_completion()
for tag in tags:
    if tag_contain_k(tag):
        print(f"[{tag}]: creating release")
        create_github_release(tag, branch_name)
        print(f"[{tag}]: end tag\n\n")


wait_for_actions_completion()

print(f"INIT RELEASE DOWNLOAD ----------------")
download_releases()
