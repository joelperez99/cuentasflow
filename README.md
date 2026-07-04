# CuentasFlow

Aplicación web para registrar diariamente las cuentas creadas durante la jornada laboral, con apariencia de producto SaaS (estilo Notion / Linear / Airtable), construida con **Python + Streamlit** y **Google Sheets** como única base de datos.

## Índice

1. [Características](#características)
2. [Estructura del proyecto](#estructura-del-proyecto)
3. [Requisitos](#requisitos)
4. [Instalación](#instalación)
5. [Configurar Google Cloud y Google Sheets](#configurar-google-cloud-y-google-sheets)
6. [Archivo secrets.toml](#archivo-secretstoml)
7. [Ejecución](#ejecución)
8. [Estructura de las hojas de cálculo](#estructura-de-las-hojas-de-cálculo)
9. [Notas técnicas](#notas-técnicas)

## Características

- Login con usuarios almacenados en Google Sheets.
- Registro diario de cuentas mediante un modal elegante (formulario de dos columnas, validaciones, sin recargar la página).
- Tabla avanzada (AgGrid): búsqueda, filtros, orden, redimensionar/ocultar columnas, edición vía doble clic, duplicar, eliminar con confirmación, exportar a Excel/CSV, paginación.
- Dashboard con métricas (hoy, semana, mes, promedio diario) y gráficas Plotly (semanal, mensual, por empleado).
- Historial con calendario y filtros por empleado/búsqueda.
- Configuración de proyecto, empleado, logo y tema.
- Estilos personalizados que ocultan el "chrome" nativo de Streamlit para lograr un look de producto comercial.

## Estructura del proyecto

```
project/
├── app.py
├── pages/
│   ├── dashboard.py
│   ├── hoy.py
│   ├── historial.py
│   └── configuracion.py
├── components/
│   ├── sidebar.py
│   ├── cards.py
│   ├── modal.py
│   ├── table.py
│   ├── metrics.py
│   ├── navbar.py
│   └── dialogs.py
├── database/
│   └── google_sheet.py
├── services/
│   ├── auth.py
│   ├── accounts.py
│   └── analytics.py
├── utils/
│   ├── constants.py
│   ├── helpers.py
│   └── styles.py
├── assets/
│   └── logo.png
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml   (creado por ti, ver más abajo)
├── requirements.txt
└── README.md
```

## Requisitos

- Python 3.12+ (compatible también con 3.10/3.11)
- Una cuenta de Google Cloud con acceso a Google Sheets API y Google Drive API
- Un Google Sheet compartido con el service account

## Instalación

```bash
# 1. Clona o descarga el proyecto y entra a la carpeta
cd project

# 2. Crea un entorno virtual (recomendado)
python -m venv .venv
source .venv/bin/activate        # En Windows: .venv\Scripts\activate

# 3. Instala las dependencias
pip install -r requirements.txt
```

## Configurar Google Cloud y Google Sheets

1. Entra a [Google Cloud Console](https://console.cloud.google.com/) y crea (o selecciona) un proyecto.
2. Habilita las APIs **Google Sheets API** y **Google Drive API** (menú "APIs y servicios" → "Biblioteca").
3. Crea una **Service Account**: "APIs y servicios" → "Credenciales" → "Crear credenciales" → "Cuenta de servicio".
4. Dentro de la cuenta de servicio, ve a la pestaña **Claves** → "Agregar clave" → "Crear clave nueva" → tipo **JSON**. Se descargará un archivo `.json` con las credenciales.
5. Crea una hoja de cálculo nueva en Google Sheets (puede estar vacía; la aplicación crea las pestañas y encabezados automáticamente la primera vez que se ejecuta).
6. **Comparte** esa hoja de cálculo con el correo de la service account (campo `client_email` del JSON descargado), dándole permisos de **Editor**.
7. Copia el **ID del spreadsheet** desde la URL: `https://docs.google.com/spreadsheets/d/ESTE_ES_EL_ID/edit`.

## Archivo secrets.toml

Copia la plantilla incluida y complétala con los datos del JSON descargado:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Edita `.streamlit/secrets.toml`:

```toml
[google_sheets]
spreadsheet_id = "EL_ID_DE_TU_SPREADSHEET"

[gcp_service_account]
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "...@....iam.gserviceaccount.com"
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "..."
universe_domain = "googleapis.com"
```

> ⚠️ El archivo `secrets.toml` real nunca debe subirse a un repositorio público. Ya está incluido en `.gitignore`.

### Crear el primer usuario

La aplicación crea automáticamente la hoja **Usuarios** (con columnas `Usuario`, `Password`, `Nombre`, `Rol`) la primera vez que se conecta. Abre el Google Sheet y agrega manualmente al menos una fila, por ejemplo:

| Usuario | Password | Nombre        | Rol   |
|---------|----------|---------------|-------|
| admin   | 12345    | Administrador | Admin |

## Ejecución

```bash
streamlit run app.py
```

Abre el navegador en `http://localhost:8501`, inicia sesión con el usuario creado en el paso anterior y comienza a registrar cuentas.

## Estructura de las hojas de cálculo

La aplicación crea automáticamente (si no existen) las siguientes pestañas dentro del spreadsheet configurado:

**Usuarios**: `Usuario`, `Password`, `Nombre`, `Rol`

**Cuentas**: `ID`, `Email`, `DOB`, `Pass1`, `Pass2`, `Direccion`, `Nombre`, `Apellido`, `Telefono`, `Usuario`, `Comentarios`, `Fecha`, `Hora`, `Empleado`

**Configuracion**: `Clave`, `Valor` (reservada para futuras preferencias globales)

## Notas técnicas

- **Modal**: se utiliza el componente nativo `st.dialog` de Streamlit (equivalente moderno a `streamlit-modal`), que ofrece animación, fondo oscurecido y mejor integración con el ciclo de vida de la app.
- **Edición por doble clic**: la tabla usa un `JsCode` en AgGrid que marca la fila al detectar `onRowDoubleClicked`; Streamlit detecta el cambio y abre el modal de edición con los datos precargados.
- **Caché**: las lecturas de Google Sheets se cachean (`st.cache_data`, TTL configurable en `utils/constants.py`) para minimizar las llamadas a la API; toda escritura invalida la caché automáticamente.
- **Reconexión**: `GoogleSheetsService` reintenta automáticamente ante errores transitorios de la API (`APIError`) y reconecta el cliente si es necesario.
- **Seguridad de contraseñas**: el servicio de autenticación admite contraseñas en texto plano (para simplicidad inicial) o hasheadas con SHA-256; se recomienda migrar a hashes antes de producción.
