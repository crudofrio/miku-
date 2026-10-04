# Recopilatorio de Miku en casa 💙

Todo lo que ha recibido Miku hasta el 2 de octubre de 2026.

## La app (versión base, 25 de septiembre)

- **Miku en Live2D.** El modelo gratuito oficial, con física, respiración, parpadeo, un movimiento en bucle y la mirada que sigue tu dedo o el cursor. Si la tocas, hace un movimiento y te dice una frase.
- **Mikuverse: 10 variantes.** Pixel, chibi, samurái, cyberpunk, bruja, sakura, carreras, sirena, astronauta y colombiana (la parcera). Flotan, se encogen cuando las tocas y cada una tiene sus frases. Con «Respetar temporada» activo, cambian según la época: en octubre sale más la bruja, de noche la de neón, de marzo a mayo la sakura, en vacaciones la sirena, y en julio y diciembre la parcera.
- **Fondos.** Cinco wallpapers (puerro, coletas y estrellas, concierto, cyber y nieve), fijos o en rotación, más los que van llegando con los paquetes del día.
- **Voz en español.** Cada 10 a 40 minutos (tú eliges) dice una frase. Busca una voz colombiana y, si no hay, otra en español. Tiene botón de silencio y control de volumen.
- **Modo fiesta.** Con `?modo=fiesta` hay bailes, rebotes y un fondo de barras de luz, sin destellos blancos. Sirve para que una automatización la abra.
- **Funciona sin internet.** Es una app instalable (PWA) que abre desde la caché de Chrome aunque Linux esté apagado. Tiene pantalla completa y evita que la tablet se duerma.
- **Pensada para el Chromebook CM3.** Corre a 30 fps (bajable a 20 si la tablet se calienta) y libera el modelo de la memoria cuando pasas a Mikuverse.

## Novedades del 2 de octubre

- **Accesorios por variante en Live2D.** Cuando eliges una variante, Miku en 3D se pone su accesorio: el **sombrero de bruja** o el **sombrero vueltiao** de la parcera. El accesorio sigue la cabeza y la inclinación de Miku sin tocar el modelo. Desde Ajustes lo puedes dejar en automático, quitarlo o fijar uno.
- **Octubre embrujado 🎃.** Todo el mes hay ambiente de Halloween: una viñeta morada y naranja, murciélagos y una calabaza flotando, el chip «🎃 Octubre» y el sombrero de bruja puesto por defecto.
- **Muchas más frases.** Se agregó un banco base de **227 frases nuevas**: 110 para cualquier día, 50 por variante (5 para cada una), 52 de octubre y Halloween, y 15 de noche. Junto con los paquetes del día, hoy Miku tiene **más de 300 frases nuevas** además de las de siempre.

## Actualizaciones automáticas

- Un temporizador revisa si hay novedades 2 minutos después de arrancar Linux y cada 3 horas. Baja todo a una carpeta aparte y solo cambia la app si la descarga salió bien. Nunca vuelve a bajar ni toca el modelo.
- Cuando llega algo nuevo aparece el aviso **«Miku se actualizó 💙»**, y la app se recarga sola a los 10 segundos o cuando tocas «Verla».
- **Desde el 2 de octubre** baja del repositorio público de GitHub, sin claves ni contraseñas. Se instala con un solo comando (`scripts/instalar.sh`), y el servidor de Miku arranca solo cada vez que se enciende Linux.

## Paquetes del día

| Fecha | Título | Novedades |
|---|---|---|
| 2026-09-25 (vie) | Viernes de puerro | Primer paquete: 8 frases |
| 2026-09-26 (sáb) | Sábado de amanecer | 12 frases y el fondo nuevo **amanecer-sabado** |
| 2026-09-27 (dom) | Domingo de cobija | 12 frases |
| 2026-09-28 (lun) | Lunes de arranque suave | 12 frases |
| 2026-09-29 (mar) | Martes de ensayo | 12 frases y el fondo nuevo **ensayo-martes** |
| 2026-09-30 (mié) | Última página de septiembre | 12 frases |
| 2026-10-01 (jue) | Octubre abre la puerta | 12 frases y el fondo nuevo **octubre-abre**. Arranca la temporada de la Miku bruja 🎃 |
| 2026-10-02 (vie) | Viernes de niebla suave | 12 frases |

Cada paquete es un archivo `contenido/dias/AAAA-MM-DD.json`, y si trae fondo, sus imágenes van en `contenido/dias/AAAA-MM-DD/`.
