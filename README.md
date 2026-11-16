# ✈️ Flight Scanner

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=flat&logo=python&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-F7DF1E?style=flat&logo=javascript&logoColor=black)
![Leaflet](https://img.shields.io/badge/Leaflet-1.9.4-199900?style=flat&logo=leaflet&logoColor=white)
![OpenStreetMap](https://img.shields.io/badge/Map-OpenStreetMap-7EBC6F?style=flat&logo=openstreetmap&logoColor=white)

**Flight Scanner** è un'applicazione web per il monitoraggio in tempo reale del traffico aereo tramite dati **ADS-B**. Il progetto combina un'interfaccia dashboard in stile radar (HTML/CSS/JavaScript con **Leaflet.js**) e un **reverse proxy locale in Python** progettato per funzionare sia su reti domestiche dirette sia dietro proxy scolastici/aziendali con autenticazione.

---

## ✨ Funzionalità principali

* **Radar aereo in tempo reale:** interroga automaticamente l'API pubblica [adsb.lol](https://api.adsb.lol) ogni 10 secondi e aggiorna la posizione degli aeromobili sulla mappa.
* **Tracciamento e scie di volo:** accumula in memoria lo storico delle coordinate (`storicoPosizioni`), aggiorna dinamicamente i segnaposto (`L.marker`) e disegna le traiettorie percorse (`L.polyline`) ogni 3 rilevamenti.
* **Conversione automatica della telemetria:** trasforma i dati aeronautici grezzi in unità leggibili:
  * Altitudine barometrica: da piedi (`ft`) a **metri (`m`)**.
  * Velocità al suolo (*Ground Speed*): da nodi (`kt`) a **km/h**.
* **Reverse Proxy Python multi-funzione (`proxy.py`):**
  * Serve i file statici del frontend (`index.html`, `style.css`, `app.js`).
  * Inoltra le richieste `/api` verso `api.adsb.lol` gestendo compressione `gzip` e certificati SSL.
  * Inoltra le richieste `/tiles/{z}/{x}/{y}` verso **OpenStreetMap** impostando gli header `User-Agent` e `Cache-Control` (cache di 7 giorni) richiesti dalle policy OSM.
* **Configurazione guidata da terminale:** permette di personalizzare al volo coordinate geografiche, raggio di ricerca (in km) e modalità di connessione (**Scuola** con proxy autenticato o **Casa** con connessione diretta).
* **Pannelli diagnostici integrati:** mostra un timer per il polling successivo, il contatore totale dei punti raccolti, la struttura dati JSON formattata e un registro sintetico per ogni volo rilevato.

---

## 📁 Struttura del progetto

```text
flight-scanner/
├── index.html          # Struttura della dashboard web e importazione di Leaflet
├── style.css           # Tema scuro in stile terminale/radar e layout della mappa
├── app.js              # Logica di polling, conversione dati, storico e rendering Leaflet
├── proxy.py            # Server HTTP locale e reverse proxy per API ADS-B e map tiles
└── README.md           # Documentazione del progetto
```

---

## 🛠️ Requisiti

* **Python 3.x** (il server utilizza esclusivamente moduli della libreria standard: `http.server`, `urllib`, `ssl`, `gzip`, `json`, `getpass`, `os` — nessuna dipendenza esterna da installare).
* **Browser web moderno** (Chrome, Firefox, Edge, Safari) con accesso a Internet per il caricamento di Leaflet da CDN e il recupero dei dati.

---

## 🚀 Installazione e avvio

1. **Clona il repository** (o scarica i file nella stessa cartella):
   ```bash
   git clone https://github.com/lo-zaffo/flight-scanner.git
   cd flight-scanner
   ```

2. **Avvia il server proxy locale in Python:**
   ```bash
   python3 proxy.py
   ```
   *(Su Windows puoi usare `python proxy.py`).*

3. **Segui la configurazione guidata nel terminale:**
   * **Zona di verifica:** scegli `2` per mantenere l'area predefinita (**Urbino**, lat `43.726`, lon `12.636`, raggio `50` miglia nautiche) oppure `1` per inserire latitudine, longitudine e raggio in chilometri personalizzati.
   * **Modalità di rete:**
     * `1` (**Uso a Scuola**): richiede indirizzo IP, porta, username e password del proxy HTTP/HTTPS.
     * `2` (**Uso a Casa**): utilizza la connessione diretta a Internet.

4. **Apri l'interfaccia nel browser:**
   Visita l'indirizzo:
   ```text
   http://localhost:8000
   ```

---

## ⚙️ Configurazione e personalizzazione

Puoi modificare rapidamente il comportamento dell'applicazione intervenendo sulle costanti principali nei file sorgente:

### Frontend (`app.js`)
| Costante | Valore predefinito | Descrizione |
| :--- | :--- | :--- |
| `INTERVALLO_AGGIORNAMENTO_SECONDI` | `10` | Intervallo in secondi tra due richieste consecutive all'API. |
| `OGNI_QUANTO_FARE_LINEA_SCIA_AEREI` | `3` | Numero di rilevamenti ogni cui viene tracciato un segmento rosso sulla mappa. |
| `URL_PROXY_LOCALE` | `"/api"` | Endpoint locale interrogato dal browser per ricevere i dati JSON. |

### Backend (`proxy.py`)
| Costante | Valore predefinito | Descrizione |
| :--- | :--- | :--- |
| `PORT_LOCALE_AEREI_API` | `8000` | Porta su cui resta in ascolto il server HTTP locale. |
| `API_URL_STANDARD` | `https://api.adsb.lol/v2/lat/43.726/lon/12.636/dist/50` | Endpoint ADS-B predefinito (area di Urbino). |
| `TILES_URL` | `https://tile.openstreetmap.org/{z}/{x}/{y}.png` | Server remoto da cui vengono scaricate le tessere della mappa. |

---

## 📌 Note tecniche

* **Persistenza dei dati:** lo storico `storicoPosizioni` viene mantenuto nella memoria RAM della scheda del browser. Aggiornando o chiudendo la pagina i rilevamenti accumulati vengono azzerati.
* **Identificativi dei voli:** ogni aeromobile viene indicizzato tramite il proprio *callsign* (`flight`); qualora non fosse trasmesso dal transponder, viene identificato tramite il codice esadecimale ICAO (`HEX_<codice>`).

---

## Note sullo sviluppo e utilizzo dell'IA

Quasi la totalità del codice di questo progetto è stata scritta interamente a mano. L'intelligenza artificiale è stata utilizzata esclusivamente come materiale di studio per approfondire concetti tecnici e librerie, oltre che come supporto nella fase di debug.