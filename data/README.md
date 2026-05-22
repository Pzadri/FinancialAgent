# Directorio de Datos

Aquí se colocan los archivos fuente (Excel, CSV) que alimentan el dashboard.

## Estructura

```
data/
├── gbm/
│   ├── portafolio-nacional.xlsx    # Detalle portafolio mercado nacional
│   └── portafolio-usa.xlsx         # Detalle portafolio mercado USA
├── GI/
│   └── gastos-ingresos.xlsx        # Base de datos de gastos e ingresos
├── README.md
```

## Instrucciones

- **GBM:** Actualizar los archivos semanalmente. Los nombres deben mantenerse consistentes.
- **GI:** Este archivo se gestiona automáticamente desde la app (formulario de registro). No editar manualmente.
- El backend lee automáticamente los archivos de cada carpeta.
