# Importa i moduli necessari:
# os e json: servono per lavorare con file e dati JSON.
# ssl: gestisce le connessioni HTTPS e i certificati.
# gzip: decomprime i dati compressi in gzip.
# getpass: legge la password senza mostrarla a video.
# urllib.request e urllib.error: permettono di fare richieste HTTP/HTTPS e gestire errori.
# HTTPServer e SimpleHTTPRequestHandler: permettono di creare un server web locale.
import os
import json
import ssl
import gzip
import getpass
import urllib.request
import urllib.error
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlsplit   # libreria usata per separare l'url

#                           COSTANTI

# Porta locale su cui il server ascolta.
PORT_LOCALE_AEREI_API = 8000
# URL dell'API remota da cui si ricevono i dati degli aerei.
API_URL_STANDARD = "https://api.adsb.lol/v2/lat/43.726/lon/12.636/dist/50"
TILES_URL = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"



#                           FUNZIONI

# funzione per impostare una zona e distanza da input
def configura_url_api():
    lat = float(input("latutudine(Urbino = 43.726):"))
    lon = float(input("longitudine(Urbino = 12.636):"))
    dist = float(input("distanza in km:"))

    dist = dist / 1.852

    return f"https://api.adsb.lol/v2/lat/{lat}/lon/{lon}/dist/{dist}"

# Questa funzione chiede all'utente quale tipo di connessione usare:
# - se è in scuola, imposta il proxy aziendale con username e password
# - se è a casa, usa direttamente Internet senza proxy
# Serve quindi a preparare il contesto di rete prima di fare richieste esterne.
def configura_ambiente_rete():
    # Stampa il menu iniziale.
    print("=" * 65)
    print("   FLIGHT SCANNER - CONFIGURAZIONE RETE (LOCAL PROXY SERVER)")
    print("=" * 65)
    print("1. Uso a Scuola (richiede Proxy di rete con autenticazione)")
    print("2. Uso a Casa (connessione diretta a Internet)")
    print("-" * 65)
    
    # Legge la scelta dell'utente.
    scelta = input("Seleziona la modalita' [1/2] (default 1): ").strip()
    
    # Se l'utente sceglie "casa", termina la configurazione.
    if scelta == "2":
        print("\n[OK] Modalita' CASA selezionata: connessione diretta.")
        return

    # Se non è casa, si prepara la configurazione del proxy scolastico.
    print("\n--- Configurazione Proxy Scolastico ---")
    host_default = "10.0.0.1"
    porta_default = "800"
    
    # Richiede IP e porta del proxy, usando i valori di default se l'utente lascia vuoto.
    ip_proxy = input(f"Indirizzo IP Proxy [{host_default}]: ").strip() or host_default
    porta_proxy = input(f"Porta Proxy [{porta_default}]: ").strip() or porta_default
    
    # Richiede username e password per autenticarsi al proxy.
    utente = input("Nome utente proxy (es. mario.rossi): ").strip()
    password = getpass.getpass("Password proxy (i caratteri non verranno mostrati): ").strip()

    # Costruisce la stringa del proxy con le credenziali.
    proxy_url = f"http://{utente}:{password}@{ip_proxy}:{porta_proxy}"

    # Crea il gestore dei proxy per HTTP e HTTPS.
    proxy_handler = urllib.request.ProxyHandler({
        'http': proxy_url,
        'https': proxy_url
    })
    
    # Crea un gestore per autenticazione HTTP Basic del proxy.
    password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(None, f"http://{ip_proxy}:{porta_proxy}", utente, password)
    auth_handler = urllib.request.ProxyBasicAuthHandler(password_mgr)
    
    # Gestore SSL senza verifica certificato.
    https_handler = urllib.request.HTTPSHandler(context=ssl_context)

    # Unisce tutti i gestori in un unico opener.
    opener = urllib.request.build_opener(proxy_handler, auth_handler, https_handler)
    urllib.request.install_opener(opener)
    
    # Messaggio di conferma.
    print(f"\n[OK] Proxy scolastico impostato su http://{ip_proxy}:{porta_proxy}")


# Crea un contesto SSL personalizzato:
# disabilita il controllo del nome host e la verifica del certificato.
# Serve per evitare problemi con certificati non validi o con proxy scolastici.
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


# Questa classe gestisce tutte le richieste HTTP ricevute dal browser o dal client.
# Estende SimpleHTTPRequestHandler, cioè il server HTTP base di Python.
# e un server http
class CustomProxyHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.dirname(os.path.abspath(__file__)), **kwargs)

    # Override del metodo che gestisce le richieste GET.
    def do_GET(self):
        # Se la richiesta è una delle URL speciali usate per le chiamate API,
        # il server non serve file statici ma recupera i dati dall'API esterna.
        if self.path in ["/api", "/proxy.py", "/proxy.php"]:
            try:
                # Header simulati da browser per far sembrare una richiesta normale.
                headers = {
                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'application/json',
                    'Accept-Encoding': 'gzip, deflate'
                }
                
                # Crea la richiesta all'API remota.
                req = urllib.request.Request(API_URL, headers=headers)
                
                # Esegue la richiesta inviandola effettivamente, con timeout e con il contesto SSL personalizzato(che disattiva protocollo SSL)
                with urllib.request.urlopen(req, timeout=10) as response:
                    # Legge i dati ricevuti.
                    data = response.read()
                    
                    # Se la risposta è compressa in gzip, la decomprime.
                    if response.info().get('Content-Encoding') == 'gzip':
                        data = gzip.decompress(data)
                    
                    # Invia una risposta HTTP 200 con contenuto JSON.
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(data)
                    
            # Se il server remoto risponde con un codice HTTP di errore.
            except urllib.error.HTTPError as e:
                print(f"\n[ERRORE HTTP REMOTO] Codice {e.code}: {e.reason}")
                self.send_response(e.code)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                msg = json.dumps({"error": f"Errore HTTP {e.code}. Verificare credenziali proxy."}).encode('utf-8')
                self.wfile.write(msg)

            # Se si verifica un qualsiasi altro errore di connessione o di rete.
            except Exception as e:
                print(f"\n[ERRORE CONNETTIVITA'] Dettaglio: {type(e).__name__} - {e}")
                self.send_response(500)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                msg = json.dumps({"error": f"Impossibile raggiungere l'API: {str(e)}"}).encode('utf-8')
                self.wfile.write(msg)
        
        # condizione che controlla l'inizio del path richiesto e ritorna true se inizia con /tiles/ 
        elif urlsplit(self.path).path.startswith("/tiles/"):
            # gestione delle richieste delle tiles per creare la mappa
            headers = {
                                'User-Agent': 'Flight Scanner (https://github.com/lo-zaffo/flight-scanner-finale)',
                            }
            # dobbiamo mettere le variabili x y z nell'url della richiesta

            # urlsplit è una funzione che divide self.path che contiene tutto l'indirizzo dopo l'indirizzo ip e la porta
            # .path.strip("/") è una opsione che toglie / iniziali e finalli 
            # split è una opsione che trasforma la tringa che verrebbe altrimenti retornata con un vettore contenente i vari elementi divisi da i / 
            # in totale pezzi diventa un vettore di stringe
            pezzi = urlsplit(self.path).path.strip("/").split("/")

            ''' ciclo per vedere le vare tiles
            for i in range (len (pezzi)):
                print(pezzi[i])
            '''

            url_tiles = TILES_URL.format(z=pezzi[1], x=pezzi[2], y=pezzi[3])

            req = urllib.request.Request(url_tiles, headers=headers)

            with urllib.request.urlopen(req, timeout=10) as response:
                # Legge i dati ricevuti.
                data = response.read()
                                
                #le immagini non sono zippate quindi non le decomprimiamo
                                
                # Invia una risposta HTTP 200 con contenuto JSON.
                self.send_response(200)
                self.send_header('Content-Type', 'img/png')
                self.send_header('Access-Control-Allow-Origin', '*')
                # questa riga fa inserire nella cache del brouser l'immagine, salvandola per 7 giorni, è un requisito per usare l'api di openstreetmap
                self.send_header('Cache-Control', 'public, max-age=604800')
                self.end_headers()
                self.wfile.write(data)


        else:
            # Per tutte le altre richieste, usa il comportamento standard del server HTTP
            # cioè serve file statici come HTML, CSS, immagini ecc.
            super().do_GET()


#                           MAIN


if __name__ == "__main__":
    print("vuoi cambiare la zona di verifica?")
    scelta = int(input("1 = si, 2 = no : "))
    if scelta == 1:
        API_URL = configura_url_api()
    else:
        API_URL = API_URL_STANDARD
    # Configura la rete prima di avviare il server.
    
    configura_ambiente_rete()
    try:
        # Crea il server locale sulla porta 8000, usando la classe CustomProxyHandler.
        server_aerei = HTTPServer(('0.0.0.0', PORT_LOCALE_AEREI_API), CustomProxyHandler)
        print(f"\nServer attivo! Apri nel browser: http://localhost:{PORT_LOCALE_AEREI_API}")
        print("Premi CTRL+C nel terminale per interrompere.\n")
        # Rimane in ascolto finché non si interrompe manualmente.
        server_aerei.serve_forever()
    except KeyboardInterrupt:
        # Se l'utente preme CTRL+C, il server viene arrestato.
        print("\nServer arrestato.")
