# AnimeFLV Downloader

Extrae enlaces de episodios desde animeflv.net y los envía a JDownloader mediante My.JDownloader.

## Requisitos

- Python 3.9+
- JDownloader instalado y en ejecución
- Una cuenta de My.JDownloader (necesaria para el acceso por API)
- Un navegador compatible
  - Chrome: instalar Chrome (el driver se gestiona automáticamente con Selenium Manager)
  - Safari: habilitar la automatización de Safari (solo macOS)

## Instalación

```powershell
.\tasks.ps1 install
```

O directamente con pip:

```powershell
python -m pip install -U pip
python -m pip install -e .
```

## Configuración

Crea un archivo `.env` con tus credenciales de My.JDownloader:

```powershell
Copy-Item .env.example .env
```

Luego edita `.env` y define:

```
JD_EMAIL=tu@email.com
JD_PASSWORD=tupassword
```

## Uso

Ejecutar desde PowerShell (recomendado):

```powershell
.\tasks.ps1 run -- "fullmetal-alchemist-brotherhood" -b chrome
```

O ejecutar el módulo directamente:

```powershell
python -m init "fullmetal-alchemist-brotherhood" -b chrome
```

Opciones:

- `-b`, `--browser`: `chrome` o `safari` (por defecto: `safari`)
- `-o`, `--offset`: empezar desde este número de episodio (por defecto: `0`)
- `-l`, `--limit`: máximo de episodios a agregar (por defecto: `-1` = sin límite)

## Flujo automático

- El script espera automáticamente a que la lista de episodios esté cargada.
- Luego espera a que LinkGrabber termine de recolectar enlaces.
- Antes de moverlos a la lista de descargas, muestra un resumen por episodio y pide confirmación.
- Renombra los episodios como `<anime> <número>.<ext>` y agrupa todo bajo un paquete con el nombre del anime.

## Notas

- JDownloader debe estar abierto y conectado a tu cuenta de My.JDownloader.
- El scraper hace scroll de la lista de episodios para cargar todos los elementos antes de recolectar enlaces.
