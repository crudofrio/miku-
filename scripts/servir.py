#!/usr/bin/env python3
"""Sirve Miku en casa solo en la máquina local.

ChromeOS reenvía localhost al contenedor Linux si el proceso escucha en
0.0.0.0. Eso no abre el puerto a la red de la casa, salvo que actives el
reenvío de puertos en los ajustes de Linux.
"""

from __future__ import annotations

import argparse
import mimetypes
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

mimetypes.add_type("application/manifest+json", ".webmanifest")
mimetypes.add_type("text/javascript", ".js")
mimetypes.add_type("application/json", ".json")
mimetypes.add_type("application/octet-stream", ".moc3")
mimetypes.add_type("image/png", ".png")


class Manejador(SimpleHTTPRequestHandler):
    def list_directory(self, path):  # noqa: ANN001
        self.send_error(404, "Sin listado")
        return None

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-cache")
        self.send_header("X-Content-Type-Options", "nosniff")
        super().end_headers()

    def log_message(self, formato: str, *args) -> None:
        if args and str(args[1]) not in {"200", "304"}:
            super().log_message(formato, *args)


def main() -> None:
    parser = argparse.ArgumentParser(description="Sirve la compañera en localhost.")
    parser.add_argument("--dir", required=True, help="Carpeta de la app")
    parser.add_argument("--port", type=int, default=8741)
    parser.add_argument("--host", default="0.0.0.0")
    args = parser.parse_args()
    handler = partial(Manejador, directory=args.dir)
    servidor = ThreadingHTTPServer((args.host, args.port), handler)
    print(f"Miku en casa en http://localhost:{args.port}", flush=True)
    servidor.serve_forever()


if __name__ == "__main__":
    main()
