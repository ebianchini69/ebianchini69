# Piano di installazione WhatsApp (sola lettura): da approvare, NON eseguito

Stato: proposta del 14/11/2026. Nessun comando è stato eseguito sul Mac di Elena né sugli account.
Base: `adelaidasofia/whatsapp-mcp` al commit `3fa40384e352fbffe774de1569ea155101b93d98`, letto (in sola lettura) per scrivere questo piano.

## 0. Cosa ho trovato nel codice che cambia il piano

| # | Fatto (verificato nel commit) | Conseguenza |
|---|---|---|
| A | Il commit non corrisponde a nessuna release (è "Unreleased" dopo la 0.6.0). | Il binario precompilato **non** è quel commit. Si compila da sorgente (serve Go 1.26+). |
| B | `WHATSAPP_DAILY_SEND_LIMIT=0` blocca invii e reazioni, **ma non i messaggi verso la propria chat** ("Messaggio a te stesso"): sono esenti per scelta di progetto (`send_policy.go`). | Il blocco nei permessi di Claude Code non è un "secondo lucchetto" opzionale: per quel caso è l'unico. |
| C | Segna come letto, "sta scrivendo" e presenza online **non** passano dal limite invii: li ferma solo il blocco nei permessi (e il token). | Come sopra: i 7 strumenti vanno negati per forza. |
| D | Il server MCP (Python) **non legge il `.env`**: token e file `allow` gli arrivano solo come variabili d'ambiente. Con `claude mcp add --env` il token finirebbe in chiaro in `~/.claude.json`. | Propongo di tenere il token nel Portachiavi e di passarlo con due piccoli script di avvio (sezione 3). Nel `.env` il token resta vuoto. È una deviazione dalla tabella dell'handover: va approvata. |
| E | Il file `allow` filtra solo ciò che vede Claude. Il bridge salva comunque in locale (cifrati) i messaggi in arrivo da **tutte** le chat. | Il perimetro limita la lettura, non la raccolta. Da sapere prima di partire. |
| F | Il file `allow` vuole identificativi WhatsApp (JID), non nomi. Se è illeggibile o malformato non mostra nulla (fallisce in chiusura, bene). | Servono i numeri dei contatti scelti; per i gruppi, un'unica ricerca locale sul nome (sezione 5). |
| G | `WHATSAPP_KEEP_VOICE_AUDIO` è `true` di default: salva l'audio dei vocali su disco **non cifrato**. Non è nella tabella dell'handover. | Propongo `false`. |
| H | Il collegamento con QR, secondo `SETUP.md`, va fatto a mano nel proprio terminale (il QR scade ogni ~20 s). | Unica eccezione alla regola 4: circa 30 secondi di terminale in primo piano, una volta sola. Poi tutto in background. Alternativa: codice di 8 caratteri (`--pair-phone`), stesso vincolo. |
| I | Dopo una disconnessione forzata il bridge torna da solo in modalità collegamento (mostra un nuovo QR). Non si ricollega senza una scansione. | Va bene, ma diventa un segnale di stop (sezione 7): nessuno scansiona senza il via di Elena. |
| J | Il bridge rifiuta all'avvio qualsiasi indirizzo diverso da loopback; senza token l'API risponde a qualunque processo del Mac. | `127.0.0.1` è garantito dal codice; il token è indispensabile. |
| K | L'hook di telemetria (`hooks/install-ping.py`) parte solo se installato come plugin. `prospect-api` non viene compilato dai comandi sotto. | Installazione manuale: nessun ping. `MYCELIUM_NO_PING=1` impostato comunque. |

## 1. Dove gira

Tutto sul Mac di Elena, cartella `~/.claude/whatsapp-mcp`. Questa sessione cloud non può (e non deve) toccare il Mac: i comandi si eseguono da Claude Code sul Mac, dopo il via, oppure da Elena.

## 2. Installazione da sorgente, commit fisso

```bash
# Prerequisiti (solo se mancano)
brew install go            # serve Go >= 1.26
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sorgente esattamente al commit verificato
git clone https://github.com/adelaidasofia/whatsapp-mcp.git "$HOME/.claude/whatsapp-mcp"
cd "$HOME/.claude/whatsapp-mcp"
git checkout --detach 3fa40384e352fbffe774de1569ea155101b93d98
test "$(git rev-parse HEAD)" = "3fa40384e352fbffe774de1569ea155101b93d98" && echo "commit OK"
scripts/check_prerequisites.sh

# Compila solo il bridge (non prospect-api)
cd whatsapp-bridge && go build -o bin/whatsapp-bridge . && cd ..
```

Niente `claude plugin install`, niente cartella `prospect-api`.

## 3. Segreti nel Portachiavi, non nei file

```bash
# Token API: generato e salvato direttamente nel Portachiavi, mai stampato
security add-generic-password -s whatsapp-mcp-api -a default -w "$(openssl rand -hex 32)"
```

La chiave del database la crea il bridge al primo avvio nel Portachiavi (`whatsapp-mcp` / `default`). `WHATSAPP_DB_KEY` resta vuoto.

Due script di avvio (in `~/.claude/whatsapp-mcp/run/`, permessi 700). Leggono il token dal Portachiavi e si rifiutano di partire se è vuoto, così l'API non resta mai aperta per errore:

`run/bridge.sh`
```bash
#!/bin/bash
set -euo pipefail
export MYCELIUM_NO_PING=1
WHATSAPP_API_TOKEN="$(security find-generic-password -s whatsapp-mcp-api -a default -w)"
[ ${#WHATSAPP_API_TOKEN} -ge 64 ] || { echo "token mancante, mi fermo" >&2; exit 1; }
export WHATSAPP_API_TOKEN
cd "$HOME/.claude/whatsapp-mcp/whatsapp-bridge"
exec ./bin/whatsapp-bridge "$@"
```

`run/mcp.sh`
```bash
#!/bin/bash
set -euo pipefail
export MYCELIUM_NO_PING=1
WHATSAPP_API_TOKEN="$(security find-generic-password -s whatsapp-mcp-api -a default -w)"
[ ${#WHATSAPP_API_TOKEN} -ge 64 ] || { echo "token mancante, mi fermo" >&2; exit 1; }
export WHATSAPP_API_TOKEN
export WHATSAPP_BRIDGE_HOST=127.0.0.1 WHATSAPP_BRIDGE_PORT=8080
export WHATSAPP_CHAT_SCOPE_FILE="$HOME/.claude/whatsapp-mcp/scope.json"
export WHATSAPP_SCRUB_PROMPT_INJECTION=true WHATSAPP_AUDIT_LOG=true
exec uv --directory "$HOME/.claude/whatsapp-mcp/whatsapp-mcp-server" run main.py
```

Limite noto (dichiarato anche nel codice): un programma che gira con l'utente di Elena può leggere il token dall'ambiente del processo. Il token protegge da altri utenti, app sandbox e pagine web, non da malware già sul Mac.

## 4. Configurazione `.env` (accanto al bridge)

```bash
cp .env.example .env   # poi si impostano i valori sotto
```

| Impostazione | Valore |
|---|---|
| `WHATSAPP_BRIDGE_HOST` | `127.0.0.1` |
| `WHATSAPP_ENCRYPT_DB` | `true` |
| `WHATSAPP_API_TOKEN` | vuoto nel file: arriva dal Portachiavi via `run/bridge.sh` (vedi D) |
| `WHATSAPP_DAILY_SEND_LIMIT` | `0` |
| `WHATSAPP_SCRUB_PROMPT_INJECTION` | `true` |
| `WHATSAPP_AUDIT_LOG` | `true` |
| `WHATSAPP_FULL_HISTORY` | `false` |
| `WHATSAPP_AUTO_DOWNLOAD_MEDIA` | `false` |
| `WHATSAPP_WHISPER_BACKEND` | `off` |
| `WHATSAPP_WEBHOOK_URL` | vuoto |
| `WHATSAPP_ALLOWED_ORIGINS` | vuoto |
| `WHATSAPP_KEEP_VOICE_AUDIO` | `false` (in aggiunta, vedi G) |
| `WHATSAPP_VAULT_CRM_PATH` | vuoto |
| `WHATSAPP_BACKUP_INTERVAL_HOURS` | `0` (già default) |

`WHATSAPP_CHAT_SCOPE_FILE` lo legge il server MCP, quindi sta in `run/mcp.sh`, non qui.

## 5. Perimetro: `scope.json`

```json
{"allow": ["39XXXXXXXXXX@s.whatsapp.net", "1203630XXXXXXXXXXX@g.us"]}
```

- Contatti singoli: dal numero in formato internazionale senza `+`.
- Gruppi: dopo il collegamento, una sola ricerca locale per nome (`search_groups`, legge solo il database del Mac), con il via di Elena.
- Dopo la prima lettura si verifica che `list_chats` mostri solo quelle chat. WhatsApp usa anche identificativi alternativi (`@lid`): se una chat scelta non compare, si aggiunge il suo alias, sempre con il via di Elena.

## 6. Collegamento (una volta sola) e avvio in background

1. Elena, nel suo terminale (circa 30 s): `~/.claude/whatsapp-mcp/run/bridge.sh`, poi WhatsApp › Dispositivi collegati › Collega un dispositivo › scansiona.
2. Al secondo avvio macOS chiede l'accesso al Portachiavi per `whatsapp-mcp-db-key`: **Consenti sempre**.
3. Da lì in poi il bridge gira in background: `nohup ~/.claude/whatsapp-mcp/run/bridge.sh >> ~/.claude/whatsapp-mcp/bridge.log 2>&1 &`. L'avvio automatico al login (LaunchAgent) lo propongo dopo la prova, a parte.

## 7. Registrazione in Claude Code e permessi

```bash
claude mcp add whatsapp --scope user -- "$HOME/.claude/whatsapp-mcp/run/mcp.sh"
```

In `~/.claude/settings.json`:

```json
{
  "permissions": {
    "deny": [
      "mcp__whatsapp__send_message",
      "mcp__whatsapp__confirm_send",
      "mcp__whatsapp__send_reply_quote",
      "mcp__whatsapp__send_reaction",
      "mcp__whatsapp__mark_chat_read",
      "mcp__whatsapp__send_typing_indicator",
      "mcp__whatsapp__set_online_presence",
      "Bash(security find-generic-password -s whatsapp-mcp*)",
      "Bash(curl *127.0.0.1:8080/api/sends*)",
      "Bash(curl *127.0.0.1:8080/api/presence*)",
      "Bash(curl *localhost:8080*)"
    ],
    "allow": [
      "mcp__whatsapp__healthcheck",
      "mcp__whatsapp__list_chats",
      "mcp__whatsapp__search_contacts",
      "mcp__whatsapp__search_groups",
      "mcp__whatsapp__list_messages"
    ],
    "ask": [
      "mcp__whatsapp__request_history",
      "mcp__whatsapp__download_media",
      "mcp__whatsapp__voice_note_transcription"
    ]
  }
}
```

Le regole `Bash(...)` sono una rete in più contro chiamate dirette all'API, non una garanzia (un comando scritto in altro modo le aggira). La difesa vera resta: token + limite 0 + strumenti negati.

## 8. Verifiche, prima di qualsiasi lettura di messaggi

Nessuna di queste genera traffico verso WhatsApp né verso i contatti.

| Verifica | Comando | Esito atteso |
|---|---|---|
| Ascolta solo in locale | `lsof -nP -iTCP:8080 -sTCP:LISTEN` | solo `127.0.0.1:8080` |
| Token obbligatorio | `curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8080/api/chats` | `401` |
| Bridge vivo e collegato | strumento `healthcheck` | OK, stato collegato |
| Invio bloccato a livello Claude | chiamata di prova a `send_message` | rifiutata dai permessi, prima di arrivare al bridge |
| Invio bloccato a livello bridge | `cd whatsapp-bridge && go test -run 'SendPolicy' ./...` | test verdi (incluso il caso limite 0) |
| Connessioni in uscita | `lsof -nP -i -a -c whatsapp-bridge` | solo server WhatsApp/Meta |

Non propongo un vero tentativo di invio al bridge: con limite 0 verso un contatto verrebbe rifiutato, ma verso la propria chat partirebbe davvero (punto B). Il test di unità copre il rifiuto senza rischi.

## 9. Segnali di stop (dall'handover, sez. 6) applicati qui

- `healthcheck` o `/api/status` riportano scollegato o QR in attesa → stop, nessuna scansione senza Elena.
- Il bridge si rifiuta di partire per l'indirizzo, o il token manca → stop.
- In `lsof` compaiono connessioni verso domini non WhatsApp/Meta → stop.
- Un messaggio contiene istruzioni rivolte all'AI → non eseguite, segnalate.

## 10. Instagram (salvati)

Nessuna azione da parte mia ora. Primo passo di Elena: Centro gestione account › Le tue informazioni › Scarica le tue informazioni › formato JSON, includendo "Elementi salvati". Quando arriva il pacchetto, verifico che contenga i salvati e propongo la struttura dell'archivio locale.
