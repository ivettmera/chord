# RESUMEN DE MODIFICACIONES - PROYECTO CHORD DHT

## Archivos Creados/Modificados

### 1. Sistema de Métricas
- **`metrics.go`** - Módulo principal de métricas
  - `MetricsCollector`: Colecta métricas por nodo
  - `GlobalMetricsAggregator`: Agrega métricas de múltiples nodos
  - Formato CSV: `timestamp,nodes,messages,lookups,avg_lookup_ms`

### 2. Configuración Multi-VM
- **`config.go`** - Agregados campos para métricas
  - `EnableMetrics bool`
  - `MetricsOutputDir string`

- **`server/main.go`** - Soporte para flags de métricas
  - `--metrics`: Habilita colección de métricas
  - `--metrics-dir`: Directorio de salida

### 3. Instrumentación del Nodo
- **`node.go`** - Integración de métricas
  - Campo `metrics *MetricsCollector` en struct Node
  - Inicialización automática si está habilitado
  - Cierre graceful en shutdown()

- **`rpc.go`** - Instrumentación de operaciones
  - FindSuccessor, Locate: Registro de latencia y lookups
  - Get, Put: Conteo de mensajes

### 4. Simulador
- **`cmd/simulator/main.go`** - Simulador completo
  - Crea múltiples nodos locales
  - Ejecuta lookups aleatorios
  - Genera métricas individuales y globales
  - Soporte para experimentos de escalabilidad

### 5. Scripts de Automatización

#### Configuración de VMs:
- **`setup-vm.sh`** - Configuración automática de VMs
- **`VM_SETUP.md`** - Instrucciones detalladas para VMs
- **`README_VM.md`** - Documentación completa del sistema

#### Construcción y Ejecución:
- **`build.sh`** - Script de compilación
- **`demo.sh`** - Demostración local del sistema
- **`run-experiments.sh`** - Experimentos de escalabilidad

#### Scripts para VMs (generados por setup-vm.sh):
- `compile.sh` - Compila el proyecto
- `run-bootstrap.sh` - Ejecuta nodo bootstrap
- `run-join.sh` - Une nodo al ring
- `run-simulator.sh` - Ejecuta simulador
- `collect-results.sh` - Recolecta resultados

### 6. Análisis de Resultados
- **`analyze_results.py`** - Script Python para análisis
  - Genera gráficos de escalabilidad
  - Calcula estadísticas de distribución
  - Crea resumen CSV global

## Arquitectura de Escalabilidad

### Nodos Físicos (3 VMs)
```
VM1 (us-east1)     ←→    VM2 (europe-west1)    ←→    VM3 (asia-southeast1)
Bootstrap:8000           Node:8000                     Node:8000
+ Simulator              + Simulator                   + Simulator  
```

### Nodos Lógicos (Simulador)
Cada VM puede ejecutar el simulador para crear múltiples nodos locales:
- VM1: Puertos 8001-8050 (50 nodos)
- VM2: Puertos 8001-8050 (50 nodos)  
- VM3: Puertos 8001-8050 (50 nodos)
- **Total**: Hasta 153 nodos (3 físicos + 150 simulados)

## Experimentos de Escalabilidad

### Configuración de Experimentos
1. **exp1_5nodes**: 5 nodos, 60s → Baseline
2. **exp2_15nodes**: 15 nodos, 120s → Escala pequeña
3. **exp3_30nodes**: 30 nodos, 180s → Escala media
4. **exp4_50nodes**: 50 nodos, 300s → Escala grande

### Métricas Evaluadas
- **Latencia**: Tiempo promedio de lookup (ms)
- **Throughput**: Lookups por segundo
- **Tráfico**: Mensajes totales enviados
- **Eficiencia**: Lookups por mensaje
- **Distribución**: Estadísticas por nodo

## Uso del Sistema

### 1. Configuración Inicial
```bash
# En cada VM
./setup-vm.sh
git clone [REPO]
./build.sh
```

### 2. Modo Nodos Físicos
```bash
# VM1 (Bootstrap)
./bin/chord-server create --addr 0.0.0.0 --port 8000 --metrics

# VM2, VM3
./bin/chord-server join IP_VM1 8000 --addr 0.0.0.0 --port 8000 --metrics
```

### 3. Modo Simulador
```bash
# En cada VM
./run-experiments.sh IP_VM1
```

### 4. Análisis de Resultados
```bash
# Recolectar de cada VM
./collect-results.sh

# Analizar localmente
python analyze_results.py results/
```

## Características Técnicas

### Métricas por Nodo
- Escritura cada 10 segundos
- Formato CSV estándar
- Métricas acumulativas y promedios

### Agregación Global
- Suma métricas de todos los nodos
- Calcula promedios ponderados
- Genera visualizaciones

### Tolerancia a Fallos
- Manejo de errores de conexión
- Timeouts configurables
- Logs detallados para debugging

### Optimizaciones
- Pool de conexiones reutilizable
- Lookups concurrentes
- Métricas en memoria hasta flush

## Resultados Esperados

### Latencia vs Escalabilidad
- Crecimiento logarítmico con número de nodos
- Impacto de latencia de red entre regiones
- Estabilización después de convergencia

### Throughput vs Carga
- Escalabilidad horizontal
- Distribución de carga balanceada
- Degradación graceful bajo alta carga

## Archivos de Configuración

### server/config.yaml
```yaml
addr: 0.0.0.0
port: 8000
enablemetrics: true
metricsoutputdir: "metrics"
logging: false
```

### Parámetros del Simulador
- `-nodes`: Número de nodos (5-50 recomendado)
- `-duration`: Duración experimento (60s-600s)
- `-lookup-interval`: Frecuencia de lookups (500ms-2s)
- `-keyspace`: Espacio de claves (100-10000)

## Validación del Sistema

### Tests Incluidos
- Conectividad entre VMs
- Operaciones básicas (Get/Put)
- Convergencia del ring
- Métricas consistency

### Comandos de Validación
```bash
# Test local
./demo.sh

# Test conectividad VM
nc -zv IP_VM 8000

# Test operaciones
echo "test" | ./bin/chord-client put IP:8000 key
./bin/chord-client get IP:8000 key
```

Este sistema está completamente configurado para ejecutar experimentos de escalabilidad en múltiples VMs de Google Cloud, con colección automática de métricas y análisis de resultados.