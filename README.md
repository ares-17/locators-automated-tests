# Test automatici
Nella presente cartella sono definiti una serie di script Python per la gestione automatizzata dei test.
Il presente repository è pensato per esser integrato nei repository [A1-ContactList](https://github.com/ares-17/A1-ContactList) e [A2-Spotify](https://github.com/ares-17/A2-Spotify) o simili per semplificare la gestione dei file condivisi che eseguono i test.

Dunque per l'esecuzione degli script python, è necessario il file **config.ini** che nel quale siano memorizzate informaioni relative al repository sul quale effettuare i test. E' fornito un esempio col file **config.example.ini**

In particolare:
- **execute_all_tests.py** file che esegue i test
- **get_all_results.py** file che copia i risultati prodotti in _release\_download_ in _Report-Seprati_ cosicché l'esecuzione dell'azione _generaReportFinale.yml_ crei un report complessivo
- **get_all_tags.py** semplice script che crea un file contenente i tag presenti nel repository e dai quali sono creati i nuovi branch di test. Non considera altri tag
- **aggregate_reports.py** aggrega i file raccolti con **get_all_results.py** e genera il file _reportComplessivo.xls_

## get_all_tags
Genera un file che risulta utile per popolare la lista _tags_ nel file _config.ini_ di riferimento.

## execute_all_tests
Per eseguire i test sfruttando le azioni di di Github è necessario che sia clonato il repository sul quale sono eseguiti i test in un'altra cartella; nella cartella clonata questo sono eseguite le operazioni di **execute_all_tests.py**, nel quale:
- crea un branch per ogni tag
- ne aggiorna i file pom (per non generare eccezioni di incompatibilità dei test)
- aggiorna i file contenenti le azioni compiute dai test rimuovendo i path assoluti del vecchio repository 
- rimuove i vecchi casi di test
- aggiunge i casi di test presenti in _automated-test/test\_cases_
- copia l'ultima versione delle azioni di Github
- rimuove la cartella "TestSuite" contenente i vecchi casi di test
- esegue una commit e push con le modifiche
- crea una release del branch

Infine, dopo aver atteso un tempo prestabilito (impostato inizialmente a 1 minuto):
- attende che tutte le azioni su Github siano terminate
- scarica nella cartella _release\_download_ i file delle release

Lo script tratta diversamente i test della famiglia "k" (es. v_1k_2b) poichè questi richiedono il completamento dell'esecuzione dell'azione _mainOnPush_ che inietta l'identificatore (hook) al nuovo elemento HTML aggiunto dal test.

### Tag della tipologia k
Quindi risulta necessario che si attendi la terminazione delle azioni di Github scatenate manualmente dopo la commit e push. Concluse, l'algoritmo crea una release per ogni tag con "k" e segue il normale flusso descritto

## get_all_results
L'esecuzione del file **get_all_results.py** segue quella del file **execute_all_tests.py**.

## aggregate_reports
L'esecuzione del file **aggregate_reports.py** segue quella del file **get_all_results.py**.