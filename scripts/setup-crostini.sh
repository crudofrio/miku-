#!/usr/bin/env bash
# Instala Miku en casa dentro de Linux (Crostini) en un Chromebook.
# Un solo comando, desde la carpeta del proyecto o del zip descomprimido.
set -euo pipefail

PORT="${PORT:-8741}"
DEST="${MIKU_HOME:-$HOME/.local/share/miku-en-casa}"
SIN_SERVICIO=0
FORZAR=""

for arg in "$@"; do
  case "$arg" in
    --no-servicio) SIN_SERVICIO=1 ;;
    --forzar) FORZAR="--forzar" ;;
    --destino)
      echo "Usa MIKU_HOME=/ruta para cambiar el destino." >&2
      exit 1
      ;;
    *)
      echo "Opción desconocida: $arg" >&2
      exit 1
      ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RAIZ="$(cd "$SCRIPT_DIR/.." && pwd)"

if [[ -d "$RAIZ/dist" && -f "$RAIZ/dist/index.html" ]]; then
  APP="$RAIZ/dist"
elif [[ -d "$RAIZ/app" && -f "$RAIZ/app/index.html" ]]; then
  APP="$RAIZ/app"
else
  echo "No encuentro la app compilada (dist/ o app/). En un clon del repo corre: npm install && npm run build" >&2
  exit 1
fi

if ! command -v curl >/dev/null || ! command -v unzip >/dev/null || ! command -v python3 >/dev/null; then
  echo "Instalando curl, unzip y python3…"
  sudo apt-get update
  sudo apt-get install -y curl unzip ca-certificates python3
fi

echo "Copiando la app a $DEST"
mkdir -p "$DEST"
rm -rf "$DEST/assets"
cp -a "$APP"/. "$DEST"/
cp "$SCRIPT_DIR/servir.py" "$SCRIPT_DIR/preparar_sprites.py" "$DEST/"
chmod +x "$DEST/servir.py" "$SCRIPT_DIR/traer-modelo.sh"

if [[ -d "$RAIZ/contenido" ]]; then
  mkdir -p "$DEST/contenido"
  cp -a "$RAIZ/contenido"/. "$DEST/contenido/"
fi
if [[ -d "$RAIZ/fuentes" ]]; then
  mkdir -p "$DEST/fuentes"
  cp -a "$RAIZ/fuentes"/. "$DEST/fuentes/"
fi

bash "$SCRIPT_DIR/traer-modelo.sh" "$DEST" $FORZAR

# Paquetes del día, banco de frases y accesorios en las rutas que sirve la app.
python3 "$SCRIPT_DIR/aplicar_actualizacion.py" --origen "$RAIZ" --destino "$DEST" >/dev/null

UNIDAD="$HOME/.config/systemd/user/miku-en-casa.service"
if [[ "$SIN_SERVICIO" == "1" ]]; then
  echo "Sin servicio. Para probar: python3 \"$DEST/servir.py\" --port $PORT --dir \"$DEST\""
  exit 0
fi

mkdir -p "$HOME/.config/systemd/user" "$HOME/.local/share/applications" "$HOME/.config/autostart"
cat > "$UNIDAD" <<EOF
[Unit]
Description=Miku en casa (compañera local)
After=default.target

[Service]
ExecStart=/usr/bin/python3 $DEST/servir.py --port $PORT --dir $DEST
Restart=on-failure
RestartSec=2

[Install]
WantedBy=default.target
EOF

cat > "$HOME/.local/share/applications/miku-en-casa.desktop" <<EOF
[Desktop Entry]
Name=Miku en casa
Comment=Abre la compañera en Chrome
Exec=xdg-open http://localhost:$PORT
Terminal=false
Type=Application
Categories=Utility;
Icon=$DEST/icons/icon-512.png
EOF

if systemctl --user daemon-reload && systemctl --user enable --now miku-en-casa.service; then
  echo "Servicio de usuario activo."
  loginctl enable-linger "$USER" 2>/dev/null || true
else
  echo "systemd no quedó disponible. La dejo para que arranque con Linux."
  cat > "$HOME/.config/autostart/miku-en-casa-servidor.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Servidor Miku en casa
Exec=/usr/bin/python3 $DEST/servir.py --port $PORT --dir $DEST
X-GNOME-Autostart-enabled=true
Terminal=false
EOF
  if ! ss -ltn 2>/dev/null | grep -q ":$PORT "; then
    nohup python3 "$DEST/servir.py" --port "$PORT" --dir "$DEST" >/tmp/miku-en-casa.log 2>&1 &
  fi
fi

cat <<EOF

Listo.

1. Abre Chrome, el de ChromeOS, no el navegador de Linux.
2. Entra a http://localhost:$PORT
3. Espera a que en Ajustes diga «Lista sin Linux».
4. Menú de Chrome → Instalar página como aplicación
   (o el icono de instalar en la barra de direcciones).
5. Abre «Miku en casa» desde el lanzador. Ya puede quedarse
   aunque apagues Linux, porque Chrome guardó la copia.

Modo fiesta, para una automatización con Linux encendido:
  http://localhost:$PORT/?modo=fiesta

No actives el reenvío de ese puerto hacia la red de la casa.
El modelo se queda en este Chromebook.

Para que el contenido y el código lleguen solos, una sola vez:
  bash scripts/activar-actualizaciones.sh

EOF
