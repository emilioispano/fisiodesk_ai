## AI Assistant: Integrazione Query Intelligenti per Professionisti Sanitari

### Contesto del Sistema Attuale

**Dreambuilders Srl** sviluppa gestionali cloud per professionisti sanitari con due prodotti principali:
- **FisioDesk**: Gestionale specializzato per fisioterapisti
- **Dottai**: Gestionale per professionisti sanitari in generale

Entrambe le piattaforme condividono un'architettura comune e funzionalità chiave che includono:
- **Calendario e gestione appuntamenti**: Pianificazione integrata con reminder automatici
- **Cartella paziente personalizzabile**: Archiviazione di referti, allegati e annotazioni sui trattamenti
- **Fatturazione elettronica e sanitaria**: Gestione automatizzata delle fatture
- **Gestione multi-utente**: Supporto per diversi livelli di accesso

**Stack tecnologico comune:**
- Backend: SpringBoot 3 + Java 17 + Gradle
- Database: MongoDB
- Frontend: Angular + Tailwind CSS

**Architettura dati attuale (MongoDB Collections):**
```javascript
// schede_valutazione - Valutazioni cliniche dei professionisti sanitari
{
  _id: ObjectId(),
  paziente_id: ObjectId(),
  data: ISODate(),
  descrizione: "Paziente riferisce miglioramento significativo del dolore lombare. Scala del dolore da 8/10 a 3/10. Mobilità migliorata, riesce a camminare per 30 minuti senza difficoltà. Consiglio di proseguire con terapia conservativa e controllo tra 15 giorni...",
  professionista_id: ObjectId()
}

// diario_trattamenti - Registro delle sedute e trattamenti
{
  _id: ObjectId(),
  paziente_id: ObjectId(),
  data: ISODate(),
  descrizione: "Seduta completata. Paziente ha mostrato buona compliance alle indicazioni terapeutiche. Miglioramento dei parametri clinici. Applicata terapia specifica. Paziente riferisce riduzione significativa della sintomatologia dolorosa...",
  professionista_id: ObjectId()
}

// eventi_calendario - Gestione appuntamenti studio
{
  _id: ObjectId(),
  paziente_id: ObjectId(),
  data: ISODate(),
  stato: "prenotato|completato|no_show|cancellato",
  durata: 60,
  professionista_id: ObjectId(),
  note: "Controllo post-trattamento"
}

// pazienti - Anagrafica pazienti
{
  _id: ObjectId(),
  nome: "Mario Rossi",
  cognome: "Rossi",
  eta: 54,
  telefono: "+39 333 123 4567",
  email: "mario.rossi@email.com",
  professionista_principale: ObjectId(),
  data_registrazione: ISODate(),
  stato: "attivo|sospeso|archiviato"
}
```

### Il Problema
I professionisti sanitari vogliono poter fare query intelligenti sui loro dati clinici. Il tuo compito è costruire un sistema che possa rispondere a questa query complessa:

**🎯 Query Target:**
*"Mostra pazienti con dolore lombare che hanno mostrato miglioramento negli ultimi 3 mesi ma hanno saltato l'ultimo appuntamento"*

**Perché è complessa:**
- Richiede **AI** per interpretare "miglioramento" dai testi liberi delle valutazioni
- Combina **multiple collections** (schede_valutazione, eventi_calendario, pazienti)
- Filtra per **timeframe** specifico ("ultimi 3 mesi")
- Correla **compliance del paziente** con **progressi clinici**

**Vincoli operativi:**
- ⚡ Performance: <2 secondi con 50+ professionisti concorrenti
- 💰 Budget limitato per API calls AI
- 🔄 Integrazione con sistemi esistenti (SpringBoot + MongoDB)
- 📊 Accuratezza per decisioni cliniche e gestione pazienti

### Il Tuo Compito
Progetta e implementa come integrare AI nei sistemi esistenti (FisioDesk e Dottai) per rispondere a questa query. Hai **5 giorni** per completare il tutto.

**🎯 Obiettivo:** Creare un **MVP funzionante** che dimostra le tue competenze di problem-solving e system design. Non cerchiamo un sistema production-ready, ma vogliamo vedere come approcci e risolvi problemi complessi in un contesto reale di gestionali per professionisti sanitari.

---

## Cosa Devi Fare

### 1. Analisi del Problema
Analizza la query target e progetta la soluzione:
- **Dove sono le informazioni** necessarie per rispondere?
- **Come estrarre** "miglioramento" da testi liberi?
- **Come identificare** "dolore lombare" tra diagnosi + testi?
- **Come definire** "ultimo appuntamento saltato"?
- **Quale architettura** permette risposte <2 secondi?
- **Come gestire** i costi delle API AI?
- **Cosa succede** se l'AI non funziona?

### 2. Progettazione della Soluzione
**Data Strategy (Come organizzi i dati per query efficienti):**
- Come gestisci i testi liberi per query veloci? (non puoi fare AI su tutto ogni volta)
- Dove e quando processi con AI? (real-time vs batch preprocessing)
- Come memorizzi/organizzi i risultati? (nuove collections, cache, indici)

**Query Processing (Come trasformi la richiesta in risposta):**
- Come scomponi la query naturale in operazioni concrete?
- Come combini ricerca su dati strutturati + analisi AI sui testi?
- Come ranki e presenti i risultati finali al dottore?

**Performance & Scalability (Come mantieni il sistema veloce):**
- Come rispetti il vincolo <2s con molti utenti concorrenti?
- Come riduci i costi delle API AI mantenendo l'accuratezza?
- Come gestisci l'aggiornamento dei dati quando arrivano nuove schede?

### 3. Implementazione MVP
**Il sistema deve:**
- Identificare pazienti con dolore lombare (da testi delle valutazioni e trattamenti)
- Analizzare "miglioramento" dai testi delle schede_valutazione e diario_trattamenti
- Filtrare per timeframe "ultimi 3 mesi"
- Identificare chi ha saltato l'ultimo appuntamento nel calendario (collection eventi_calendario)
- Presentare risultati in modo utile per il professionista sanitario

---

## Deliverable Richiesti

### **Deliverable Finali:**
1. **Diagramma architettura** - Schema chiaro della tua soluzione (Excalidraw va benissimo)
2. **GitHub repository** con:
   - Codice dell'MVP funzionante
   - Docker Compose per setup facile
   - README con istruzioni setup
3. **Nel README documenta:**
   - Come far partire il sistema
   - 2-3 bullet points sui trade-offs principali che hai fatto
   - Demo della query target funzionante

**💡 Ricorda:** È un MVP per valutare le tue competenze, non un sistema production-ready. Concentrati su funzionalità e chiarezza del design.

---

## Criteri di Valutazione

### **System Design & Problem Solving:**
- Come scomponi il problema complesso
- Scelte architetturali appropriate per un MVP
- Considerazioni pratiche (performance, costi, vincoli)
- Gestione di trade-offs e edge cases

### **Implementation & Code Quality:**
- MVP funzionante end-to-end
- Codice pulito e ben strutturato
- Setup facile con Docker Compose
- Gestione errori di base

### **Technical Communication:**
- README chiaro e completo
- Diagramma architetturale comprensibile
- Giustificazione delle decisioni tecniche principali
- Dimostrazione del sistema funzionante

**💡 Focus:** Valutiamo le tue competenze di ingegneria e problem-solving, non la perfezione del codice. Gli aspetti di production-readiness li discuteremo durante la call.

---

## Note Importanti

- **Tempo**: 5 giorni dalla ricezione del compito
- **Obiettivo**: MVP funzionante che dimostra le tue competenze
- **Linguaggio**: Libera scelta (menziona nel README il perché - considera lo stack FisioDesk)
- **AI Provider**: Puoi usare OpenAI, Anthropic, o mock intelligente
- **Database**: Simula MongoDB con strutture appropriate (in-memory va bene)
- **Dati di test**: Coprono Marzo-Dicembre 2024; per "ultimi 3 mesi" usa una data di riferimento esplicita (es. 2024-12-31 o la data massima nel dataset)
- **Integrazione**: Considera l'architettura SpringBoot esistente nel design
- **Setup**: Docker Compose per facilitare la review
- **Focus**: Problem solving e design thinking, non production-readiness

**Domande?** Non esitare a chiedere chiarimenti durante lo sviluppo.
