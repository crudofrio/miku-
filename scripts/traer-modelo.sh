#!/usr/bin/env bash
# Descarga el modelo gratuito de Hatsune Miku y Cubism Core 4 al directorio
# que se va a servir. No subas esa carpeta a un sitio público.
#
# Ejecutar este script implica que leíste y aceptas, para uso personal:
#   https://www.live2d.com/eula/live2d-free-material-license-agreement_en.html
#   https://www.live2d.com/eula/live2d-proprietary-software-license-agreement_en.html
#   https://www.live2d.com/eula/live2d-open-software-license-agreement_en.html
#   https://piapro.net/intl/en_for_creators.html
set -euo pipefail

DEST="${1:-public}"
FORZAR="${2:-}"
MODELO_URL="https://cubism.live2d.com/sample-data/bin/miku/miku_ja.zip"
SDK_URL="https://cubism.live2d.com/sdk-web/bin/CubismSdkForWeb-4-r.7.zip"

if [[ ! -d "$DEST" ]]; then
  echo "No existe el directorio de destino: $DEST" >&2
  exit 1
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

bajar() {
  local url="$1" salida="$2" local_zip="${3:-}"
  if [[ -n "$local_zip" && -f "$local_zip" ]]; then
    cp "$local_zip" "$salida"
    return
  fi
  curl -fL --retry 3 --retry-delay 2 -o "$salida" "$url"
}

if [[ ! -f "$DEST/live2d/miku/miku.model3.json" || "$FORZAR" == "--forzar" ]]; then
  echo "Descargando el modelo gratuito Hatsune Miku (solo miku_free/runtime)…"
  bajar "$MODELO_URL" "$TMP/miku.zip" "${MIKU_ZIP:-}"
  unzip -q "$TMP/miku.zip" -d "$TMP/miku"
  RUNTIME="$(find "$TMP/miku" -type d -path '*/miku_free/runtime' | head -n 1)"
  if [[ -z "$RUNTIME" || ! -f "$RUNTIME/miku.model3.json" ]]; then
    echo "El zip no trae miku_free/runtime/miku.model3.json" >&2
    exit 1
  fi
  rm -rf "$DEST/live2d/miku"
  mkdir -p "$DEST/live2d/miku"
  cp -a "$RUNTIME"/. "$DEST/live2d/miku/"
  # Los .cmo3/.can3 del editor no hacen falta y pesan mucho. El runtime no los incluye.
else
  echo "El modelo ya está en $DEST/live2d/miku (usa --forzar para bajarlo de nuevo)."
fi

if [[ ! -f "$DEST/cubism/live2dcubismcore.min.js" || "$FORZAR" == "--forzar" ]]; then
  echo "Descargando Cubism SDK for Web 4-r.7 y dejando solo Cubism Core…"
  bajar "$SDK_URL" "$TMP/sdk.zip" "${CORE_ZIP:-}"
  unzip -q "$TMP/sdk.zip" -d "$TMP/sdk"
  CORE="$(find "$TMP/sdk" -name live2dcubismcore.min.js -path '*/Core/*' | head -n 1)"
  if [[ -z "$CORE" ]]; then
    echo "No encontré live2dcubismcore.min.js en el SDK." >&2
    exit 1
  fi
  mkdir -p "$DEST/cubism"
  cp "$CORE" "$DEST/cubism/live2dcubismcore.min.js"
else
  echo "Cubism Core ya está en $DEST/cubism."
fi

python3 - "$DEST" <<'PY'
import json, os, sys
dest = sys.argv[1]
raiz = os.path.join(dest, "live2d", "miku")
archivos = []
for carpeta, _, nombres in os.walk(raiz):
    for nombre in nombres:
        if nombre == "files.json":
            continue
        full = os.path.join(carpeta, nombre)
        rel = os.path.relpath(full, dest).replace(os.sep, "/")
        archivos.append("/" + rel)
archivos.append("/cubism/live2dcubismcore.min.js")
salida = os.path.join(raiz, "files.json")
with open(salida, "w", encoding="utf-8") as fh:
    json.dump(sorted(archivos), fh, indent=2)
    fh.write("\n")
print(f"Lista de caché: {len(archivos)} archivos")
PY

echo "Modelo listo en $DEST (no lo publiques)."
