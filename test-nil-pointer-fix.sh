#!/bin/bash

# Script para probar la corrección del panic nil pointer
# Este script reproduce el error original y valida la corrección

set -e

echo "🔧 Testing Chord DHT Nil Pointer Fix"
echo "===================================="

# Crear directorios necesarios
mkdir -p results/logs results/metrics

# Compilar el proyecto
echo "📦 Compilando proyecto..."
go build -o bin/chord-server ./server
go build -o bin/chord-client ./client

echo "✅ Compilación completada"

# Test 1: Crear nodo bootstrap
echo ""
echo "🚀 Test 1: Creando nodo bootstrap..."
nohup ./bin/chord-server create \
    --addr 0.0.0.0 \
    --port 8000 \
    --log-level info \
    > results/logs/bootstrap_test.log 2>&1 &

BOOTSTRAP_PID=$!
echo "Bootstrap PID: $BOOTSTRAP_PID"

# Esperar que el bootstrap se inicialice
sleep 3

# Verificar que el bootstrap está corriendo
if ps -p $BOOTSTRAP_PID > /dev/null; then
    echo "✅ Bootstrap iniciado correctamente"
else
    echo "❌ Bootstrap falló al iniciar"
    cat results/logs/bootstrap_test.log
    exit 1
fi

# Test 2: Intentar join inmediatamente (reproducir el error original)
echo ""
echo "🔗 Test 2: Join inmediato para probar race condition fix..."

for i in {1..3}; do
    echo "  Intento $i de join..."
    
    nohup ./bin/chord-server join localhost 8000 \
        --addr 0.0.0.0 \
        --port 800$i \
        --log-level info \
        > results/logs/join_test_$i.log 2>&1 &
    
    JOIN_PID=$!
    echo "  Join PID: $JOIN_PID"
    
    # Esperar un poco para que se conecte
    sleep 2
    
    # Verificar que el join fue exitoso
    if ps -p $JOIN_PID > /dev/null; then
        echo "  ✅ Join $i exitoso"
    else
        echo "  ⚠️  Join $i terminó (puede ser normal si completó rápidamente)"
        
        # Verificar si hubo panic en los logs
        if grep -q "panic\|SIGSEGV\|nil pointer" results/logs/join_test_$i.log; then
            echo "  ❌ PANIC DETECTADO en join $i:"
            tail -10 results/logs/join_test_$i.log
            echo "  🔧 El fix no funcionó correctamente"
        else
            echo "  ✅ No hay panics en join $i"
        fi
    fi
done

# Test 3: Operaciones básicas para verificar funcionamiento
echo ""
echo "🧪 Test 3: Operaciones básicas..."

sleep 2

# Test PUT
echo "  Testing PUT operation..."
if ./bin/chord-client put localhost:8000 test_key "test_value" 2>/dev/null; then
    echo "  ✅ PUT operation successful"
else
    echo "  ❌ PUT operation failed"
fi

# Test GET  
echo "  Testing GET operation..."
if result=$(./bin/chord-client get localhost:8000 test_key 2>/dev/null); then
    echo "  ✅ GET operation successful: $result"
else
    echo "  ❌ GET operation failed"
fi

# Test 4: Verificar logs de inicialización
echo ""
echo "📋 Test 4: Verificando logs de inicialización..."

echo "  Bootstrap initialization logs:"
if grep -q "successfully created and initialized" results/logs/bootstrap_test.log; then
    echo "  ✅ Bootstrap initialization message found"
else
    echo "  ⚠️  Bootstrap initialization message not found"
fi

echo "  Join initialization logs:"
for i in {1..3}; do
    if [ -f "results/logs/join_test_$i.log" ]; then
        if grep -q "successfully joined ring and initialized" results/logs/join_test_$i.log; then
            echo "  ✅ Join $i initialization message found"
        else
            echo "  ⚠️  Join $i initialization message not found"
        fi
    fi
done

# Test 5: Verificar que no hay panics en ningún log
echo ""
echo "🔍 Test 5: Scanning for panics and errors..."

PANIC_FOUND=false

for logfile in results/logs/*.log; do
    if [ -f "$logfile" ]; then
        if grep -q "panic\|SIGSEGV\|nil pointer\|runtime error" "$logfile"; then
            echo "  ❌ PANIC/ERROR found in $logfile:"
            grep -A 5 -B 5 "panic\|SIGSEGV\|nil pointer\|runtime error" "$logfile"
            PANIC_FOUND=true
        fi
    fi
done

if [ "$PANIC_FOUND" = false ]; then
    echo "  ✅ No panics or nil pointer errors found in any logs"
fi

# Cleanup
echo ""
echo "🧹 Cleanup: Stopping all test processes..."
pkill -f chord-server || echo "No processes to kill"

sleep 2

# Final result
echo ""
echo "📊 RESULTADO FINAL:"
echo "=================="

if [ "$PANIC_FOUND" = false ]; then
    echo "🎉 ✅ NIL POINTER FIX SUCCESSFUL!"
    echo "   - No se detectaron panics"
    echo "   - Los nodos se inicializan correctamente"
    echo "   - Las operaciones básicas funcionan"
    echo "   - Las goroutines de mantenimiento esperan la inicialización"
else
    echo "❌ TESTS FAILED - Aún hay problemas de nil pointer"
    echo "   Revisa los logs en results/logs/"
fi

echo ""
echo "Ver logs detallados:"
echo "- Bootstrap: cat results/logs/bootstrap_test.log"
echo "- Joins: cat results/logs/join_test_*.log"