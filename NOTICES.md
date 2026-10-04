# Avisos

Uso personal y no comercial. Esta carpeta no es un producto y no debe publicarse con el modelo Live2D dentro.

## Personaje

Hatsune Miku es de Crypton Future Media, Inc. El uso personal de fan art entra en la Piapro Character License. No se presenta como producto oficial.

- https://piapro.net/intl/en_for_creators.html

## Modelo de muestra

El modelo es el sample gratuito «Hatsune Miku» de Live2D, carpeta `miku_free/runtime` del zip oficial. No se modifica el archivo del modelo. El script `scripts/traer-modelo.sh` lo descarga en el equipo y no debe subirse a un hosting público.

- https://www.live2d.com/en/learn/sample/hatsune-miku/
- https://www.live2d.com/eula/live2d-free-material-license-agreement_en.html

Ilustración del modelo: Crypton Future Media, Inc. Modelado: Live2D Inc.

## Cubism Core y framework

Cubism Core (`live2dcubismcore.min.js`) es software propietario. Se usa la build de Cubism SDK for Web 4-r.7, que corresponde al runtime Cubism 3/4 del sample. El script lo extrae del zip oficial. Está en la lista de archivos redistribuibles del SDK, pero este repositorio no lo incluye.

- https://www.live2d.com/eula/live2d-proprietary-software-license-agreement_en.html
- https://www.live2d.com/eula/live2d-open-software-license-agreement_en.html

El render usa `pixi-live2d-display` (MIT), que incorpora el Cubism Web Framework bajo la licencia abierta de Live2D. PixiJS tiene su propia licencia en `node_modules/pixi.js`.

Quien ejecuta el script de instalación acepta esos contratos para un uso personal en su propio equipo. Un negocio con ingresos por encima del umbral de Live2D necesita además la Cubism SDK Release License; este proyecto no está pensado para eso.
