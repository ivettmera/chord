# 🚀 Guía: Subir Chord DHT a GitHub y Desplegar en VMs

## 📋 Paso 1: Preparar el Repositorio Local

### Inicializar Git (si no está inicializado)
```bash
# Verificar si ya es un repo
git status

# Si no es un repo, inicializar
git init
```

### Configurar Git (si es necesario)
```bash
# Configurar tu información
git config --global user.name "Tu Nombre"
git config --global user.email "tu-email@ejemplo.com"

# Verificar configuración
git config --list
```

### Limpiar y preparar archivos
```bash
# Ver qué archivos están tracked
git status

# Agregar archivos importantes (evitar binarios)
git add README.md
git add docs/
git add scripts/
git add tools/
git add examples/
git add cmd/
git add server/
git add client/
git add chordpb/
git add *.go
git add go.mod
git add go.sum
git add Makefile
git add LICENSE
git add .gitignore

# NO agregar:
# git add bin/  (binarios compilados)
```

### Actualizar .gitignore
```bash
# Crear/actualizar .gitignore
cat >> .gitignore << EOF
# Binarios compilados
bin/
server/chord
client/chord

# Archivos temporales
*.tmp
*.log
nohup.out

# Resultados de experimentos
results/
metrics_*/
*.csv

# Archivos del sistema
.DS_Store
Thumbs.db

# IDEs
.vscode/
.idea/
*.swp
*.swo

# Go específicos
vendor/
EOF
```

## 📤 Paso 2: Crear Repositorio en GitHub

### Opción A: Desde GitHub Web
1. Ve a https://github.com
2. Click en "New repository"
3. Nombre: `chord-dht-mc714`
4. Descripción: `Chord DHT implementation - MC714 Sistemas Distribuidos UNICAMP`
5. ✅ Public repository
6. ❌ NO inicializar con README (ya tienes uno)
7. Click "Create repository"

### Opción B: Desde GitHub CLI (si tienes gh instalado)
```bash
gh repo create chord-dht-mc714 --public --description "Chord DHT implementation - MC714 Sistemas Distribuidos UNICAMP"
```

## 📤 Paso 3: Subir al Repositorio

### Conectar con el repositorio remoto
```bash
# Cambiar por tu usuario de GitHub
git remote add origin https://github.com/TU-USUARIO/chord-dht-mc714.git

# Verificar remote
git remote -v
```

### Commit inicial
```bash
# Hacer commit de todos los archivos
git commit -m "🚀 Initial commit: Chord DHT with multi-VM support

✅ Features implemented:
- Complete Chord DHT protocol
- Multi-VM deployment support (3 continents)
- Automatic metrics collection (CSV)
- Scalability simulator (up to 200+ nodes)
- gRPC client for GET/PUT/LOCATE operations
- Automated deployment scripts for Google Cloud
- Cross-continental testing capabilities

🌍 VM Configuration:
- ds-node-1: Europe (34.38.96.126)
- ds-node-2: South America (35.199.69.216)  
- us-central1-c: US Central (34.58.253.117)

📚 Project: MC714 - Sistemas Distribuidos | UNICAMP 2024"
```

### Push al repositorio
```bash
# Primera subida
git branch -M main
git push -u origin main
```

## 📥 Paso 4: Clonar en las VMs

### En cada VM (ds-node-1, ds-node-2, us-central1-c):

```bash
# Conectarse a la VM
gcloud compute ssh ds-node-1 --zone=europe-west1-d
# o
gcloud compute ssh ds-node-2 --zone=southamerica-east1-c  
# o
gcloud compute ssh us-central1-c --zone=us-central1-c

# En la VM, clonar el proyecto
git clone https://github.com/TU-USUARIO/chord-dht-mc714.git
cd chord-dht-mc714

# Instalar Go 1.21 (si no está instalado)
./scripts/deployment/setup-vm.sh

# Compilar el proyecto
./scripts/build/build.sh

# Verificar que todo funciona
ls bin/
```

## 🔧 Paso 5: Configuración Rápida de VMs

### Script automatizado para cada VM:
```bash
# En cada VM, crear script de setup rápido
cat > quick-setup.sh << 'EOF'
#!/bin/bash
echo "🚀 Configurando Chord DHT..."

# Actualizar sistema
sudo apt update

# Instalar herramientas básicas
sudo apt install -y git htop

# Compilar proyecto
cd chord-dht-mc714
./scripts/build/build.sh

# Crear directorios para métricas
mkdir -p results/metrics results/logs

echo "✅ Setup completado. Listo para ejecutar Chord DHT!"
echo "📝 Siguiente paso:"
echo "   Bootstrap: ./bin/chord-server create --addr 0.0.0.0 --port 8000 --metrics"
echo "   Join: ./bin/chord-server join 34.38.96.126 8000 --addr 0.0.0.0 --port 8000 --metrics"
EOF

chmod +x quick-setup.sh
./quick-setup.sh
```

## 🎯 Paso 6: Verificar Instalación

### En cada VM, probar:
```bash
# Verificar compilación
./bin/chord-server --help
./bin/chord-client --help
./bin/chord-simulator --help

# Verificar Go
go version

# Verificar puertos disponibles
sudo netstat -tlnp | grep :8000
```

## 📝 Comandos de Referencia Rápida

### Para subir cambios futuros:
```bash
git add .
git commit -m "📝 Update: descripción del cambio"
git push
```

### Para actualizar VMs con cambios:
```bash
# En cada VM
cd chord-dht-mc714
git pull
./scripts/build/build.sh
```

### Para limpiar y recompilar:
```bash
# Limpiar binarios
rm -rf bin/*

# Recompilar
./scripts/build/build.sh
```

## 🔗 Enlaces Útiles

- **Tu repositorio**: `https://github.com/TU-USUARIO/chord-dht-mc714`
- **Guía de despliegue**: `docs/DEPLOYMENT_GUIDE.md`
- **Inicio rápido**: `QUICK_START_GLOBAL.md`
- **Scripts de VM**: `scripts/deployment/`

## 🚨 Notas Importantes

1. **Reemplaza `TU-USUARIO`** con tu username real de GitHub
2. **No subas binarios** (están en .gitignore)
3. **Las métricas** se generan localmente en cada VM
4. **Firewall** debe estar configurado (puertos 8000-8100)
5. **Orden de ejecución**: Europa → Sudamérica → US Central

¡Listo para desplegar tu DHT global! 🌍🚀