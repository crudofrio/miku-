#!/usr/bin/env bash
# Baja la última versión de Miku en casa desde GitHub (repo público, sin claves)
# y la instala. Si la descarga falla, no toca la app que ya corre.
# Nunca vuelve a bajar ni pisa el modelo Live2D ni Cubism Core.
set -euo pipefail

DEST="${MIKU_HOME:-$HOME/.local/share/miku-en-casa}"
CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}/miku-en-casa/fuente"
LOG="${XDG_STATE_HOME:-$HOME/.local/state}/miku-en-casa/actualizar.log"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_POR_DEFECTO="https://github.com/crudofrio/miku-"

mkdir -p "$(dirname "$LOG")"
log() { printf '%s %s\n' "$(date -Is)" "$*" | tee -a "$LOG" >&2; }

# Evita dos revisiones a la vez (timer + arranque).
exec 9>"$(dirname "$LOG")/actualizar.lock"
if command -v flock >/dev/null && ! flock -n 9; then
  log "Ya hay una revisión corriendo. Salgo."
  exit 0
fi

REPO_ENV="${MIKU_REPO-}"
RAMA_ENV="${MIKU_RAMA-}"
PROYECTO_ENV="${MIKU_PROYECTO-}"
MIKU_REPO=""
MIKU_RAMA=""
MIKU_PROYECTO=""

if [[ -f "$CONFIG" ]]; then
  # Solo claves conocidas. El archivo no puede redefinir PATH ni nada más.
  while IFS= read -r linea || [[ -n "$linea" ]]; do
    case "$linea" in
      MIKU_REPO=*|MIKU_RAMA=*|MIKU_PROYECTO=*)
        clave="${linea%%=*}"
        valor="${linea#*=}"
        printf -v "$clave" '%s' "$valor"
        ;;
    esac
  done < "$CONFIG"
fi

[[ -n "$REPO_ENV" ]] && MIKU_REPO="$REPO_ENV"
[[ -n "$RAMA_ENV" ]] && MIKU_RAMA="$RAMA_ENV"
[[ -n "$PROYECTO_ENV" ]] && MIKU_PROYECTO="$PROYECTO_ENV"
MIKU_REPO="${MIKU_REPO:-$REPO_POR_DEFECTO}"
MIKU_RAMA="${MIKU_RAMA:-main}"
MIKU_PROYECTO="${MIKU_PROYECTO:-$HOME/mikuverse}"

case "$MIKU_REPO" in
  *@*|*token*|*\?*)
    log "MIKU_REPO trae usuario o token en la URL. No lo uso. El repo es público: no hace falta."
    exit 1
    ;;
esac

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
ORIGEN=""

bajar_github() {
  # https://github.com/DUEÑO/REPO(.git) -> tarball público de codeload.
  local ruta dueno repo url
  ruta="${MIKU_REPO#https://github.com/}"
  ruta="${ruta%.git}"
  ruta="${ruta%/}"
  dueno="${ruta%%/*}"
  repo="${ruta#*/}"
  url="https://codeload.github.com/$dueno/$repo/tar.gz/refs/heads/$MIKU_RAMA"
  curl -fsSL --retry 3 --retry-delay 3 --max-time 300 -o "$TMP/miku.tar.gz" "$url" || return 1
  mkdir -p "$TMP/x"
  tar -xzf "$TMP/miku.tar.gz" -C "$TMP/x" || return 1
  ORIGEN="$(find "$TMP/x" -mindepth 1 -maxdepth 1 -type d | head -n 1)"
  [[ -n "$ORIGEN" && -f "$ORIGEN/app/index.html" ]] || return 1
  REVISION="$(gzip -dc "$TMP/miku.tar.gz" 2>/dev/null | git get-tar-commit-id 2>/dev/null | cut -c1-7 || true)"
}

bajar_git() {
  git clone --quiet --depth 1 --branch "$MIKU_RAMA" "$MIKU_REPO" "$TMP/x" || return 1
  ORIGEN="$TMP/x"
  REVISION="$(git -C "$ORIGEN" rev-parse --short HEAD)"
}

REVISION=""
if [[ -d "$MIKU_REPO" ]]; then
  ORIGEN="$MIKU_REPO"          # carpeta local (pruebas o sin internet)
  REVISION="carpeta local"
elif [[ "$MIKU_REPO" == https://github.com/* ]]; then
  if ! bajar_github; then
    log "No pude bajar $MIKU_REPO ($MIKU_RAMA). Sigue la versión que ya está instalada."
    exit 1
  fi
else
  export GIT_TERMINAL_PROMPT=0
  if ! bajar_git; then
    log "No pude clonar $MIKU_REPO. Sigue la versión que ya está instalada."
    exit 1
  fi
fi

# Por si alguien subió el modelo por error: no se copia nunca.
find "$ORIGEN" \( -name '*.moc3' -o -name 'live2dcubismcore*.js' \) -print 2>/dev/null | grep -q . && {
  log "El repo trae modelo o Cubism Core. No los copio (y habría que sacarlos del repo)."
  [[ "$ORIGEN" == "$TMP"* ]] && find "$ORIGEN" \( -name '*.moc3' -o -name 'live2dcubismcore*.js' \) -delete
}

APLICAR="$ORIGEN/scripts/aplicar_actualizacion.py"
[[ -f "$APLICAR" ]] || APLICAR="$SCRIPT_DIR/aplicar_actualizacion.py"
resultado="$(python3 "$APLICAR" --origen "$ORIGEN" --destino "$DEST")"

# Mantener ~/mikuverse al día (sin borrar nada que tengas ahí).
if [[ "$ORIGEN" == "$TMP"* ]]; then
  mkdir -p "$MIKU_PROYECTO"
  cp -a "$ORIGEN"/. "$MIKU_PROYECTO"/
fi

log "Revisión ${REVISION:-?} aplicada en $DEST ($resultado)"
