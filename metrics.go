package chord

import (
	"encoding/csv"
	"fmt"
	"os"
	"path/filepath"
	"sync"
	"time"
)

// MetricsCollector colecta y registra métricas del nodo
type MetricsCollector struct {
	nodeID           string
	startTime        time.Time
	messagesSent     int64
	lookupsPerformed int64
	lookupLatencies  []float64
	currentNodes     int64

	mutex     sync.RWMutex
	csvFile   *os.File
	csvWriter *csv.Writer
}

// NewMetricsCollector crea un nuevo colector de métricas
func NewMetricsCollector(nodeID string, outputDir string) (*MetricsCollector, error) {
	// Crear directorio si no existe
	if err := os.MkdirAll(outputDir, 0755); err != nil {
		return nil, fmt.Errorf("error creating output directory: %v", err)
	}

	// Crear archivo CSV para este nodo
	filename := filepath.Join(outputDir, fmt.Sprintf("node_%s_metrics.csv", nodeID))
	file, err := os.Create(filename)
	if err != nil {
		return nil, fmt.Errorf("error creating CSV file: %v", err)
	}

	writer := csv.NewWriter(file)

	// Escribir header
	header := []string{"timestamp", "nodes", "messages", "lookups", "avg_lookup_ms"}
	if err := writer.Write(header); err != nil {
		file.Close()
		return nil, fmt.Errorf("error writing CSV header: %v", err)
	}
	writer.Flush()

	mc := &MetricsCollector{
		nodeID:          nodeID,
		startTime:       time.Now(),
		lookupLatencies: make([]float64, 0),
		csvFile:         file,
		csvWriter:       writer,
	}

	// Iniciar goroutine para escribir métricas periódicamente
	go mc.periodicWrite()

	return mc, nil
}

// IncrementMessages incrementa el contador de mensajes enviados
func (mc *MetricsCollector) IncrementMessages() {
	mc.mutex.Lock()
	defer mc.mutex.Unlock()
	mc.messagesSent++
}

// RecordLookup registra un lookup realizado con su latencia
func (mc *MetricsCollector) RecordLookup(latencyMs float64) {
	mc.mutex.Lock()
	defer mc.mutex.Unlock()
	mc.lookupsPerformed++
	mc.lookupLatencies = append(mc.lookupLatencies, latencyMs)
}

// UpdateNodeCount actualiza el número de nodos conocidos
func (mc *MetricsCollector) UpdateNodeCount(count int64) {
	mc.mutex.Lock()
	defer mc.mutex.Unlock()
	mc.currentNodes = count
}

// GetCurrentMetrics retorna las métricas actuales
func (mc *MetricsCollector) GetCurrentMetrics() (int64, int64, int64, float64) {
	mc.mutex.RLock()
	defer mc.mutex.RUnlock()

	avgLatency := 0.0
	if len(mc.lookupLatencies) > 0 {
		sum := 0.0
		for _, latency := range mc.lookupLatencies {
			sum += latency
		}
		avgLatency = sum / float64(len(mc.lookupLatencies))
	}

	return mc.currentNodes, mc.messagesSent, mc.lookupsPerformed, avgLatency
}

// writeMetrics escribe las métricas actuales al CSV
func (mc *MetricsCollector) writeMetrics() error {
	mc.mutex.Lock()
	defer mc.mutex.Unlock()

	avgLatency := 0.0
	if len(mc.lookupLatencies) > 0 {
		sum := 0.0
		for _, latency := range mc.lookupLatencies {
			sum += latency
		}
		avgLatency = sum / float64(len(mc.lookupLatencies))
	}

	timestamp := time.Now().Format("2006-01-02 15:04:05")
	record := []string{
		timestamp,
		fmt.Sprintf("%d", mc.currentNodes),
		fmt.Sprintf("%d", mc.messagesSent),
		fmt.Sprintf("%d", mc.lookupsPerformed),
		fmt.Sprintf("%.2f", avgLatency),
	}

	if err := mc.csvWriter.Write(record); err != nil {
		return err
	}
	mc.csvWriter.Flush()
	return nil
}

// periodicWrite escribe métricas cada 10 segundos
func (mc *MetricsCollector) periodicWrite() {
	ticker := time.NewTicker(10 * time.Second)
	defer ticker.Stop()

	for range ticker.C {
		if err := mc.writeMetrics(); err != nil {
			fmt.Printf("Error writing metrics for node %s: %v\n", mc.nodeID, err)
		}
	}
}

// Close cierra el archivo CSV y finaliza la colección de métricas
func (mc *MetricsCollector) Close() error {
	// Escribir métricas finales
	if err := mc.writeMetrics(); err != nil {
		fmt.Printf("Error writing final metrics: %v\n", err)
	}

	mc.csvWriter.Flush()
	return mc.csvFile.Close()
}

// GlobalMetricsAggregator agrega métricas de múltiples nodos
type GlobalMetricsAggregator struct {
	outputDir string
	mutex     sync.RWMutex
}

// NewGlobalMetricsAggregator crea un nuevo agregador de métricas globales
func NewGlobalMetricsAggregator(outputDir string) *GlobalMetricsAggregator {
	return &GlobalMetricsAggregator{
		outputDir: outputDir,
	}
}

// AggregateMetrics agrega todas las métricas de los nodos en un CSV global
func (gma *GlobalMetricsAggregator) AggregateMetrics() error {
	gma.mutex.Lock()
	defer gma.mutex.Unlock()

	// Crear archivo de resultados globales
	globalFile := filepath.Join(gma.outputDir, "global_metrics.csv")
	file, err := os.Create(globalFile)
	if err != nil {
		return fmt.Errorf("error creating global metrics file: %v", err)
	}
	defer file.Close()

	writer := csv.NewWriter(file)
	defer writer.Flush()

	// Escribir header
	header := []string{"timestamp", "total_nodes", "total_messages", "total_lookups", "avg_lookup_ms"}
	if err := writer.Write(header); err != nil {
		return fmt.Errorf("error writing global CSV header: %v", err)
	}

	// Leer todos los archivos de métricas individuales
	files, err := filepath.Glob(filepath.Join(gma.outputDir, "node_*_metrics.csv"))
	if err != nil {
		return fmt.Errorf("error finding metrics files: %v", err)
	}

	// Agregar datos (implementación simple - toma la última entrada de cada nodo)
	totalNodes := int64(len(files))
	totalMessages := int64(0)
	totalLookups := int64(0)
	totalLatencies := []float64{}

	for _, filename := range files {
		nodeMessages, nodeLookups, nodeLatencies := gma.readLastEntry(filename)
		totalMessages += nodeMessages
		totalLookups += nodeLookups
		totalLatencies = append(totalLatencies, nodeLatencies...)
	}

	avgLatency := 0.0
	if len(totalLatencies) > 0 {
		sum := 0.0
		for _, latency := range totalLatencies {
			sum += latency
		}
		avgLatency = sum / float64(len(totalLatencies))
	}

	// Escribir resumen global
	timestamp := time.Now().Format("2006-01-02 15:04:05")
	record := []string{
		timestamp,
		fmt.Sprintf("%d", totalNodes),
		fmt.Sprintf("%d", totalMessages),
		fmt.Sprintf("%d", totalLookups),
		fmt.Sprintf("%.2f", avgLatency),
	}

	return writer.Write(record)
}

// readLastEntry lee la última entrada de un archivo de métricas de nodo
func (gma *GlobalMetricsAggregator) readLastEntry(filename string) (int64, int64, []float64) {
	file, err := os.Open(filename)
	if err != nil {
		return 0, 0, nil
	}
	defer file.Close()

	reader := csv.NewReader(file)
	records, err := reader.ReadAll()
	if err != nil || len(records) < 2 {
		return 0, 0, nil
	}

	// Tomar la última fila (excluyendo header)
	lastRecord := records[len(records)-1]
	if len(lastRecord) < 5 {
		return 0, 0, nil
	}

	messages := int64(0)
	lookups := int64(0)

	fmt.Sscanf(lastRecord[2], "%d", &messages)
	fmt.Sscanf(lastRecord[3], "%d", &lookups)

	// Para simplicidad, no agregamos latencias individuales aquí
	return messages, lookups, nil
}
