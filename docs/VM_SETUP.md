# Configuración para VMs de Google Cloud

## Configuración de Red

### VM 1 (us-east1)
- IP Externa: [IP_EXTERNA_VM1]
- IP Interna: [IP_INTERNA_VM1]
- Puerto: 8000

### VM 2 (europe-west1)
- IP Externa: [IP_EXTERNA_VM2]
- IP Interna: [IP_INTERNA_VM2]
- Puerto: 8000

### VM 3 (asia-southeast1)
- IP Externa: [IP_EXTERNA_VM3]  
- IP Interna: [IP_INTERNA_VM3]
- Puerto: 8000

## Instrucciones de Instalación en cada VM

1. Instalar Go:
```bash
wget https://golang.org/dl/go1.19.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.19.linux-amd64.tar.gz
echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
source ~/.bashrc
```

2. Clonar y compilar el proyecto:
```bash
git clone [REPO_URL]
cd chord
go mod tidy
go build -o chord-server ./server
go build -o chord-client ./client
go build -o chord-simulator ./cmd/simulator
```

3. Configurar firewall:
```bash
# Permitir puerto 8000
sudo ufw allow 8000
# Permitir rango de puertos para simulador (8000-8100)
sudo ufw allow 8000:8100/tcp
```

## Comandos para Ejecutar

### En VM1 (Bootstrap):
```bash
# Crear el ring inicial
./chord-server create --addr 0.0.0.0 --port 8000

# O ejecutar simulador local
./chord-simulator -nodes 20 -start-port 8001 -bootstrap-addr [IP_INTERNA_VM1] -bootstrap-port 8000 -duration 300s -output results/vm1
```

### En VM2:
```bash
# Unirse al ring existente
./chord-server join --addr 0.0.0.0 --port 8000 --contact [IP_EXTERNA_VM1]:8000

# O ejecutar simulador local
./chord-simulator -nodes 20 -start-port 8001 -bootstrap-addr [IP_EXTERNA_VM1] -bootstrap-port 8000 -duration 300s -output results/vm2
```

### En VM3:
```bash
# Unirse al ring existente  
./chord-server join --addr 0.0.0.0 --port 8000 --contact [IP_EXTERNA_VM1]:8000

# O ejecutar simulador local
./chord-simulator -nodes 20 -start-port 8001 -bootstrap-addr [IP_EXTERNA_VM1] -bootstrap-port 8000 -duration 300s -output results/vm3
```

## Experimentos de Escalabilidad

### Experimento 1: Pocos Nodos (5 por VM)
```bash
./chord-simulator -nodes 5 -duration 60s -output results/exp1_5nodes
```

### Experimento 2: Nodos Medianos (15 por VM)  
```bash
./chord-simulator -nodes 15 -duration 120s -output results/exp2_15nodes
```

### Experimento 3: Muchos Nodos (30 por VM)
```bash
./chord-simulator -nodes 30 -duration 180s -output results/exp3_30nodes
```

### Experimento 4: Máximo Nodos (50 por VM)
```bash
./chord-simulator -nodes 50 -duration 300s -output results/exp4_50nodes
```

## Recolección de Resultados

Los archivos CSV se generarán en:
- `results/[experimento]/node_*_metrics.csv` - Métricas individuales por nodo
- `results/[experimento]/global_metrics.csv` - Métricas agregadas

## Análisis de Resultados

Usar el siguiente script Python para analizar:

```python
import pandas as pd
import matplotlib.pyplot as plt
import glob

def analyze_experiment(exp_dir):
    # Leer métricas globales
    global_df = pd.read_csv(f"{exp_dir}/global_metrics.csv")
    
    # Leer todas las métricas individuales
    node_files = glob.glob(f"{exp_dir}/node_*_metrics.csv")
    
    print(f"Experimento: {exp_dir}")
    print(f"Nodos totales: {global_df['total_nodes'].iloc[-1]}")
    print(f"Mensajes totales: {global_df['total_messages'].iloc[-1]}")
    print(f"Lookups totales: {global_df['total_lookups'].iloc[-1]}")
    print(f"Latencia promedio: {global_df['avg_lookup_ms'].iloc[-1]:.2f}ms")
    print("-" * 50)

# Analizar todos los experimentos
for exp in ['exp1_5nodes', 'exp2_15nodes', 'exp3_30nodes', 'exp4_50nodes']:
    analyze_experiment(f"results/{exp}")
```