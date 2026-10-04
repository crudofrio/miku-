# Miku en casa

> Novedades: mira el [Recopilatorio (CHANGELOG.md)](CHANGELOG.md).

Compañera de escritorio para un Chromebook en el stand: Hatsune Miku en Live2D o en los dibujos de Mikuverse, con fondos, voz en español y un modo fiesta. Sin anuncios, sin analíticas y sin red en el día a día. Después de instalarla, Chrome la abre aunque Linux esté apagado.

Pensada para el ASUS Chromebook Detachable CM3 (pantalla 10.5" en horizontal, poco RAM). El modelo va a 30 fps y a resolución 1 para no calentar el MediaTek.

## Instalar en el Chromebook

1. Activa Linux: Ajustes → Avanzado → Desarrolladores → Linux → Activar.
2. Abre la Terminal de Linux y pega **una sola vez**:

```bash
curl -fsSL https://raw.githubusercontent.com/crudofrio/miku-/main/scripts/instalar.sh | bash
```

Eso baja el proyecto a `~/mikuverse`, instala la app en `~/.local/share/miku-en-casa` (si el modelo ya estaba, no lo vuelve a bajar), deja el servidor del puerto **8741** arrancando solo con Linux y activa el actualizador. Puede pedir la contraseña de Linux si faltan `curl`, `tar`, `unzip` o `python3`. Sirve igual para instalar de cero o para pasar una instalación vieja a GitHub.

3. Abre **Chrome de ChromeOS** (no el navegador que vive dentro de Linux) en [http://localhost:8741](http://localhost:8741).
4. Entra a Ajustes y espera el texto **Lista sin Linux**.
5. Menú de Chrome → **Instalar página como aplicación**. Ábrela desde el lanzador.

Instalación manual (sin internet, desde una copia de la carpeta): `bash scripts/setup-crostini.sh && bash scripts/activar-actualizaciones.sh`.

`localhost` es un contexto seguro: por eso se puede instalar como PWA, usar el service worker y el bloqueo de pantalla. ChromeOS reenvía ese puerto al contenedor. No actives el reenvío del puerto hacia la red de tu casa.

También aparece un acceso de Linux llamado «Miku en casa» que abre la misma dirección. Ese icono solo funciona con Linux encendido. La aplicación instalada de Chrome es la que sigue cuando apagas Linux.

### Modo fiesta

Con el servidor encendido, una automatización puede abrir:

```text
http://localhost:8741/?modo=fiesta
```

Hay bailes o rebotes y un fondo de palitos de luz, sin destellos blancos. Otros atajos de una sola visita: `?modo=live2d`, `?modo=mikuverse`, `?fondo=concierto`, `?variante=colombiana`, `?mudo=1`. No cambian lo que guardaste, salvo que después muevas un ajuste.

Si Linux está apagado, la app instalada abre desde la caché de Chrome. Una automatización que pega la URL necesita el servidor, así que para la fiesta deja Linux encendido.

## Qué hace

- **Live2D.** El sample gratuito, con física, respiración, parpadeo, un idle en bucle y la mirada siguiendo el dedo o el cursor. Un toque lanza un movimiento al azar y una frase.
- **Mikuverse.** Diez variantes. El fondo blanco se quita al preparar los PNG. Flotan, se achican al tocarlas y hablan con su propia frase. Rotan al azar; si «Respetar temporada» está activo, en octubre pesa más la bruja, de noche la de neón, en marzo–mayo Sakura, en vacaciones (junio, julio, diciembre y enero) la sirena, y en julio y diciembre la parcera.
- **Fondos.** Cinco wallpapers, fijos o en rotación.
- **Accesorios en Live2D.** Sombrero de bruja y vueltiao según la variante, y el de bruja todo octubre. Ver «Accesorios por variante».
- **Voz.** Cada cierto rato (de 10 a 40 minutos, configurable) dice una frase en español con `speechSynthesis`, buscando voz `es-CO` y si no hay, otra de español. Hay silencio y volumen. El toque también habla, si no está en silencio.
- **Compañera.** Pantalla completa, Wake Lock para que el stand no se duerma, y un panel corto de ajustes.
- **Sin red al usarla.** El service worker guarda la app. El modelo se copia a la caché la primera vez que carga con Linux encendido.

En el CM3 puedes bajar a 20 fps desde Ajustes si la tablet se calienta. Al pasar a Mikuverse se descarga el modelo de la memoria.

## Añadir una variante

1. Suelta el PNG (puede traer fondo blanco) en `fuentes/sprites/` con un nombre nuevo, por ejemplo `11-lluvia.png`.
2. Agrega una entrada en `contenido/mikuverse.json` con `id`, `nombre`, `archivo` (`sprites/11-lluvia.png`), `estilo`, `temporada` y `frases` (dos textos).
3. Prepara y vuelve a construir:

```bash
python3 scripts/preparar_sprites.py
npm run build
./scripts/setup-crostini.sh
```

En el Chromebook, si ya está instalada y no quieres Node, copia el PNG a `~/.local/share/miku-en-casa/fuentes/sprites/`, edita el JSON de `contenido/` y corre:

```bash
sudo apt-get install -y python3-pil python3-numpy
python3 ~/.local/share/miku-en-casa/preparar_sprites.py --raiz ~/.local/share/miku-en-casa --destino ~/.local/share/miku-en-casa
```

Recarga con Linux encendido para que el service worker guarde el dibujo nuevo. Temporadas que entiende el texto: `todo el año`, `noche`, `octubre`, `marzo-mayo`, `julio y diciembre`, `vacaciones`, o un mes suelto.

## Paquete del día

Cada día cabe en un solo archivo. No hace falta tocar el código. La app lee todos los que haya y mezcla las frases con las de siempre y con las de cada variante.

Crea `contenido/dias/AAAA-MM-DD.json` (la fecha del día, con ceros). Ejemplo real: `contenido/dias/2026-09-25.json`.

```json
{
  "fecha": "2026-09-26",
  "titulo": "Sábado corto",
  "frases": [
    "Frase general, en español, con humor de por acá."
  ],
  "por_variante": {
    "colombiana": ["Frase solo cuando está la parcera."],
    "pixel": ["Frase solo de la pixel."]
  },
  "fondos": [
    { "id": "lluvia", "nombre": "Lluvia", "archivo": "dias/2026-09-26/lluvia.png" }
  ],
  "variantes": [
    {
      "id": "lluvia",
      "nombre": "Miku Lluvia",
      "archivo": "dias/2026-09-26/miku.png",
      "estilo": "lluvia",
      "temporada": "todo el año",
      "frases": ["Una frase.", "Otra."]
    }
  ]
}
```

- `fecha` tiene que coincidir con el nombre del archivo.
- `frases` son líneas sueltas. `por_variante` usa el `id` que ya está en `contenido/mikuverse.json` (`pixel`, `chibi`, `samurai`, `cyberpunk`, `bruja`, `sakura`, `carreras`, `sirena`, `astronauta`, `colombiana`).
- `fondos` y `variantes` son opcionales. Si los usas, el PNG va al lado, en `contenido/dias/2026-09-26/lluvia.png`. La ruta del JSON es `dias/2026-09-26/lluvia.png`, sin `..` y sin barra al inicio. Los sprites nuevos conviene dejarlos ya con fondo transparente.
- No edites `manifiesto.json`. Lo arma el actualizador al instalar.

Con solo ese archivo, el temporizador del Chromebook lo copia. No hace falta `npm run build`. Si cambias código de la app, sí: `npm run build` refresca la carpeta `app/` (sin el modelo) y ese cambio también viaja en el siguiente ciclo.

## Accesorios por variante (modo Live2D)

Cuando eliges una variante de Mikuverse y estás en modo Live2D, Miku se pone el accesorio de esa variante: un PNG transparente pegado a su cabeza que sigue la posición de la cara y la inclinación (`PARAM_ANGLE_Z` y `PARAM_BODY_ANGLE_Z`) en cada cuadro. Es una capa encima del lienzo, así que **no toca los archivos del modelo**.

- Vienen dos: **sombrero de bruja** (`bruja`) y **sombrero vueltiao** (`colombiana`). Los dibuja `scripts/dibujar_accesorios.py` (arte propio, con Pillow).
- **Octubre:** todo el mes, si la variante no tiene accesorio propio, Miku usa el de bruja (`"octubre": "bruja"`). Además hay un ambiente de Halloween suave (viñeta morada y naranja, murciélagos y una calabaza que flotan despacio, sin destellos) y el chip «🎃 Octubre».
- En Ajustes → Variante → **Accesorio en Live2D**: Automático (según la variante y la temporada), Ninguno o uno fijo.
- Atajos de URL: `?accesorio=colombiana`, `?accesorio=ninguno`, `?temporada=octubre` o `?temporada=normal` para probar. Con `?depurar=1` se dibuja la caja de la cara en rojo.

Formato, en `contenido/accesorios/accesorios.json` (el PNG va al lado, en `contenido/accesorios/<variante>.png`):

```json
{
  "octubre": "bruja",
  "accesorios": {
    "bruja": {
      "nombre": "Sombrero de bruja",
      "archivo": "accesorios/bruja.png",
      "ancho": 3.0, "dx": 0.08, "dy": 0.3, "giro": -6, "ancla": [0.5, 0.82]
    }
  }
}
```

- `ancho`: cuántas veces el ancho de la cara mide el PNG.
- `dx` y `dy`: corrimiento desde el borde de arriba de la cara, medido en anchos de cara (un `dy` negativo lo sube).
- `giro`: grados extra. `ancla`: el punto del PNG (de 0 a 1) que queda pegado a la cabeza; normalmente es el centro del ala.

Un paquete del día también puede traer accesorios nuevos o reemplazar uno, con el mismo formato y el PNG en su carpeta:

```json
"accesorios": {
  "sakura": { "nombre": "Flor de cerezo", "archivo": "dias/2026-10-05/flor.png", "ancho": 1.2, "dx": 0.4, "dy": 0.1 }
}
```

## Banco de frases

`contenido/frases/banco.json` tiene el banco base, que hoy suma 227 frases: 110 generales, 50 por variante (5 por cada una), 40 de octubre más 12 de octubre para variantes, y 15 de noche. Está dividido en `bloques`, y cada bloque lleva hasta 40 `frases` y/o un `por_variante`, con una `temporada` opcional (`octubre`, `noche`, `marzo-mayo`, `vacaciones`…, el mismo texto de `mikuverse.json`). La app lo mezcla con las frases de siempre y con las de los paquetes del día. Para sumar frases todo el año alcanza con un paquete del día, y para una temporada nueva se agrega un bloque aquí.

## Actualizaciones en el Chromebook

`instalar.sh` ya lo deja activo. Si alguna vez hace falta repetirlo: `bash ~/mikuverse/scripts/activar-actualizaciones.sh`.

- **Servidor:** `miku-en-casa.service` (systemd del usuario) arranca con Linux y se reinicia solo.
- **Actualizador:** `miku-en-casa-actualizar.timer` revisa 2 minutos después de arrancar Linux y cada 3 horas (`Persistent=true`, así se pone al día si el contenedor estuvo apagado). Si `systemd --user` no responde, queda una entrada de cron equivalente.
- **De dónde baja:** el repo público `https://github.com/crudofrio/miku-` (tarball de `codeload.github.com`). Sin usuario, sin token, sin claves en el Chromebook.
- **Seguro:** baja a una carpeta temporal y solo entonces reemplaza `~/.local/share/miku-en-casa`. Si la descarga falla, no toca nada. El modelo y Cubism Core que ya viven ahí se conservan (se comprueba su huella) y nunca se bajan de nuevo. También refresca `~/mikuverse` sin borrar lo tuyo.

Cuando el service worker ve código nuevo, o aparece un paquete en el manifiesto, sale el aviso «Miku se actualizó 💙». Se recarga sola a los 10 segundos, o al toque en «Verla».

La fuente está en `~/.config/miku-en-casa/fuente` (`MIKU_REPO`, `MIKU_RAMA`, `MIKU_PROYECTO`). El log, en `~/.local/state/miku-en-casa/actualizar.log`.

### Publicar un paquete nuevo

Basta con hacer commit de `contenido/dias/AAAA-MM-DD.json` (y su carpeta de PNG si trae fondo) en `main`. En menos de 3 horas, o al siguiente arranque de Linux, el Chromebook lo tiene.

## Qué hay y qué no hay en este repo

Está el código de la app ya compilada (`app/`), los scripts, los paquetes del día y los dibujos de Mikuverse. **No está** el modelo Live2D (`.moc3`, texturas, `model3.json`) ni Cubism Core: `.gitignore` los bloquea y el actualizador los descarta si aparecieran. Cada Chromebook los baja directo de live2d.com con `scripts/traer-modelo.sh`, para uso personal.

## Por qué el modelo no está en internet

El modelo de muestra y Cubism Core no deben publicarse en GitHub Pages, Netlify ni ningún host abierto. `localhost` en el contenedor Linux es la vía privada: el archivo no sale del Chromebook, Chrome lo trata como origen seguro y, tras la primera visita, la app instalada vive en la caché.

Otras ideas que encajan peor: una extensión (incómoda a pantalla completa), o un APK con WebView (hay que firmarlo y sideloadearlo, y cambiar un dibujo es más pesado). El contenedor gana porque ya tienes Linux y el script es un solo comando.

## Desarrollo en este repo

```bash
npm install
python3 scripts/preparar_sprites.py
MIKU_ZIP=/ruta/miku_ja.zip CORE_ZIP=/ruta/CubismSdkForWeb-4-r.7.zip ./scripts/traer-modelo.sh public
npm run dev
```

Sin esas variables, `traer-modelo.sh` descarga los zip oficiales. `public/live2d` y `public/cubism` están en `.gitignore` a propósito.

```bash
npm test
npm run build
npm run preview
```

La vista previa queda en el puerto 8741.

## Licencias

Lee [NOTICES.md](NOTICES.md). Resumen: fan art y personaje bajo la licencia Piapro, solo uso personal; el modelo se descarga en el equipo; Cubism Core se extrae del SDK 4-r.7 y tampoco se sube al repositorio.

## Fuera de esta versión

- **Chat con IA.** Un modelo pequeño puede vivir en Linux, en otro puerto de localhost, y esta página le mandaría el texto. No hace falta una API de internet.
- **Spotify.** El reproductor web pide cuenta y red. Si más adelante aceptas salir a internet, un panel de «suena ahora» sería un módulo aparte.
- **Alexa u otras rutinas.** Una rutina puede abrir `http://localhost:8741/?modo=fiesta` mientras Linux está encendido. No hay skill propia.
- **Flotar encima de otras apps.** Una página no puede dibujarse sobre las ventanas de ChromeOS. Más adelante podría ser una ventana de Linux siempre visible, o una app de Android con permiso de superposición. No entra aquí.
