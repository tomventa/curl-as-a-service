# Curl-as-a-Service

## Project overview

Curl-as-a-Service e` un'applicazione web che permetta di creare richieste HTTP e di analizzare poi le
risposte, ricevendo informazioni anche sull'analisi dell'URL. Applicazione che salva tutte le
richieste e le relative risposte in un database i cui dati possono essere poi sfogliati attraverso una
pagina che prende nell'URL l'id della richiesta.

## Getting started

1) ### Install the required software
    Installa [Docker](https://docs.docker.com/get-docker/) e [Docker Compose](https://docs.docker.com/compose/install/), se non lo hai gia` fatto.
2) ### Navigate into the project directory
    ```bash
    cd digitiamo
    ```
3) ### Initialize the environment variables
    Copia il file .env.example in un nuovo file chiamato .env, e modifica le variabili di ambiente se necessario.
    ```bash
    cp .env.example .env
    ```

4) ### Edit the docker-compose.yml file
    Modifica il file `docker-compose.yml` per rimuovere mongo-express, un tool per visualizzare il database, se non ti serve o per non esporlo all'esterno.

5) ### Start the application
    ```bash
    docker compose up -d
    ```
    Questo comando avvia l'applicazione in background. Per visualizzare i log, esegui:
    ```bash
    docker compose logs -f
    ```
    Per fermare l'applicazione, esegui:
    ```bash
    docker compose down
    ```
    Per eseguire i test, esegui:
    ```bash
    docker exec -it digitiamo-server-1 python -m pytest -vv
    ```
    Per eseguire il report di coverage, esegui:
    ```bash
    docker exec -it digitiamo-server-1 python -m pytest --cov app --cov-report html:app/htmlcov
    python -m http.server -d app/htmlcov
    ```
    Successivamente apri il browser all'indirizzo http://localhost:8000 per visualizzare il report.

## Project architecture

Curl-as-a-Service fa affidamento su Docker e Docker Compose per l'ambiente di sviluppo e di produzione. Il progetto e` composto da 4 container:
- `digitiamo-server-1`: contiene il server FastAPI che si occupa degli endpoint API
- `digitiamo-mongo-1`: contiene il database MongoDB dove vengono salvate le richieste e le risposte
- `digitiamo-mongo-express-1`: contiene `mongo-express`, un tool per visualizzare il database
- `digitiamo-webserver-1`: contiene un webserver Nginx che si occupa di servire i file statici e di fare da reverse proxy al server FastAPI, nonche` di gestire il rate limiting degli endpoint delle API

## API documentation

La documentazione delle API e\` disponibile all'indirizzo http://localhost/docs e permette di testare le API direttamente dal browser. Alternativamente, e\` possibile utilizzare [Postman](https://www.postman.com/) o [Insomnia](https://insomnia.rest) per testare le API.
E\` disponibile il file `openapi.json` che contiene la documentazione delle API in formato JSON all'indirizzo http://localhost/openapi.json.

## Security

L'applicazione e\` protetta da un sistema di rate limiting che limita il numero di richieste che possono essere fatte in un certo intervallo di tempo. Il rate limiting e\` impostato a 100 richieste ogni 60 secondi per ogni indirizzo IP. Il rate limiting e\` gestito dal webserver Nginx.

Per evitare attacchi di tipo SSRF ([Server Side Request Forgery](https://owasp.org/www-community/attacks/Server_Side_Request_Forgery)) particolarmente dannosi nell'ambiente Cloud, l'applicazione verifica ad ogni step se un dominio punta ad un indirizzo IP privato, e in caso blocca la richiesta. 

La suite di test include test per i piu` comuni attacchi SSRF oltre a attacchi generici quali redirect infiniti.
Sviluppi futuri possono includere protezione da attacchi [DNS Rebinding](https://www.paloaltonetworks.com/cyberpedia/what-is-dns-rebinding) e [DNS Cache Poisoning](https://www.cloudflare.com/it-it/learning/dns/dns-cache-poisoning/).
