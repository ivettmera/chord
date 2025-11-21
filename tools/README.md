# Herramientas de Desarrollo

Este directorio contiene utilidades y herramientas auxiliares para el desarrollo y análisis del proyecto.

## Archivos

### `analyze_results.py`

Script de Python para analizar los resultados de experimentos. Lee archivos CSV de métricas y genera:

- Gráficos de rendimiento
- Estadísticas de latencia
- Análisis de escalabilidad
- Comparaciones entre regiones

### `gen-pb.sh`

Script para generar código Go a partir de definiciones Protocol Buffers.
Procesa `chordpb/chord.proto` y genera `chordpb/chord.pb.go`.

### Uso

```bash
# Analizar resultados de experimentos
python3 tools/analyze_results.py results_directory/

# Regenerar código Protocol Buffers
./tools/gen-pb.sh
```

### Dependencias

- **Python 3**: Para análisis de resultados
- **protoc**: Compilador Protocol Buffers
- **protoc-gen-go**: Plugin Go para protoc