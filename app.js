// untervallo ogni quanto viene fatta la richiesta all'api e cambiati i dati di conseguenza 
const INTERVALLO_AGGIORNAMENTO_SECONDI = 10;


const OGNI_QUANTO_FARE_LINEA_SCIA_AEREI = 3

// oggetto che Contiene lo storico solo nella memoria della pagina: ricaricandola, i punti vengono azzerati.
// Ogni chiave identifica un volo e il relativo array conserva i suoi rilevamenti in ordine di arrivo.
const storicoPosizioni = {}; // oggetto di javascript stile array dove ogni elemento è caraterizzato da una etichetta e un array di elementi che contiene

let aerei_disegnati = {};   // oggetto che conterra gli oggetti corrispondenti agli aerei disegnati

// variabile della mappa
var map = L.map('mappa').setView([43.726, 12.636], 8)

// Il browser chiede i dati al server Python locale, che li recupera dall'API remota.
const URL_PROXY_LOCALE = "/api";
let secondiMancanti = INTERVALLO_AGGIORNAMENTO_SECONDI;   // secondi tra una richiesta e l'altra
document.getElementById('timer').textContent = secondiMancanti;

// funzione che Scarica i dati correnti e aggiunge un nuovo punto allo storico di ciascun aereo ricevuto.
async function scaricaEAccumulaDati() {
    try {
        // La risposta del server locale contiene il JSON restituito dall'API.
        const risposta = await fetch(URL_PROXY_LOCALE); // chiama il server per i dati dell'apy,
        // la chiamata al'api effettiva viene fatta dal server python

        const dati = await risposta.json(); // legge la risposta e trasforma i valori da json a javascript

        // 'ac' e' l'elenco degli aerei; se manca, il ciclo lavora su una lista vuota.
        const aerei = dati.ac || [];    // recupera dai dati la lista degli aerei solo gli aerei
        const orario = new Date().toLocaleTimeString(); // trasforma l'ora in formato locale

        aerei.forEach(aereo => {    // ciclo che cicla per ogni elemento del vettore, elemento chiamato aereo
            // Usa il nominativo del volo quando disponibile; altrimenti identifica l'aereo con il codice hex.
            // accede alla struttura dati dell'oggetto contenuto nell'array e recupera il nome dell'aereo, assegnandolo
            // alla varianile idAereo
            const idAereo = aereo.flight ? aereo.flight.trim() : `HEX_${aereo.hex}`;

            // Crea lo spazio per i rilevamenti del volo al suo primo avvistamento.
            // controlla se dentro l'oggetto instanziato in precedenza esiste una etichetta chiamata come l'aereo della lista
            if (!storicoPosizioni[idAereo]) {
                storicoPosizioni[idAereo] = []; // se non ce crea una nuova etichetta contenente un array vuoto,
                //  dove poi andra un oggetto
            }

            // variabili temporanee
            // Converte i valori dell'API in unita' piu' pratiche da leggere: piedi in metri e nodi in km/h.
            const altitudineMetri = Math.round((aereo.alt_baro || 0) * 0.3048);
            const velocitaKmh = Math.round((aereo.gs || 0) * 1.852);

            // aggiunge un oggetto all'array di oggetti creato in precedenza contrassegnato dell'etichetta idAereo
            // e assegna al nuovo oggetto diverse variabili, con il nome prima dei duepunti, 
            // e gli assegna il valore contenuto nella variabile dopo i 2 punti
            storicoPosizioni[idAereo].push({
                lat: aereo.lat,
                lon: aereo.lon,
                altitudine_m: altitudineMetri,
                velocita_kmh: velocitaKmh,
                rotta_deg: aereo.track || 0,    // in questo caso || significa oppure per impostare 0 come valore predefinito
                ora: orario
            });
        });

        // Dopo l'accumulo aggiorna entrambe le rappresentazioni visibili dello storico.
        aggiornaInterfaccia();
    } catch (errore) {
        // L'errore viene registrato nella console; i dati gia' raccolti restano in memoria.
        console.error("Errore recupero dati:", errore);
    }
}

// funzione che ridisegna JSON e aggiorna le parti della pagina che contengono i dati dell'aereo
function aggiornaInterfaccia() {
    // La formattazione indentata rende visibili struttura e campi dei dati accumulati.
    // getElementById('outputJSON') trova il riquadro della pagina con quell’ID, gli asssegna un nuovo valore
    // JSON.stringify(storicoPosizioni, null, 2) funzione che formatta l'oggetto storicoPosioni in una stringa in formato JSON
    // storico posizioni è l'oggetto che cambia, null indica di non formattare i fioltrare i dati, 2 sono gli spazzi che vengono dati come indentazione
    document.getElementById('outputJSON').textContent = JSON.stringify(storicoPosizioni, null, 2);

    let totalePunti = 0;    // contatore dei rilevamenti di aerei
    let htmlLog = "";   // stringa contenente l'html che mostra gli aerei

    // ciclo che scorre tutte le voci di storicoPosizioni, una alla volta
    // Object.entries(storicoPosizioni) trasfforma l'oggetto storicoPosizioni in un array di array conteneti tag e contenuto del tag dentro un ulteriore array
    // const [aereo, punti] serve invece per assegnare a aereo il primo valore dell'array iterato dal ciclo in questo passaggio e a punti il secondo
    for (const [aereo, punti] of Object.entries(storicoPosizioni)) {

        // Somma i punti di tutti i voli e seleziona l'ultimo per il riepilogo.

        // punti è un array contenente oggetti che contengono i dati che arrivano dall'api
        // con punti.length ottenieamo il numero di elementi nell'array e quindi il numero di rilevamenti di quel specifico aereo
        // lo sommiamo a totalePunti, un contatore di tutti i relivamenti fatti in generale
        totalePunti += punti.length;

        // salviamo l'ultimo oggetto dell'array per mostrare le informazioni piu aggiornate sull'aereo
        const ultimo = punti[punti.length - 1];

        // scrive l'html che verra mostrato nella pagina con i vari dati dell'aereo
        // lo aggiungiamo a una stringa unica che conterra le informazioni di tutti gli aerei
        htmlLog += `<p>Volo ${aereo}: ${punti.length} rilevamenti. ` +
            `Ultimo alle ${ultimo.ora} - ` +
            `Lat: ${ultimo.lat}, Lon: ${ultimo.lon} | ` +
            `Alt: ${ultimo.altitudine_m} m | Vel: ${ultimo.velocita_kmh} km/h</p>`;

    }

    // Aggiorna la mappa, dopo aver finito il ciclo del riepilogo.
    aggiorna_mappa();

    // Aggiorna il contatore complessivo e mostra un messaggio se non e' stato trovato alcun aereo.
    document.getElementById('totalePunti').textContent = totalePunti;
    document.getElementById('logAerei').innerHTML = htmlLog || "Nessun aereo rilevato nel raggio selezionato";
    // la prima funzione returna testo semplice, 
    // mentre la seconde returna un pezzo di pagina in html che viene interpretato come tale
}

function crea_mappa() {
    L.tileLayer('http://localhost:8000/tiles/{z}/{x}/{y}', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);
}

function aggiorna_mappa() {
    for (const [nome_aereo, atributi_aereo] of Object.entries(storicoPosizioni)) {
        // Prende l'ultimo rilevamento: l'indice length - 1 è l'ultima posizione dell'array.
        const ultima_posizione = [atributi_aereo[atributi_aereo.length - 1].lat, atributi_aereo[atributi_aereo.length - 1].lon];

        const indice_inizio_linea = Math.max(0, atributi_aereo.length - OGNI_QUANTO_FARE_LINEA_SCIA_AEREI - 1);
        let posizione_precedente_linea = [atributi_aereo[indice_inizio_linea].lat, atributi_aereo[indice_inizio_linea].lon];

        if (aerei_disegnati[nome_aereo] == null) {

            // Primo rilevamento per questo aereo: crea il marker sulla mappa.
            aerei_disegnati[nome_aereo] = {
                marker: L.marker(ultima_posizione).addTo(map),
                linee: []
            };

            // vecchia versione
            /*aerei_disegnati[nome_aereo] = {
                marker: L.marker(ultima_posizione).addTo(map),
                linee: L.polyline(
                    [prima_posizione, ultima_posizione],
                    {color: 'red'}
                ).addTo(map),
            };*/

        } else {
            // Marker già esistente: aggiorna la sua posizione con le nuove coordinate.
            // Prima qui veniva passato l'intero oggetto ultima_posizione al posto di .lat,
            // formando una coppia errata e causando salti/spostamenti anomali del marker.
            aerei_disegnati[nome_aereo].marker.setLatLng(ultima_posizione);


            // aggiungo una nuova linea ogni 2/3 rivelazioni
            if (posizione_precedente_linea !== null && storicoPosizioni[nome_aereo].length % OGNI_QUANTO_FARE_LINEA_SCIA_AEREI === 0) {
                aerei_disegnati[nome_aereo].linee.push(L.polyline(
                    [posizione_precedente_linea, ultima_posizione],
                    { color: 'red' }
                ).addTo(map));
            }

            //vecchia versione
            //aerei_disegnati[nome_aereo].linea.setLatLngs([prima_posizione, ultima_posizione]);
        }
    }
}

function vettori_uguali(a, b) {
    if (a.length !== b.length) {
        return false;
    }

    for (let indice = 0; indice < a.length; indice++) {
        if (a[indice] !== b[indice]) {
            return false;
        }
    }

    return true;
}

// chiamata a una funzione javascript di una libreria standard gia scritta
// gli viene passata una funzione da eseguire in questo caso descritta con la sintassi: "() => { codice da eseguire }"
// e un intervallo in milisecondi da aspettare tra una essecuzione e un altra
// crea un cico infinito ripetuto ogni tot tempo
crea_mappa();
setInterval(() => {
    secondiMancanti--;  // ogni secondo toglie un secondo dal contatore 
    document.getElementById('timer').textContent = secondiMancanti; // aggiorna il contatore nella pagina html

    if (secondiMancanti <= 0) { // quando il contatore finisce
        secondiMancanti = INTERVALLO_AGGIORNAMENTO_SECONDI;   // viene ripristinato
        scaricaEAccumulaDati();
    }
}, 1000);

// Primo recupero immediato: non aspetta la fine del primo conto alla rovescia.
scaricaEAccumulaDati();
