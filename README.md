# 🚀 AI Healthcare Assignment – Intelligent Query System

Sistema per eseguire query intelligenti su dati sanitari (MongoDB) utilizzando NLP e logica applicativa.

---

## ✨ Features

- 🔍 Query in linguaggio naturale su dati clinici
- 🧠 Integrazione AI per interpretazione semantica (es. “miglioramento”)
- 🗄️ Database MongoDB con dati realistici pre-caricati
- ⚡ Architettura modulare (services, scoring, text utils)
- 🐳 Setup automatizzato tramite script

---

## 📦 Prerequisites

Assicurati di avere:

- Python 3.10+
- Docker
- Bash (Linux/macOS)

---

## ⚡ Quick Start

### 1. Setup ambiente

```bash
./init.sh
```

Questo script si occupa di:

- Creare l’ambiente (virtualenv se previsto)
- Installare le dipendenze
- Preparare il database (eventuale seed dati)
- Configurare variabili e servizi

---

### 2. Avvio applicazione

```bash
./runapp.sh
```

Questo comando:

- Avvia il backend
- Espone le API (o interfaccia)
- Connette automaticamente al database

---

## 📁 Project Structure

```
.
├── app/
│   ├── main.py          # Entry point applicazione
│   ├── services.py      # Logica di business
│   ├── scoring.py       # Ranking / scoring risultati
│   ├── text_utils.py    # NLP e parsing testo
│   ├── db.py            # Connessione MongoDB
│   ├── models.py        # Modelli dati
│   └── config.py        # Configurazioni
│
├── data/                # Dataset di test
│
├── init/                # Script di inizializzazione
│   └── init.sh
│
├── runapp.sh            # Avvio applicazione
├── init.sh              # Setup ambiente
└── README.md
```

---

## 🧠 Query Target

Il sistema è progettato per gestire query complesse come:

> “Mostra pazienti con dolore lombare che hanno mostrato miglioramento negli ultimi 3 mesi ma hanno saltato l'ultimo appuntamento”

---

## 🔍 Come Funziona

Il flusso è:

1. **Parsing query naturale**
   - Estrazione entità (dolore lombare, miglioramento, timeframe)
   - Normalizzazione linguistica

2. **Query su MongoDB**
   - Join logiche tra:
     - `pazienti`
     - `schede_valutazione`
     - `eventi_calendario`

3. **Scoring / ranking**
   - Matching semantico
   - Filtri temporali
   - Compliance paziente

4. **Output finale**
   - Lista pazienti rilevanti

---

## 🗄️ Database

Le principali collections:

- `pazienti`
- `schede_valutazione`
- `diario_trattamenti`
- `eventi_calendario`

Contengono dati realistici con variabilità linguistica (es. lombalgia, low back pain, ecc.).

---

## 🧪 Test e Debug

Per verificare il funzionamento:

- Controlla i log dell’app
- Testa query manualmente via API
- Verifica i dati nel database

---

## ⚙️ Troubleshooting

### Problema: l’app non parte

```bash
bash init.sh
```

→ assicurati che le dipendenze siano installate

---

### Problema: DB non raggiungibile

- Controlla config in `app/config.py`
- Verifica che MongoDB sia attivo

---

### Problema: risultati vuoti

- Verifica dataset in `data/`
- Controlla parsing in `text_utils.py`

---

## 🧩 Development Workflow

1. Setup iniziale:

```bash
bash init.sh
```

2. Avvio:

```bash
bash runapp.sh
```

3. Modifica codice in `app/`

4. Restart app

---

## 🎯 Assignment Goal

Questo progetto serve a dimostrare:

- System design
- Integrazione AI + database
- Gestione query complesse
- Trade-off tra performance e accuratezza

---

## 📌 Note

- I dati coprono un periodo temporale limitato → usa una data di riferimento
- Le query richiedono interpretazione semantica (non solo filtri esatti)
