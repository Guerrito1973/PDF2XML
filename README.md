# PDF2XML
Conversor PDF a XML para parseo de tablas

## Descripción

Este proyecto extrae tablas de archivos PDF y las convierte a formato XML. Está diseñado específicamente para trabajar con PDFs creados mediante "select.PDF for .NET v2017 17.3.0".

### Características

- **Extracción de tablas entre marcadores de sección**: Extrae tablas comprendidas entre "HISTORIAL CURSOS ClÍNICOS" y "Constantes"
- **Procesamiento de tablas multi-página**: Mantiene la integridad de las filas aunque se corten en saltos de página
- **Eliminación de protecciones**: Remueve automáticamente las protecciones del PDF antes de procesarlo
- **Procesamiento por lotes**: Puede procesar un único PDF o todos los PDFs en un directorio
- **Salida XML estructurada**: Genera archivos XML bien formados con la estructura de las tablas

## Requisitos

- Python 3.7 o superior
- Bibliotecas Python (ver `requirements.txt`)

## Instalación

1. Clone el repositorio:
```bash
git clone https://github.com/Guerrito1973/PDF2XML.git
cd PDF2XML
```

2. Instale las dependencias:
```bash
pip install -r requirements.txt
```

## Uso

### Procesar un único archivo PDF

```bash
python pdf2xml.py archivo.pdf
```

### Procesar todos los PDFs en un directorio

```bash
python pdf2xml.py --directory /ruta/a/directorio
```

O simplemente:

```bash
python pdf2xml.py /ruta/a/directorio
```

### Opciones avanzadas

```bash
# Usar un archivo de configuración personalizado
python pdf2xml.py --config mi_config.json archivo.pdf

# Especificar directorio de salida personalizado
python pdf2xml.py --output resultados archivo.pdf

# Activar modo verbose para más información
python pdf2xml.py --verbose archivo.pdf

# Guardar logs en un archivo para debugging
python pdf2xml.py --log-file proceso.log archivo.pdf

# Combinar opciones: verbose + guardar logs
python pdf2xml.py --verbose --log-file debug.log archivo.pdf

# Ver ayuda completa
python pdf2xml.py --help
```

## Logs y Debugging

### ¿Dónde están los logs?

Por defecto, los logs se muestran en la **salida de consola** (stdout/stderr) cuando ejecutas el script. 

Para guardar los logs en un archivo para revisión posterior:

```bash
# Guardar logs en un archivo específico
python pdf2xml.py --log-file proceso.log archivo.pdf

# Modo verbose con archivo de logs (recomendado para debugging)
python pdf2xml.py --verbose --log-file debug.log archivo.pdf
```

Los archivos de log incluyen:
- Timestamp de cada operación
- Nivel de log (INFO, WARNING, ERROR, DEBUG)
- Mensajes detallados sobre el procesamiento
- Información sobre páginas procesadas y tablas extraídas
- Errores y excepciones completas

### Niveles de logging

- **Normal**: Muestra operaciones principales (INFO y superior)
- **Verbose** (`--verbose`): Muestra información detallada de debugging (DEBUG y superior)

```
## Configuración

El archivo `config.json` permite personalizar el comportamiento del extractor:

```json
{
  "section_start_marker": "HISTORIAL CURSOS ClÍNICOS",
  "section_end_marker": "Constantes",
  "output_directory": "output"
}
```

### Parámetros de configuración

- **section_start_marker**: Texto que marca el inicio de la sección a extraer
- **section_end_marker**: Texto que marca el final de la sección a extraer
- **output_directory**: Directorio donde se guardarán los archivos XML generados

## Formato de salida XML

Los archivos XML generados tienen la siguiente estructura:

```xml
<?xml version='1.0' encoding='utf-8'?>
<document source="archivo.pdf" section_start="HISTORIAL CURSOS ClÍNICOS" section_end="Constantes">
  <table id="1" rows="10">
    <header>
      <column index="1">Columna1</column>
      <column index="2">Columna2</column>
    </header>
    <data>
      <row index="1">
        <cell column="1" name="Columna1">Valor1</cell>
        <cell column="2" name="Columna2">Valor2</cell>
      </row>
      <!-- Más filas... -->
    </data>
  </table>
</document>
```

## Cómo funciona

1. **Eliminación de protecciones**: El script primero intenta remover cualquier protección del PDF usando `pikepdf`
2. **Búsqueda de marcadores**: Localiza las páginas que contienen los marcadores de inicio y fin de sección
3. **Extracción de tablas**: Utiliza `pdfplumber` para extraer las tablas en el rango de páginas identificado
4. **Unión de tablas multi-página**: Detecta y une automáticamente tablas que continúan en múltiples páginas basándose en la estructura de columnas
5. **Generación de XML**: Convierte las tablas extraídas a formato XML estructurado usando `lxml`
6. **Limpieza**: Elimina archivos temporales creados durante el proceso

## Resolución de problemas

### No se encuentran los marcadores de sección

Verifique que los textos "HISTORIAL CURSOS ClÍNICOS" y "Constantes" existan exactamente como están escritos en el PDF. Puede personalizar estos marcadores en el archivo `config.json`.

### No se extraen tablas

- Asegúrese de que el PDF contenga tablas reales (no solo texto formateado)
- Algunos PDFs pueden requerir OCR si son imágenes escaneadas
- Use el modo verbose (`--verbose`) para más información sobre el proceso

### Errores de permisos

Si obtiene errores relacionados con permisos del PDF, el script intentará removerlos automáticamente. Si persiste el problema, puede intentar desbloquear el PDF manualmente primero.

## Licencia

Este proyecto está disponible como código abierto.

## Contribuciones

Las contribuciones son bienvenidas. Por favor, abra un issue para discutir cambios importantes antes de crear un pull request.
