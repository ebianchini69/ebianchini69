#!/bin/bash
# Installa il bot sul Mac.  Uso:  bash setup_mac.sh paper   (oppure: live)
# - copia il bot in ~/claude-trading
# - salva le chiavi Alpaca nel Portachiavi macOS (le incolli tu, non compaiono a schermo)
# - programma due esecuzioni automatiche nei giorni feriali (ora locale del Mac):
#     16:05  run     -> controlli + ribilanciamento mensile (mercato USA aperto dalle 15:30)
#     22:20  report  -> saldo di fine giornata, notifica e file in ~/claude-trading/reports
set -euo pipefail
ENV="${1:-paper}"
[[ "$ENV" == "paper" || "$ENV" == "live" ]] || { echo "Uso: bash setup_mac.sh paper|live"; exit 1; }

command -v python3 >/dev/null || { echo "Manca python3: eseguo xcode-select --install (conferma la finestra che appare)"; xcode-select --install; exit 1; }

DEST="$HOME/claude-trading"
mkdir -p "$DEST/reports"
cp "$(dirname "$0")/bot.py" "$DEST/bot.py"

for item in key-id secret; do
  svc="claude-trading-$ENV-$item"
  if security find-generic-password -s "$svc" >/dev/null 2>&1; then
    echo "Chiave $svc gia' presente nel Portachiavi."
  else
    label=$([[ $item == key-id ]] && echo "API Key ID" || echo "Secret Key")
    echo "Incolla la $label Alpaca ($ENV) e premi Invio (due volte per conferma):"
    security add-generic-password -U -a "$USER" -s "$svc" -w
  fi
done

PY="$(command -v python3)"
for job in run report; do
  label="com.claude-trading.$ENV.$job"
  plist="$HOME/Library/LaunchAgents/$label.plist"
  if [[ $job == run ]]; then H=16; M=5; else H=22; M=20; fi
  cal=""
  for d in 1 2 3 4 5; do cal+="<dict><key>Weekday</key><integer>$d</integer><key>Hour</key><integer>$H</integer><key>Minute</key><integer>$M</integer></dict>"; done
  cat > "$plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>$label</string>
  <key>ProgramArguments</key><array><string>$PY</string><string>$DEST/bot.py</string><string>$job</string></array>
  <key>EnvironmentVariables</key><dict><key>TRADING_ENV</key><string>$ENV</string></dict>
  <key>StartCalendarInterval</key><array>$cal</array>
  <key>StandardOutPath</key><string>$DEST/launchd-$ENV-$job.log</string>
  <key>StandardErrorPath</key><string>$DEST/launchd-$ENV-$job.log</string>
</dict></plist>
PLIST
  launchctl unload "$plist" 2>/dev/null || true
  launchctl load "$plist"
  echo "Programmato: $label alle $H:$(printf %02d $M) lun-ven"
done

echo "Prima esecuzione di prova:"
TRADING_ENV="$ENV" "$PY" "$DEST/bot.py" status
