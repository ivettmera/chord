# Chord DHT con Soporte Multi-VM y Métricas

Este proyecto implementa un Distributed Hash Table (DHT) usando el protocolo Chord, optimizado para ejecutarse en múltiples VMs de Google Cloud con capacidades completas de métricas y simulación.

## Características Principales

- **Multi-VM Support**: Diseñado para ejecutarse en 3 VMs de Google Cloud en diferentes regiones
- **Sistema de Métricas**: Colección automática de métricas (latencia, throughput, mensajes)
- **Simulador de Escalabilidad**: Herramienta para probar múltiples nodos locales
- **Análisis de Resultados**: Scripts Python para generar gráficos y análisis

## Arquitectura

### Métricas Registradas
- `timestamp`: Marca de tiempo
- `nodes`: Número de nodos en el ring  
- `messages`: Mensajes enviados
- `lookups`: Lookups realizados
- `avg_lookup_ms`: Latencia promedio en millisegundos

### Archivos de Salida
- `node_*_metrics.csv`: Métricas individuales por nodo
- `global_metrics.csv`: Métricas agregadas del experimento

## Configuración de VMs en Google Cloud

### 1. Crear las VMs

Crear 3 VMs en diferentes regiones:

```bash
# VM 1 - us-east1 (Bootstrap)
gcloud compute instances create chord-vm1 \
    --zone=us-east1-b \
    --machine-type=e2-medium \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud \
    --tags=chord-node

# VM 2 - europe-west1  
gcloud compute instances create chord-vm2 \
    --zone=europe-west1-b \
    --machine-type=e2-medium \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud \
    --tags=chord-node

# VM 3 - asia-southeast1
gcloud compute instances create chord-vm3 \
    --zone=asia-southeast1-b \
    --machine-type=e2-medium \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud \
    --tags=chord-node
```

### 2. Configurar Firewall

```bash
gcloud compute firewall-rules create chord-ports \
    --allow tcp:8000-8100 \
    --source-ranges 0.0.0.0/0 \
    --target-tags chord-node
```

### 3. Configurar cada VM

En cada VM, ejecutar:

```bash
# Descargar script de configuración
wget https://raw.githubusercontent.com/TU_USUARIO/chord/master/setup-vm.sh
chmod +x setup-vm.sh
./setup-vm.sh

# Clonar repositorio
git clone https://github.com/TU_USUARIO/chord.git .

# Compilar proyecto
./compile.sh
```

## Uso del Sistema

### Modo 1: Nodos Físicos (Una VM = Un Nodo)

#### En VM1 (Bootstrap):
```bash
# Iniciar nodo bootstrap con métricas
./chord-server create --addr 0.0.0.0 --port 8000 --metrics --metrics-dir results/bootstrap
```

#### En VM2 y VM3:
```bash
# Reemplazar IP_VM1 con la IP externa de VM1
./run-join.sh IP_VM1
```

### Modo 2: Simulador (Múltiples Nodos por VM)

#### En cada VM:
```bash
# Ejecutar experimentos de escalabilidad
# Reemplazar IP_VM1 con la IP externa de VM1
./run-experiments.sh IP_VM1
```

### Comandos del Simulador

```bash
# Experimento básico
./chord-simulator -nodes 20 -bootstrap-addr IP_VM1 -bootstrap-port 8000 -duration 300s -output results/exp1

# Experimento con parámetros personalizados
./chord-simulator \
    -nodes 50 \
    -start-port 8001 \
    -bootstrap-addr IP_VM1 \
    -bootstrap-port 8000 \
    -duration 600s \
    -output results/exp_custom \
    -lookup-interval 500ms \
    -keyspace 10000
```

## Experimentos de Escalabilidad

El script `run-experiments.sh` ejecuta automáticamente 4 experimentos:

1. **exp1_5nodes**: 5 nodos, 60 segundos
2. **exp2_15nodes**: 15 nodos, 120 segundos  
3. **exp3_30nodes**: 30 nodos, 180 segundos
4. **exp4_50nodes**: 50 nodos, 300 segundos

## Análisis de Resultados

### Recolectar Resultados
```bash
# En cada VM
./collect-results.sh

# Descargar a máquina local
scp user@VM_IP:~/chord_results_*.tar.gz .
```

### Análisis con Python
```bash
# Instalar dependencias
pip install pandas matplotlib numpy

# Ejecutar análisis
python analyze_results.py results/

# O analizar directorio específico
python analyze_results.py path/to/experiment/results/
```

### Métricas Generadas

El script de análisis genera:
- **scalability_summary.csv**: Resumen de todos los experimentos
- **scalability_analysis.png**: Gráficos de análisis
- Estadísticas de distribución por nodo

## Estructura de Archivos

```
chord/
├── metrics.go              # Sistema de métricas
├── cmd/simulator/main.go   # Simulador principal
├── setup-vm.sh            # Script configuración VM
├── run-experiments.sh     # Script experimentos
├── analyze_results.py     # Analizador resultados
├── server/                # Servidor Chord
├── client/                # Cliente Chord
├── results/               # Directorio resultados
└── VM_SETUP.md           # Documentación VMs
```

## Configuración Avanzada

### Habilitar Métricas en config.yaml
```yaml
addr: 0.0.0.0
port: 8000
enablemetrics: true
metricsoutputdir: "custom_metrics"
```

### Parámetros del Simulador
- `-nodes`: Número de nodos a crear
- `-start-port`: Puerto inicial (puertos consecutivos)
- `-bootstrap-addr`: Dirección del nodo bootstrap
- `-bootstrap-port`: Puerto del nodo bootstrap
- `-duration`: Duración del experimento
- `-output`: Directorio de salida
- `-lookup-interval`: Intervalo entre lookups
- `-keyspace`: Espacio de claves para lookups aleatorios

## Troubleshooting

### Problemas Comunes

1. **Error de conexión entre VMs**:
   - Verificar reglas de firewall
   - Confirmar IPs externas correctas
   - Verificar que el puerto 8000 esté libre

2. **Error de compilación**:
   - Verificar instalación de Go
   - Ejecutar `go mod tidy`
   - Verificar permisos de archivos

3. **Métricas no se generan**:
   - Verificar flag `--metrics` o `enablemetrics: true`
   - Confirmar permisos de escritura en directorio
   - Verificar espacio en disco

### Logs y Debug

```bash
# Ver logs del servidor
./chord-server create --logging true

# Monitor de recursos
htop
iostat -x 1

# Test de conectividad
nc -zv IP_BOOTSTRAP 8000
```

## Interpretación de Resultados

### Métricas Clave
- **Latencia**: Tiempo promedio de lookup (objetivo: < 100ms)
- **Throughput**: Lookups por segundo (objetivo: > 100/s)
- **Eficiencia**: Lookups por mensaje (objetivo: > 0.5)
- **Escalabilidad**: Latencia debe crecer logarítmicamente

### Análisis de Escalabilidad
- Comparar experimentos con diferente número de nodos
- Evaluar impacto de latencia de red entre regiones
- Analizar distribución de carga entre nodos

## Desarrollo y Contribución

### Agregar Nuevas Métricas
1. Modificar `MetricsCollector` en `metrics.go`
2. Agregar campos al CSV header
3. Instrumentar código en `rpc.go` o `node.go`
4. Actualizar scripts de análisis

### Personalizar Experimentos
1. Modificar `run-experiments.sh`
2. Agregar nuevos parámetros al simulador
3. Actualizar scripts de análisis

## Referencias

- [Chord Protocol Paper](https://pdos.csail.mit.edu/papers/chord:sigcomm01/chord_sigcomm.pdf)
- [Google Cloud Compute Engine](https://cloud.google.com/compute)
- [Go gRPC Tutorial](https://grpc.io/docs/languages/go/)