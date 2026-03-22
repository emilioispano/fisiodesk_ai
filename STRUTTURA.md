# Struttura del codice: package `app/`

La directory `app/` contiene la logica principale dell’applicazione ed è organizzata secondo una struttura modulare che separa chiaramente le responsabilità tra i diversi componenti: configurazione, accesso ai dati, logica applicativa, modelli, processamento del testo e scoring.

Questa organizzazione facilita la manutenzione, la scalabilità e la comprensione del sistema.

---

## `main.py`

`main.py` rappresenta il punto di ingresso dell’applicazione.

Le sue responsabilità principali sono:

- inizializzare l’esecuzione dell’applicazione;
- gestire l’input (utente o sistema esterno);
- invocare la logica applicativa;
- restituire l’output nel formato previsto.

Il file mantiene un ruolo volutamente leggero, delegando la logica operativa al modulo `services.py`.  
In questo modo si evita di mescolare gestione dell’esecuzione e logica di business, migliorando la leggibilità e la modularità del codice.

---

## `services.py`

`services.py` costituisce il livello di **orchestrazione** dell’applicazione.

Questo modulo coordina l’intero flusso di esecuzione:

1. riceve la richiesta da `main.py`;
2. recupera i dati necessari tramite `db.py`;
3. applica eventuali trasformazioni tramite `text_utils.py`;
4. calcola priorità o rilevanza tramite `scoring.py`;
5. costruisce la risposta finale.

Qui risiede la logica di dominio: è il punto in cui vengono prese le decisioni su quali dati utilizzare, come combinarli e come presentarli.

---

## `db.py`

`db.py` rappresenta il livello di **accesso ai dati** (data access layer).

Le sue responsabilità includono:

- gestione della connessione al database;
- accesso alle collezioni;
- definizione di funzioni di retrieval specializzate.

Tra le funzionalità principali:

- recupero della connessione al database;
- caricamento di strutture di supporto (es. mapping dei pazienti);
- recupero di documenti clinici recenti;
- estrazione degli eventi più recenti associati ai pazienti.

---

## `models.py`

`models.py` definisce le strutture dati utilizzate internamente all’applicazione.

Tipicamente include:

- classi che rappresentano entità di dominio (es. pazienti, documenti, eventi);
- strutture tipizzate per lo scambio di dati tra moduli;
- eventuali logiche di validazione o normalizzazione.

---

## `scoring.py`

`scoring.py` contiene la logica di **valutazione e ranking** dei dati.

Questo modulo è responsabile di:

- assegnare punteggi a documenti o eventi;
- ordinare i risultati in base alla rilevanza;
- combinare diversi criteri (es. recenza, contenuto testuale, metadati).

---

## `text_utils.py`

`text_utils.py` raccoglie le utility per il processamento del testo.

Le sue funzioni possono includere:

- normalizzazione del testo;
- pulizia (lowercasing, rimozione punteggiatura, spazi);
- tokenizzazione;
- supporto al matching testuale;
- generazione di snippet o formattazione dell’output.

---

## `config.py`

`config.py` centralizza i parametri di configurazione dell’applicazione.

Può includere:

- variabili d’ambiente;
- parametri di connessione al database;
- nomi delle collezioni;
- soglie e costanti utilizzate nei moduli di scoring e retrieval.

---

## `__init__.py`

Il file `__init__.py` definisce `app/` come package Python.

Questo permette l’utilizzo di import strutturati tra i moduli.

---

## Flusso di esecuzione

Il funzionamento complessivo dell’applicazione può essere descritto come segue:

1. `main.py` riceve una richiesta;
2. la richiesta viene passata a `services.py`;
3. `services.py` interroga il database tramite `db.py`;
4. i dati testuali vengono processati tramite `text_utils.py`;
5. i risultati vengono valutati e ordinati tramite `scoring.py`;
6. i dati vengono organizzati secondo le strutture definite in `models.py`;
7. `services.py` costruisce la risposta finale;
8. `main.py` restituisce l’output.

---

## Vantaggi dell’architettura

Questa struttura offre diversi vantaggi:

- separazione delle responsabilità;
- maggiore manutenibilità;
- facilità di debug e testing;
- possibilità di evoluzione modulare del sistema.
