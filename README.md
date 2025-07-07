# facturator

## Descripción

facturator es una aplicación para gestionar facturación electrónica de manera sencilla y eficiente.

## Requisitos

- Python 3.x
- pip
- Dependencias listadas en `requirements.txt`

## Instalación

```bash
git clone <repo-url>
cd /app
pip install -r requirements.txt
```

## Comando para iniciar

```bash
cd /app && python src/manage.py runserver 0:8000
```

## Uso

Accede a la aplicación en [http://localhost:8000](http://localhost:8000) desde tu navegador.

- `/backoffice/factutas/` es el listado de facturas para pasar a pdf
- `/admin` para crear proveedores, clientes y facturas con sus lineas de factura

## Estructura del proyecto

- `src/` - Código fuente de la aplicación
- `requirements.txt` - Dependencias del proyecto
- `README.md` - Este archivo

## Ejecutar pruebas

```bash
python src/manage.py test
```

## Contribuir

¡Las contribuciones son bienvenidas! Por favor, abre un issue o un pull request.

## Licencia
