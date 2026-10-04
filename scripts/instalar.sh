#!/usr/bin/env bash
# Instalación / actualización de Miku en casa en un Chromebook (Linux / Crostini).
# Uso, una sola vez, en la Terminal de Linux:
#   curl -fsSL https://raw.githubusercontent.com/crudofrio/miku-/main/scripts/instalar.sh | bash
# - Baja el proyecto de GitHub (público, sin claves) a ~/mikuverse.
# - Instala la app en ~/.local/share/miku-en-casa, conservando el modelo si ya está.
# - Deja el servidor arrancando con Linux y el actualizador cada 3 h.
set -euo pipefail

DUENO="${MIKU_GITHUB:-crudofrio}"
REPO="${MIKU_REPO_NOMBRE:-miku-}"
RAMA="${MIKU_RAMA:-main}"
PROYECTO="${MIKU_PROYECTO:-$HOME/mikuverse}"
DEST="${MIKU_HOME:-$HOME/.local/share/miku-en-casa}"
export MIKU_PROYECTO="$PROYECTO" MIKU_HOME="$DEST" MIKU_RAMA="$RAMA"
export MIKU_REPO="https://github.com/$DUENO/$REPO"

echo "💙 Miku en casa: instalando desde github.com/$DUENO/$REPO ($RAMA)"

faltan=()
for h in curl tar unzip python3; do command -v "$h" >/dev/null || faltan+=("$h"); done
if [[ ${#faltan[@]} -gt 0 ]]; then
  echo "Instalo lo que falta: ${faltan[*]} (puede pedir la contraseña de Linux)"
  sudo apt-get update
  sudo apt-get install -y "${faltan[@]}" ca-certificates
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
curl -fsSL --retry 3 --retry-delay 3 \
  -o "$TMP/miku.tar.gz" "https://codeload.github.com/$DUENO/$REPO/tar.gz/refs/heads/$RAMA"
mkdir -p "$TMP/x"
tar -xzf "$TMP/miku.tar.gz" -C "$TMP/x"
ORIGEN="$(find "$TMP/x" -mindepth 1 -maxdepth 1 -type d | head -n 1)"
if [[ ! -f "$ORIGEN/app/index.html" || ! -f "$ORIGEN/scripts/setup-crostini.sh" ]]; then
  echo "La descarga no trae la app. No toqué nada." >&2
  exit 1
fi

# Proyecto en ~/mikuverse: se actualiza encima, sin borrar lo que ya tengas
# (si ahí guardaste live2d/ o cubism/, se quedan).
mkdir -p "$PROYECTO"
cp -a "$ORIGEN"/. "$PROYECTO"/
chmod +x "$PROYECTO"/scripts/*.sh

if [[ -f "$DEST/live2d/miku/miku.model3.json" && -f "$DEST/cubism/live2dcubismcore.min.js" ]]; then
  echo "El modelo Live2D ya está en este Chromebook. No lo vuelvo a bajar."
else
  echo "Todavía no hay modelo: lo bajo de live2d.com (uso personal, licencias en NOTICES.md)."
fi

# Copia la app (sin tocar live2d/ ni cubism/), baja el modelo solo si falta
# y deja el servidor en el puerto 8741.
bash "$PROYECTO/scripts/setup-crostini.sh"

# Fuente GitHub + temporizador (2 min tras arrancar y cada 3 h) + autoarranque.
bash "$PROYECTO/scripts/activar-actualizaciones.sh"

cat <<EOT

✅ Listo. Abre Chrome (el de ChromeOS) en http://localhost:8741
   Si ya la tenías instalada como app, ábrela normal: se pone al día sola.
EOT
