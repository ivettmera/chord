# Proyecto Chord DHT - Estructura Reorganizada

```
chord/
├── README.md                   # Documentación principal
├── go.mod                     # Dependencias de Go
├── go.sum                     # Checksums de dependencias
├── Makefile                   # Comandos de construcción
├── LICENSE                    # Licencia del proyecto
│
├── docs/                      # 📚 Documentación
│   ├── DEPLOYMENT_GUIDE.md    # Guía de despliegue en Google Cloud
│   └── MODIFICATIONS_SUMMARY.md # Resumen de modificaciones
│
├── cmd/                       # 🚀 Aplicaciones principales
│   └── simulator/             # Simulador de escalabilidad
│       └── main.go
│
├── server/                    # 🖥️  Aplicación servidor
│   ├── main.go
│   ├── config.yaml
│   └── chord                  # Binario compilado
│
├── client/                    # 💻 Aplicación cliente
│   ├── main.go
│   ├── config.yaml
│   └── chord                  # Binario compilado
│
├── chordpb/                   # 📡 Definiciones Protocol Buffers
│   ├── chord.proto
│   └── chord.pb.go
│
├── scripts/                   # 🛠️  Scripts de automatización
│   └── deployment/
│       └── vm-scripts/        # Scripts para VMs de Google Cloud
│           └── README.md
│
├── examples/                  # 📋 Ejemplos y tests
│   └── test-nodes/           # Nodos de ejemplo (antes test/)
│       ├── node1.go.example
│       ├── node2.go.example
│       ├── node3.go.example
│       ├── node4.go.example
│       └── node5.go.example
│
└── *.go                      # 🔧 Código fuente principal
    ├── node.go               # Implementación del nodo Chord
    ├── rpc.go                # Implementación gRPC
    ├── config.go             # Configuración del sistema
    ├── finger.go             # Tabla de dedos (finger table)
    ├── replica.go            # Sistema de replicación
    ├── util.go               # Utilidades generales
    ├── metrics.go            # Sistema de métricas
    └── *_test.go             # Tests unitarios
```

## Ventajas de esta Estructura

### 🎯 **Organización Clara**
- **`docs/`**: Toda la documentación centralizada
- **`cmd/`**: Aplicaciones ejecutables siguiendo convención Go
- **`scripts/`**: Automatización separada del código fuente
- **`examples/`**: Casos de uso y ejemplos prácticos

### 🚀 **Facilidad de Uso**
- Compilación: `go build -o bin/chord-server ./server`
- Documentación: Todo en `docs/`
- Scripts de VM: `scripts/deployment/vm-scripts/`
- Ejemplos: `examples/test-nodes/`

### 📦 **Distribución**
- Código fuente principal en la raíz (estándar para librerías Go)
- Aplicaciones en `cmd/` y subdirectorios específicos
- Documentación bien organizada para GitHub
- Scripts de despliegue separados por contexto

### 🔧 **Desarrollo**
- Imports simples: `"github.com/cdesiniotis/chord"`
- Tests junto al código que prueban
- Configuración cerca de las aplicaciones
- Separación clara entre código y herramientas

## Archivos Principales

### Core DHT
- `node.go` - Implementación principal del protocolo Chord
- `rpc.go` - Servicios gRPC y comunicación entre nodos
- `finger.go` - Tabla de dedos para lookups eficientes
- `replica.go` - Sistema de replicación de datos

### Configuración y Utilidades  
- `config.go` - Gestión de configuración y parámetros
- `util.go` - Funciones auxiliares y utilitarios
- `metrics.go` - Sistema de métricas y monitoreo

### Aplicaciones
- `server/main.go` - Nodo servidor del ring Chord
- `client/main.go` - Cliente para operaciones GET/PUT/LOCATE
- `cmd/simulator/main.go` - Simulador multi-nodo para escalabilidad

### Documentación
- `docs/DEPLOYMENT_GUIDE.md` - Guía completa para VMs de Google Cloud
- `docs/MODIFICATIONS_SUMMARY.md` - Resumen de cambios realizados
- `scripts/deployment/vm-scripts/README.md` - Scripts de automatización

Esta estructura es estándar en proyectos Go, facilita el mantenimiento y es intuitiva para nuevos desarrolladores.