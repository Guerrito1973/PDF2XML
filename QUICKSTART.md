# Guía de Inicio Rápido / Quick Start Guide

## Instalación Rápida / Quick Installation

```bash
# Clonar el repositorio / Clone the repository
git clone https://github.com/Guerrito1973/PDF2XML.git
cd PDF2XML

# Instalar dependencias / Install dependencies
pip install -r requirements.txt
```

## Uso Básico / Basic Usage

### Procesar un solo PDF / Process a single PDF
```bash
python pdf2xml.py mi_archivo.pdf
```

### Procesar todos los PDFs en un directorio / Process all PDFs in a directory
```bash
python pdf2xml.py --directory /ruta/a/pdfs
```

## Requisitos de los PDFs / PDF Requirements

Los PDFs deben contener:
- Texto buscable "HISTORIAL CURSOS ClÍNICOS" (marca el inicio de la sección)
- Texto buscable "Constantes" (marca el final de la sección)
- Tablas entre estos dos marcadores

PDFs must contain:
- Searchable text "HISTORIAL CURSOS ClÍNICOS" (marks the start of the section)
- Searchable text "Constantes" (marks the end of the section)
- Tables between these two markers

## Salida / Output

Los archivos XML generados se guardarán en el directorio `output/` por defecto.

Generated XML files will be saved in the `output/` directory by default.

## Solución de Problemas Comunes / Common Troubleshooting

### Error: No se encuentran los marcadores
**Problema**: El script no encuentra "HISTORIAL CURSOS ClÍNICOS" o "Constantes"
**Solución**: Verifique que estos textos existan exactamente en el PDF. Puede personalizar los marcadores en `config.json`

### Error: No se extraen tablas
**Problema**: El script no detecta tablas en el PDF
**Solución**: 
- Asegúrese de que el PDF tenga tablas reales (no solo texto formateado)
- Algunos PDFs escaneados pueden requerir OCR primero
- Use `--verbose` para obtener más información del proceso

### Error: PDF protegido
**Problema**: El PDF tiene protecciones que impiden su procesamiento
**Solución**: El script intenta remover protecciones automáticamente. Si falla, intente desbloquear el PDF manualmente primero.

## Ejemplos / Examples

```bash
# Ejemplo 1: Procesar un PDF con salida en un directorio personalizado
# Example 1: Process a PDF with output to a custom directory
python pdf2xml.py --output mis_resultados documento.pdf

# Ejemplo 2: Procesar con modo verbose para debugging
# Example 2: Process with verbose mode for debugging
python pdf2xml.py --verbose documento.pdf

# Ejemplo 3: Usar configuración personalizada
# Example 3: Use custom configuration
python pdf2xml.py --config mi_config.json documento.pdf
```

## Contacto / Contact

Para reportar problemas o hacer preguntas, use el sistema de Issues de GitHub:
https://github.com/Guerrito1973/PDF2XML/issues

For reporting issues or asking questions, use GitHub Issues:
https://github.com/Guerrito1973/PDF2XML/issues
