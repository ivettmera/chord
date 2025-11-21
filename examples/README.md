# Ejemplos

Este directorio contiene ejemplos de uso y casos de prueba para el sistema Chord DHT.

## Estructura

### `test-nodes/`
Contiene archivos de ejemplo que muestran cómo crear nodos de prueba programáticamente.

Archivos incluidos:
- `node1.go.example` - Ejemplo de nodo bootstrap
- `node2.go.example` - Ejemplo de nodo que se une al ring
- `node3.go.example` - Ejemplo de nodo adicional
- `node4.go.example` - Ejemplo de nodo con configuración custom
- `node5.go.example` - Ejemplo de nodo con métricas habilitadas

## Uso

Los archivos `.example` son plantillas que puedes copiar y modificar:

```bash
# Copiar ejemplo para uso
cp examples/test-nodes/node1.go.example my_node.go

# Editar según tus necesidades
vim my_node.go

# Compilar y ejecutar
go run my_node.go
```

## Propósito

Estos ejemplos están diseñados para:
- Mostrar diferentes configuraciones de nodos
- Servir como punto de partida para desarrollo
- Demostrar patrones de uso comunes
- Facilitar pruebas y debugging

**Nota**: Los archivos tienen extensión `.example` para evitar conflictos durante la compilación del proyecto principal.