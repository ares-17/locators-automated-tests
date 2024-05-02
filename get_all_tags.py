import os
import subprocess
import re
from datetime import datetime
from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')

# Funzione per eseguire uno script bash
def run_script(script):
    subprocess.run(script, shell=True, check=True)

def get_tags():
    try:
        current_dir = os.getcwd()
        git_repo_path = config.get("get_all_tags", "git_repo_path")
        os.chdir(git_repo_path)

        tags = subprocess.check_output(["git", "tag"], text=True).splitlines()
        tag_pattern = r'v_\d+[a-z]_\d+[a-z](_m\d+)?'
        filtered_tags = [tag for tag in tags if re.match(tag_pattern, tag)]

        print(f"Ricavati {len(filtered_tags)} tags, esclusi {len(set(tags) - set(filtered_tags))}")

        os.chdir(current_dir)
        return filtered_tags

    except subprocess.CalledProcessError:
        print("Errore: Non è una cartella di un repository Git.")
    except Exception as e:
        print(f"Errore: {e}")

def find_commits_with_tag(tag_list):
    try:
        commits_with_tag = set()
        tags_without_commit = []
        tags_with_commit = []

        for tag in tag_list:
            # Rimuovi il prefisso "v_" dal tag
            tag_no_prefix = tag.replace("v_", "")
            commit_list = subprocess.check_output(["git", "log", "--grep", tag_no_prefix, "--format=%H"], text=True).splitlines()
            commits_with_tag.update(commit_list)

            if(len(commit_list) == 0):
                tags_without_commit.append(tag)
            else:
                tags_with_commit.append(tag)

        return list(commits_with_tag), tags_without_commit, tags_with_commit

    except subprocess.CalledProcessError:
        print("Errore: Impossibile trovare le commit.")
        return None
    except Exception as e:
        print(f"Errore: {e}")
        return None    

def create_tags_file(tag_list):
    # Genera il nome del file usando la data corrente
    current_date = datetime.today().strftime('%d-%m-%Y')
    file_name = f"tags-{current_date}.txt"

    # Crea il file nella directory corrente e scrivi gli elementi della lista
    with open(file_name, 'w') as file:
        for tag in tag_list:
            file.write(tag + '\n')

    print(f"File '{file_name}' creato con successo.")

def filter_strings(strings):
    # Ordina le stringhe in modo crescente in base alla loro lunghezza
    sorted_strings = sorted(strings, key=len)
    
    filtered_set = set()

    # Itera attraverso le stringhe in ordine crescente di lunghezza
    for string in sorted_strings:
        is_contained = any(string in existing_string for existing_string in filtered_set)
        if not is_contained:
            filtered_set.add(string)
    
    return filtered_set

tags = get_tags()
commits_with_tag, tags_without_commit, tags_with_commit = find_commits_with_tag(tags)
print(f"Numero totale commit distinte: {len(commits_with_tag)}")
print(f"tags con commit: {len(tags_with_commit)}")
print(f"tags senza commit: {len(tags_without_commit)}")

create_tags_file(tags)