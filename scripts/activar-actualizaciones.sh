#!/usr/bin/env bash
# Un solo comando en la terminal de Linux del Chromebook.
# Deja:
#  - el servidor de Miku arrancando solo cuando arranca Linux (puerto 8741),
#  - un temporizador que revisa GitHub 2 min después de arrancar y cada 3 horas.
# El repo es público: no hace falta usuario, token ni clave.
set -euo pipefail

PORT="${PORT:-8741}"
DEST="${MIKU_HOME:-$HOME/.local/share/miku-en-casa}"
CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/miku-en-casa"
CONFIG="$CONFIG_DIR/fuente"
STATE="${XDG_STATE_HOME:-$HOME/.local/state}/miku-en-casa"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RAIZ="$(cd "$SCRIPT_DIR/.." && pwd)"
PROYECTO="${MIKU_PROYECTO:-$HOME/mikuverse}"
REPO="${MIKU_REPO:-https://github.com/crudofrio/miku-}"
UNIDADES="$HOME/.config/systemd/user"

faltan=()
for herramienta in curl tar python3; do
  command -v "$herramienta" >/dev/null || faltan+=("$herramienta")
done
if [[ ${#faltan[@]} -gt 0 ]]; then
  echo "Faltan ${faltan[*]}. Las instalo."
  sudo apt-get update
  sudo apt-get install -y "${faltan[@]}" ca-certificates
fi

if [[ ! -f "$PROYECTO/scripts/actualizar.sh" && -f "$RAIZ/scripts/actualizar.sh" ]]; then
  PROYECTO="$RAIZ"
fi

mkdir -p "$DEST" "$CONFIG_DIR" "$STATE" "$UNIDADES" "$HOME/.config/autostart"

if [[ ! -f "$DEST/index.html" ]]; then
  if [[ -f "$PROYECTO/app/index.html" ]]; then
    cp -a "$PROYECTO/app"/. "$DEST"/
  else
    echo "No hay app en $DEST ni en $PROYECTO/app. Corre primero: bash scripts/setup-crostini.sh" >&2
    exit 1
  fi
fi

cp "$SCRIPT_DIR/actualizar.sh" "$SCRIPT_DIR/aplicar_actualizacion.py" "$SCRIPT_DIR/servir.py" "$DEST/"
chmod 755 "$DEST/actualizar.sh" "$DEST/servir.py" "$DEST/aplicar_actualizacion.py"

# Fuente: GitHub público. Si había una config vieja (vacía, Origin o carpeta local), la migro.
actual=""
if [[ -f "$CONFIG" ]]; then
  actual="$(sed -n 's/^MIKU_REPO=//p' "$CONFIG" | tail -n 1)"
  cp "$CONFIG" "$CONFIG.antes-de-github" 2>/dev/null || true
fi
case "$actual" in
  https://github.com/*) REPO="$actual" ;;
esac
cat > "$CONFIG" <<EOT
# De dónde baja actualizaciones Miku en casa. Repo público: sin usuario ni token.
MIKU_REPO=$REPO
MIKU_RAMA=main
MIKU_PROYECTO=$PROYECTO
EOT
chmod 600 "$CONFIG"

cat > "$UNIDADES/miku-en-casa.service" <<EOT
[Unit]
Description=Miku en casa (servidor local en el puerto $PORT)
After=default.target

[Service]
ExecStart=/usr/bin/python3 $DEST/servir.py --port $PORT --dir $DEST
Restart=always
RestartSec=3

[Install]
WantedBy=default.target
EOT

cat > "$UNIDADES/miku-en-casa-actualizar.service" <<EOT
[Unit]
Description=Instalar actualización de Miku en casa desde GitHub
Wants=network-online.target
After=network-online.target

[Service]
Type=oneshot
ExecStart=/bin/bash $DEST/actualizar.sh
Nice=10
EOT

cat > "$UNIDADES/miku-en-casa-actualizar.timer" <<EOT
[Unit]
Description=Revisar si Miku en casa tiene versión nueva (2 min tras arrancar y cada 3 h)

[Timer]
OnStartupSec=2min
OnUnitActiveSec=3h
Persistent=true
AccuracySec=1min

[Install]
WantedBy=timers.target
EOT

# El .desktop viejo de autostart ya no hace falta: el timer cubre el arranque.
rm -f "$HOME/.config/autostart/miku-en-casa-actualizar.desktop"

if systemctl --user daemon-reload 2>/dev/null \
   && systemctl --user enable miku-en-casa.service miku-en-casa-actualizar.timer \
   && systemctl --user restart miku-en-casa.service \
   && systemctl --user start miku-en-casa-actualizar.timer; then
  echo "Servidor y temporizador activos: Miku arranca sola con Linux."
  loginctl enable-linger "$USER" 2>/dev/null || true
else
  echo "systemd --user no respondió. Dejo cron como respaldo."
  if [[ "${MIKU_SIN_CRON:-}" == "1" ]]; then
    echo "Sin crontab en esta corrida."
  elif command -v crontab >/dev/null; then
    (crontab -l 2>/dev/null | grep -v 'miku-en-casa' || true
     echo "@reboot /usr/bin/python3 $DEST/servir.py --port $PORT --dir $DEST >/tmp/miku-en-casa.log 2>&1"
     echo "@reboot sleep 120 && /bin/bash $DEST/actualizar.sh"
     echo "17 */3 * * * /bin/bash $DEST/actualizar.sh") | crontab -
  fi
  if [[ "${MIKU_SIN_SERVIDOR:-}" != "1" ]] && ! (ss -ltn 2>/dev/null | grep -q ":$PORT "); then
    nohup python3 "$DEST/servir.py" --port "$PORT" --dir "$DEST" >/tmp/miku-en-casa.log 2>&1 &
  fi
fi

echo "Primera revisión…"
bash "$DEST/actualizar.sh" || echo "La primera revisión no pudo bajar nada. La app que ya tenías sigue igual."

cat <<EOT

Listo. Miku baja sola lo nuevo de:
  $REPO
2 minutos después de que arranca Linux y cada 3 horas.
Cuando llega algo nuevo, la app muestra «Miku se actualizó 💙».

No hace falta volver a correr este comando.
EOT
