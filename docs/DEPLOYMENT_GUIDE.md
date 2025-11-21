# Guía de Despliegue - Chord DHT en 3 VMs de Google Cloud

## Configuración de Red

### IPs Externas de las VMs
- **ds-node-1 (Bootstrap)**: `34.38.96.126` - Europa (europe-west1-d) 🇪🇺
- **ds-node-2**: `35.199.69.216` - Sudamérica (southamerica-east1-c) 🇧🇷  
- **us-central1-c**: `34.58.253.117` - US Central (us-central1-c) 🇺🇸

### Arquitectura del Sistema
```
Internet
    |
┌───┴─────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  ds-node-1 (Europa)    ds-node-2 (Sudamérica)    us-central1-c (US)    │
│  34.38.96.126          35.199.69.216              34.58.253.117         │
│  ┌─────────────┐      ┌─────────────┐       ┌─────────────┐ │
│  │Bootstrap:800│─────▶│  Node:8000  │◀──────│  Node:8000  │ │
│  │             │      │             │       │             │ │
│  │Simulator:   │      │Simulator:   │       │Simulator:   │ │
│  │8001-8050    │      │8001-8050    │       │8001-8050    │ │
│  └─────────────┘      └─────────────┘       └─────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘

Total: 153 nodos (3 físicos + 150 simulados)
```

## Paso 1: Preparar el Código en cada VM

### Conectarse a cada VM:
```bash
# VM1 (España - Bootstrap)
gcloud compute ssh chord-vm1 --zone=europe-west1-b

# VM2 (US Central)
gcloud compute ssh chord-vm2 --zone=us-central1-a

# VM3 (US East)
gcloud compute ssh chord-vm3 --zone=us-east1-b
```

### En cada VM, ejecutar:
```bash
# Instalar Go
wget https://golang.org/dl/go1.21.5.linux-amd64.tar.gz
sudo rm -rf /usr/local/go && sudo tar -C /usr/local -xzf go1.21.5.linux-amd64.tar.gz
echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
source ~/.bashrc

# Clonar tu proyecto
git clone https://github.com/tu-usuario/chord.git
cd chord

# Compilar
go mod tidy
go build -o bin/chord-server ./server
go build -o bin/chord-client ./client
go build -o bin/chord-simulator ./cmd/simulator

# Crear directorios para resultados
mkdir -p results/metrics
mkdir -p results/logs
```

## Paso 2: Configurar Firewall (ejecutar localmente)

```bash
# Permitir puertos para Chord
gcloud compute firewall-rules create chord-dht-ports \
    --allow tcp:8000-8100 \
    --source-ranges 0.0.0.0/0 \
    --target-tags chord-node \
    --description "Puertos para Chord DHT - MC714 Projeto"
```

## Paso 3: Ejecutar los Nodos

### VM1 (34.38.96.126) - Nodo Bootstrap:
```bash
cd ~/chord

# Ejecutar como bootstrap (crear el ring)
./bin/chord-server create \
    --addr 0.0.0.0 \
    --port 8000 \
    --metrics \
    --metrics-dir results/metrics/vm1_bootstrap \
    --log-level info \
    > results/logs/vm1_bootstrap.log 2>&1 &

# Guardar PID para poder detenerlo después
echo $! > vm1_bootstrap.pid

echo "Bootstrap node iniciado en VM1 (España)"
echo "IP: 34.38.96.126:8000"
```

### VM2 (35.199.69.216) - Unirse al ring:
```bash
cd ~/chord

# Esperar 30 segundos para que bootstrap esté listo
sleep 30

# Unirse al ring usando la IP de VM1
./bin/chord-server join 34.38.96.126 8000 \
    --addr 0.0.0.0 \
    --port 8000 \
    --metrics \
    --metrics-dir results/metrics/vm2_node \
    --log-level info \
    > results/logs/vm2_node.log 2>&1 &

echo $! > vm2_node.pid

echo "Nodo VM2 conectado al ring"
echo "IP: 35.199.69.216:8000"
```

### VM3 (34.58.253.117) - Unirse al ring:
```bash
cd ~/chord

# Esperar que VM2 se conecte
sleep 30

# Unirse al ring usando la IP de VM1
./bin/chord-server join 34.38.96.126 8000 \
    --addr 0.0.0.0 \
    --port 8000 \
    --metrics \
    --metrics-dir results/metrics/vm3_node \
    --log-level info \
    > results/logs/vm3_node.log 2>&1 &

echo $! > vm3_node.pid

echo "Nodo VM3 conectado al ring"
echo "IP: 34.58.253.117:8000"
```

## Paso 4: Verificar Conectividad

### Desde cualquier VM, probar operaciones:
```bash
# Test 1: Guardar datos desde VM1
echo "Hola desde España" | ./bin/chord-client put 34.38.96.126:8000 key_from_spain

# Test 2: Leer desde VM2 (US Central)
./bin/chord-client get 35.199.69.216:8000 key_from_spain

# Test 3: Leer desde VM3 (US East)
./bin/chord-client get 34.58.253.117:8000 key_from_spain

# Test 4: Guardar desde VM2
echo "Hello from US Central" | ./bin/chord-client put 35.199.69.216:8000 key_from_us_central

# Test 5: Leer desde VM1
./bin/chord-client get 34.38.96.126:8000 key_from_us_central

# Test 6: Localizar claves
./bin/chord-client locate 34.58.253.117:8000 key_from_spain
./bin/chord-client locate 34.38.96.126:8000 key_from_us_central
```

## Paso 5: Ejecutar Simulaciones de Escalabilidad

### VM1 (España) - 50 nodos simulados:
```bash
cd ~/chord

# Simulación de 50 nodos por 10 minutos
./bin/chord-simulator \
    -nodes 50 \
    -start-port 8001 \
    -bootstrap-addr 34.38.96.126 \
    -bootstrap-port 8000 \
    -duration 600s \
    -output results/metrics/vm1_sim_50nodes \
    > results/logs/vm1_simulator.log 2>&1 &

echo $! > vm1_simulator.pid
echo "Simulador VM1: 50 nodos locales iniciados"
```

### VM2 (US Central) - 50 nodos simulados:
```bash
cd ~/chord

# Simulación de 50 nodos conectándose al bootstrap en España
./bin/chord-simulator \
    -nodes 50 \
    -start-port 8001 \
    -bootstrap-addr 34.38.96.126 \
    -bootstrap-port 8000 \
    -duration 600s \
    -output results/metrics/vm2_sim_50nodes \
    > results/logs/vm2_simulator.log 2>&1 &

echo $! > vm2_simulator.pid
echo "Simulador VM2: 50 nodos locales iniciados"
```

### VM3 (US East) - 50 nodos simulados:
```bash
cd ~/chord

# Simulación de 50 nodos conectándose al bootstrap en España
./bin/chord-simulator \
    -nodes 50 \
    -start-port 8001 \
    -bootstrap-addr 34.38.96.126 \
    -bootstrap-port 8000 \
    -duration 600s \
    -output results/metrics/vm3_sim_50nodes \
    > results/logs/vm3_simulator.log 2>&1 &

echo $! > vm3_simulator.pid
echo "Simulador VM3: 50 nodos locales iniciados"
```

## Paso 6: Monitoreo y Logs

### Verificar estado de los procesos:
```bash
# Ver procesos corriendo
ps aux | grep chord

# Ver logs en tiempo real
tail -f results/logs/vm1_bootstrap.log
tail -f results/logs/vm1_simulator.log

# Verificar métricas
ls -la results/metrics/
head results/metrics/*/metrics_*.csv
```

### Comandos de control:
```bash
# Detener nodo principal
kill $(cat vm1_bootstrap.pid)

# Detener simulador
kill $(cat vm1_simulator.pid)

# Detener todos los procesos chord
pkill -f chord
```

## Paso 7: Recolección de Resultados

### En cada VM, crear script de recolección:
```bash
# crear collect_results.sh
cat > collect_results.sh << 'EOF'
#!/bin/bash
echo "Recolectando resultados de $(hostname)..."

# Crear directorio con timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RESULTS_DIR="chord_results_${TIMESTAMP}"
mkdir -p $RESULTS_DIR

# Copiar métricas
cp -r results/metrics $RESULTS_DIR/
cp -r results/logs $RESULTS_DIR/

# Información del sistema
echo "Hostname: $(hostname)" > $RESULTS_DIR/system_info.txt
echo "Fecha: $(date)" >> $RESULTS_DIR/system_info.txt
echo "Uptime: $(uptime)" >> $RESULTS_DIR/system_info.txt
echo "Memoria: $(free -h)" >> $RESULTS_DIR/system_info.txt

# Comprimir
tar -czf ${RESULTS_DIR}.tar.gz $RESULTS_DIR
echo "Resultados guardados en: ${RESULTS_DIR}.tar.gz"
EOF

chmod +x collect_results.sh
```

### Desde tu máquina local, descargar resultados:
```bash
# Crear directorio local para resultados
mkdir -p ~/chord_experiment_results

# Descargar de cada VM
gcloud compute scp chord-vm1:~/chord/chord_results_*.tar.gz ~/chord_experiment_results/vm1_spain_results.tar.gz --zone=europe-west1-b

gcloud compute scp chord-vm2:~/chord/chord_results_*.tar.gz ~/chord_experiment_results/vm2_us_central_results.tar.gz --zone=us-central1-a

gcloud compute scp chord-vm3:~/chord/chord_results_*.tar.gz ~/chord_experiment_results/vm3_us_east_results.tar.gz --zone=us-east1-b
```

## Experimentos Sugeridos

### Experimento 1: Latencia por Región
```bash
# Medir tiempo de lookup desde cada región
for i in {1..100}; do
    time ./bin/chord-client get 34.38.96.126:8000 test_key_$i
    time ./bin/chord-client get 35.199.69.216:8000 test_key_$i  
    time ./bin/chord-client get 34.58.253.117:8000 test_key_$i
done
```

### Experimento 2: Escalabilidad Incremental
```bash
# Iniciar con 10 nodos, incrementar cada 2 minutos
for nodes in 10 20 30 40 50; do
    echo "Iniciando $nodes nodos..."
    # (comando de simulador con $nodes)
    sleep 120
done
```

### Experimento 3: Tolerancia a Fallos
```bash
# Detener VM2 y verificar que el ring sigue funcionando
# En VM2:
pkill -f chord

# En VM1 y VM3:
./bin/chord-client get IP:8000 existing_key
```

## Resolución de Problemas

### Si no se pueden conectar los nodos:
```bash
# Verificar firewall
gcloud compute firewall-rules list | grep chord

# Verificar puertos abiertos
sudo netstat -tlnp | grep 8000

# Verificar conectividad entre VMs
telnet 34.38.96.126 8000
```

### Si las métricas no se generan:
```bash
# Verificar permisos
ls -la results/metrics/
chmod -R 755 results/
```

Esta configuración te permitirá demostrar el funcionamiento del protocolo Chord en un ambiente distribuido real con latencia intercontinental (España ↔ US).