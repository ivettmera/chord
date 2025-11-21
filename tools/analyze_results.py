#!/usr/bin/env python3
"""
Script de análisis para resultados de experimentos Chord DHT
Analiza métricas de escalabilidad y genera gráficos
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import glob
import os
import sys
from pathlib import Path

def analyze_single_experiment(exp_dir):
    """Analiza un experimento individual"""
    try:
        # Leer métricas globales
        global_file = os.path.join(exp_dir, "global_metrics.csv")
        if not os.path.exists(global_file):
            print(f"Archivo de métricas globales no encontrado: {global_file}")
            return None
            
        global_df = pd.read_csv(global_file)
        
        # Leer todas las métricas individuales
        node_files = glob.glob(os.path.join(exp_dir, "node_*_metrics.csv"))
        
        if global_df.empty:
            print(f"Métricas globales vacías en {exp_dir}")
            return None
            
        # Obtener última fila con métricas finales
        final_metrics = global_df.iloc[-1]
        
        result = {
            'experiment': os.path.basename(exp_dir),
            'total_nodes': int(final_metrics['total_nodes']),
            'total_messages': int(final_metrics['total_messages']),
            'total_lookups': int(final_metrics['total_lookups']),
            'avg_latency_ms': float(final_metrics['avg_lookup_ms']),
            'node_files_count': len(node_files),
            'directory': exp_dir
        }
        
        # Calcular métricas adicionales si hay suficientes datos
        if len(global_df) > 1:
            # Throughput promedio (lookups por segundo)
            time_diff = pd.to_datetime(global_df['timestamp']).iloc[-1] - pd.to_datetime(global_df['timestamp']).iloc[0]
            if time_diff.total_seconds() > 0:
                result['lookups_per_second'] = result['total_lookups'] / time_diff.total_seconds()
            else:
                result['lookups_per_second'] = 0
        else:
            result['lookups_per_second'] = 0
            
        return result
        
    except Exception as e:
        print(f"Error analizando {exp_dir}: {e}")
        return None

def generate_scalability_report(results_dir="results"):
    """Genera reporte completo de escalabilidad"""
    
    if not os.path.exists(results_dir):
        print(f"Directorio de resultados no encontrado: {results_dir}")
        return
    
    # Encontrar todos los experimentos
    exp_dirs = []
    for item in os.listdir(results_dir):
        item_path = os.path.join(results_dir, item)
        if os.path.isdir(item_path) and ('exp' in item or 'node' in item):
            exp_dirs.append(item_path)
    
    if not exp_dirs:
        print("No se encontraron directorios de experimentos")
        return
    
    print(f"Encontrados {len(exp_dirs)} experimentos:")
    for exp_dir in exp_dirs:
        print(f"  - {exp_dir}")
    
    # Analizar cada experimento
    all_results = []
    for exp_dir in exp_dirs:
        result = analyze_single_experiment(exp_dir)
        if result:
            all_results.append(result)
    
    if not all_results:
        print("No se pudieron analizar experimentos")
        return
    
    # Crear DataFrame con resultados
    df = pd.DataFrame(all_results)
    df = df.sort_values('total_nodes')
    
    print("\n=== RESUMEN DE ESCALABILIDAD ===")
    print(df[['experiment', 'total_nodes', 'total_messages', 'total_lookups', 
              'avg_latency_ms', 'lookups_per_second']].to_string(index=False))
    
    # Generar gráficos
    generate_plots(df, results_dir)
    
    # Guardar resumen CSV
    summary_file = os.path.join(results_dir, "scalability_summary.csv")
    df.to_csv(summary_file, index=False)
    print(f"\nResumen guardado en: {summary_file}")
    
    return df

def generate_plots(df, results_dir):
    """Genera gráficos de escalabilidad"""
    
    # Crear figura con subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Análisis de Escalabilidad - Chord DHT', fontsize=16, fontweight='bold')
    
    # Gráfico 1: Latencia vs Número de Nodos
    axes[0, 0].plot(df['total_nodes'], df['avg_latency_ms'], 'bo-', linewidth=2, markersize=8)
    axes[0, 0].set_xlabel('Número de Nodos')
    axes[0, 0].set_ylabel('Latencia Promedio (ms)')
    axes[0, 0].set_title('Latencia vs Escalabilidad')
    axes[0, 0].grid(True, alpha=0.3)
    
    # Gráfico 2: Throughput vs Número de Nodos
    axes[0, 1].plot(df['total_nodes'], df['lookups_per_second'], 'go-', linewidth=2, markersize=8)
    axes[0, 1].set_xlabel('Número de Nodos')
    axes[0, 1].set_ylabel('Lookups por Segundo')
    axes[0, 1].set_title('Throughput vs Escalabilidad')
    axes[0, 1].grid(True, alpha=0.3)
    
    # Gráfico 3: Mensajes Totales vs Número de Nodos
    axes[1, 0].bar(df['total_nodes'], df['total_messages'], alpha=0.7, color='orange')
    axes[1, 0].set_xlabel('Número de Nodos')
    axes[1, 0].set_ylabel('Mensajes Totales')
    axes[1, 0].set_title('Tráfico de Red vs Escalabilidad')
    axes[1, 0].grid(True, alpha=0.3)
    
    # Gráfico 4: Eficiencia (Lookups por Mensaje)
    efficiency = df['total_lookups'] / df['total_messages']
    axes[1, 1].plot(df['total_nodes'], efficiency, 'ro-', linewidth=2, markersize=8)
    axes[1, 1].set_xlabel('Número de Nodos')
    axes[1, 1].set_ylabel('Lookups por Mensaje')
    axes[1, 1].set_title('Eficiencia vs Escalabilidad')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Guardar gráfico
    plot_file = os.path.join(results_dir, "scalability_analysis.png")
    plt.savefig(plot_file, dpi=300, bbox_inches='tight')
    print(f"Gráficos guardados en: {plot_file}")
    
    # Mostrar gráficos si es posible
    try:
        plt.show()
    except:
        print("No se puede mostrar gráficos en este entorno")

def analyze_individual_nodes(exp_dir):
    """Analiza métricas de nodos individuales en un experimento"""
    
    node_files = glob.glob(os.path.join(exp_dir, "node_*_metrics.csv"))
    
    if not node_files:
        print(f"No se encontraron archivos de nodos en {exp_dir}")
        return
    
    print(f"\n=== ANÁLISIS DE NODOS INDIVIDUALES - {os.path.basename(exp_dir)} ===")
    
    node_metrics = []
    for node_file in node_files:
        try:
            df = pd.read_csv(node_file)
            if not df.empty:
                final_row = df.iloc[-1]
                node_metrics.append({
                    'node': os.path.basename(node_file).replace('_metrics.csv', ''),
                    'messages': int(final_row['messages']),
                    'lookups': int(final_row['lookups']),
                    'avg_latency': float(final_row['avg_lookup_ms'])
                })
        except Exception as e:
            print(f"Error leyendo {node_file}: {e}")
    
    if node_metrics:
        node_df = pd.DataFrame(node_metrics)
        print(node_df.to_string(index=False))
        
        # Estadísticas de distribución
        print(f"\nEstadísticas de distribución:")
        print(f"Latencia - Media: {node_df['avg_latency'].mean():.2f}ms, Std: {node_df['avg_latency'].std():.2f}ms")
        print(f"Mensajes - Media: {node_df['messages'].mean():.1f}, Std: {node_df['messages'].std():.1f}")
        print(f"Lookups - Media: {node_df['lookups'].mean():.1f}, Std: {node_df['lookups'].std():.1f}")

def main():
    """Función principal"""
    
    if len(sys.argv) > 1:
        results_dir = sys.argv[1]
    else:
        results_dir = "results"
    
    print("=== ANALIZADOR DE RESULTADOS CHORD DHT ===")
    print(f"Directorio de resultados: {results_dir}")
    
    # Generar reporte de escalabilidad
    df = generate_scalability_report(results_dir)
    
    if df is not None:
        # Analizar nodos individuales para cada experimento
        for _, row in df.iterrows():
            analyze_individual_nodes(row['directory'])
    
    print("\n=== ANÁLISIS COMPLETADO ===")

if __name__ == "__main__":
    main()