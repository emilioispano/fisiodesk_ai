# Dati di Test e Casi d'Uso

## Overview

Questo repository contiene un dataset realistico preparato per testare il sistema di query intelligenti. I dati simulano un ambiente clinico reale con pazienti, valutazioni, trattamenti e appuntamenti.

## Dati di Test Preparati

Il repository contiene un dataset realistico che supporta perfettamente la query target:

> *"Mostra pazienti con dolore lombare che hanno mostrato miglioramento negli ultimi 3 mesi ma hanno saltato l'ultimo appuntamento"*

### Casi Positivi (dovrebbero essere restituiti dalla query):

**1. Mario Rossi (paziente_id: 507f1f77bcf86cd799439011)**
- ✅ **Dolore lombare**: "dolore lombare", "lombalgia"
- ✅ **Miglioramento**: Da 8/10 a 3/10 sulla scala del dolore (Nov-Dic 2024)
- ✅ **No_show**: 20/12/2024

**2. Laura Bianchi (paziente_id: 507f1f77bcf86cd799439012)**
- ✅ **Dolore lombare**: "dolore alla bassa schiena", "rachialgia lombare"
- ✅ **Miglioramento**: Da "forte dolore" a "netto miglioramento" (Ott-Dic 2024)
- ✅ **No_show**: 22/12/2024

**3. Roberto Romano (paziente_id: 507f1f77bcf86cd799439015)**
- ✅ **Dolore lombare**: "forte low back pain", "dolore lombare"
- ✅ **Miglioramento**: Da VAS 9/10 a "completa risoluzione della lombalgia"
- ✅ **No_show**: 30/12/2024

**4. Marco Colombo (paziente_id: 507f1f77bcf86cd799439017)**
- ✅ **Dolore lombare**: "rachialgia lombare acuta", "dolore alla bassa schiena"
- ✅ **Miglioramento**: Da VAS 8/10 a "nessun dolore residuo"
- ✅ **No_show**: 31/12/2024

### Casi Negativi (non dovrebbero essere restituiti):

**5. Anna Ferrari (paziente_id: 507f1f77bcf86cd799439014)**
- ✅ **Dolore lombare**: "mal di schiena cronico", "lombalgia"
- ❌ **NO miglioramento**: "situazione stazionaria", "lieve peggioramento"
- ✅ **No_show**: 24/12/2024

**6. Giuseppe Verdi (paziente_id: 507f1f77bcf86cd799439013)**
- ❌ **NO dolore lombare**: Solo "cervicalgia acuta"
- ✅ **Miglioramento**: Da 7/10 a 4/10 (ma per cervicale)
- ❌ **NO no_show**: Ha appuntamento futuro prenotato

**7. Francesca Ricci (paziente_id: 507f1f77bcf86cd799439016)**
- ❌ **NO dolore lombare**: Solo "spalla congelata"
- ❌ **NO dati recenti**: Solo dati del giugno 2024

### Variabilità Linguistica Implementata:

**Termini per "dolore lombare":**
- "dolore lombare"
- "mal di schiena" 
- "lombalgia"
- "rachialgia lombare"
- "low back pain"
- "dolore alla bassa schiena"
- "colpo della strega"

**Indicatori di "miglioramento":**
- "miglioramento significativo"
- "ottimi progressi"
- "sta molto meglio"
- "netto miglioramento"
- "situazione eccellente"
- "completa risoluzione"
- "buon recupero"

## Struttura Collections MongoDB

### pazienti (7 record)
```javascript
{
  _id: ObjectId(),
  nome: "Mario",
  cognome: "Rossi", 
  eta: 54,
  telefono: "+39 333 123 4567",
  email: "mario.rossi@email.com",
  professionista_principale: ObjectId(),
  data_registrazione: ISODate(),
  stato: "attivo|sospeso|archiviato"
}
```

### schede_valutazione (18 record)
```javascript
{
  _id: ObjectId(),
  paziente_id: ObjectId(),
  data: ISODate(),
  descrizione: "Paziente riferisce miglioramento significativo del dolore lombare. Scala del dolore da 8/10 a 3/10. Mobilità migliorata...",
  professionista_id: ObjectId()
}
```

### diario_trattamenti (16 record)  
```javascript
{
  _id: ObjectId(),
  paziente_id: ObjectId(),
  data: ISODate(),
  descrizione: "Seduta completata con successo. Eseguita mobilizzazione lombare e TENS. Paziente risponde bene al trattamento...",
  professionista_id: ObjectId()
}
```

### eventi_calendario (21 record)
```javascript
{
  _id: ObjectId(),
  paziente_id: ObjectId(),
  data: ISODate(),
  stato: "completato|no_show|cancellato|prenotato",
  durata: 60,
  professionista_id: ObjectId(),
  note: "Controllo post-trattamento"
}
```

## Setup per Accedere ai Dati

```bash
# Avvia l'ambiente MongoDB
docker-compose up -d

# Verifica importazione dati
docker logs fisiodesk-mongodb-seed

# Accedi a MongoDB Express per esplorare i dati
http://localhost:8081
```

## Note sui Dati

- **Timeframe**: I dati coprono Marzo-Dicembre 2024; per il filtro "ultimi 3 mesi" usa una data di riferimento esplicita (es. 2024-12-31 o la data massima nel dataset)
- **Realismo**: Le descrizioni cliniche usano terminologia medica reale
- **Complessità**: Include casi edge come peggioramenti, patologie diverse, stati diversi degli appuntamenti
- **Scalabilità**: Design pronto per essere espanso con più pazienti e professionisti
