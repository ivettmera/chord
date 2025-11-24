import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
import seaborn as sns

sns.set(style="whitegrid")

csv_folder = 'chord/experiments/csv'
csv_files = [
    'busquedas_7_nodes.csv',
    'busquedas_12_nodes.csv',
    'busquedas_15_nodes.csv',
    'busquedas_17_nodes.csv',
    'busquedas_20_nodes.csv'
]

node_counts = [7, 12, 15, 17, 20] 
average_times = []

for file_name in csv_files:
    file_path = os.path.join(csv_folder, file_name)
    try:
        df = pd.read_csv(file_path)
        average_time = df['tiempo_ms'].mean()
        average_times.append(average_time)
    except FileNotFoundError:
        print(f"Erro: Arquivo não encontrado em {file_path}")

n_log_n = [n * np.log2(n) for n in node_counts]

max_n_log_n = max(n_log_n)
max_average_times = max(average_times)

n_log_n_normalized = [ (x / max_n_log_n) * max_average_times for x in n_log_n]

plt.figure(figsize=(10, 6))
plt.plot(node_counts, average_times, marker='o', 
         linestyle='-', color='b', linewidth=2, 
         label='Tempo Promédio de Busca (ms)')
plt.plot(node_counts, n_log_n_normalized, marker='x', 
         linestyle='--', color='r', linewidth=1.5, 
         label='N log N (Normalizado)')

plt.title('Análise de Latência de Busca em Função da Escala (Chord)')
plt.xlabel('Número de Nodos (N)')
plt.ylabel('Tempo (ms)')
plt.xticks(node_counts)
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.savefig(os.path.join(csv_folder, 'search_time_vs_nlogn.png'))
plt.show()