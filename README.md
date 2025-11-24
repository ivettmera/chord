# Chord DHT
Uma tabela de espalhamento distribuída (DHT) usando o protocolo de lookup Chord, implementada em Go.

## Objetivos
- Implementar uma DHT funcional com tolerancia a falhas de nós caídos
- Implementar o protocolo Chord para lookup eficiente de nós fisicos em diferentes regioes 
- Estender o Chord com replicação de dados para aumentar a disponibilidade
- Fazer testes de rendimento
- Aprender gRPC e protocol buffers

## Modificacoes
O node.go foi modificado para ter en cuenta a latencia de regioes longas e evitar a condicao de carrera. Tambem se implemento o join de n nós apos da conexao do nó físico para automatizar o levantamento de n nós locais.

## Pré-requisitos
É necessário ter o Go na versão 1.24 ou superior instalado na máquina para construir o projeto.

## Compilação
Para compilar o servidor e o cliente do chord, execute:
```
make server
make client
```
 # Chord DHT
Uma tabela de dispersão distribuída (DHT) usando o protocolo de lookup Chord, implementada em Go.


## Objetivos

- Implementar uma DHT funcional com tolerância a falhas (nós que caem/reiniciam).
- Implementar o protocolo Chord para lookup eficiente de nós físicos em diferentes regiões.
- Estender o Chord com replicação de dados para aumentar a disponibilidade.
- Realizar testes de desempenho e coletar métricas.
- Aprender e usar gRPC e Protocol Buffers para comunicação RPC.

## Modificações recentes

- `node.go` foi ajustado para considerar a latência entre regiões e reduzir condições de corrida.
- Implementado procedimento para criar múltiplos nós lógicos em um nó físico (script em `experiments/`) para facilitar testes locais.

## Pré-requisitos

- Go 1.24 ou superior instalado.
- `make` disponível (para executar `make server` / `make client`).

## Compilação

Para compilar o servidor e o cliente, execute:

```bash
make server
make client
```

Após a compilação os executáveis `chord` serão criados nas pastas `server/` e `client/`.

No Windows PowerShell, após compilar, você pode executar os binários com:

```powershell
.\server\chord.exe create
.\client\chord.exe put <key> <val>
```

Se preferir rodar sem compilar (apenas para testes):

```bash
go run server/main.go -- <args>
go run client/main.go -- <args>
```

## Configuração

### Servidor

Edite `./server/config.yaml` com as informações do servidor (IP, porta, logging). Exemplo:

```yaml
addr: 172.0.0.1
port: 8001
logging: false
```

Observação sobre redes: se for usar nós físicos em diferentes regiões na mesma VPC, prefira IPs internos para tráfego entre nós; para clientes externos use o IP público/externo do servidor que atua como ponto de entrada.

### Cliente

Edite `./client/config.yaml` com o endereço do servidor Chord a receber as requisições. Exemplo:

```yaml
addr: 34.58.253.117:8001
```

## Execução

### Servidor

Criar um novo anel Chord (no nó inicial):

```bash
./server/chord create
```

Entrar em um anel existente (informe IP e porta de um nó do anel):

```bash
./server/chord join <ip> <port>
```

Para levantar múltiplos nós lógicos em um mesmo nó físico (útil para testes locais), use o script `experiments/n_nodes.sh`. Exemplo:

```bash
./experiments/n_nodes.sh -n <numero_de_nos> -i <ip_do_host> -p <porta_inicial>
```

> O script cria várias instâncias locais variando portas a partir de `<porta_inicial>`.

### Cliente

Inserir um par chave-valor na DHT:

```bash
./client/chord put <key> <val>
```

Obter o valor associado a uma chave:

```bash
./client/chord get <key>
```

Localizar (debug) o nó responsável por uma chave:

```bash
./client/chord locate <key>
```

## Desenvolvimento local e testes

Scripts úteis em `experiments/`:

- `n_nodes.sh`: levanta `n` nós locais em portas sequenciais.
- `make_keys.sh`: gera e insere várias chaves no sistema para testes de carga.
- `client_test.sh`: realiza `k` consultas `get` em um anel com `n` nós e grava tempos de resposta em CSV (em `experiments/csv/`).

## Métricas e resultados

- Os scripts de teste coletam tempos de resposta por consulta e exportam para CSV em `experiments/csv/`.
- Métrica básica usada: tempo médio de resposta para 10 buscas aleatórias (média utilizada para confirmar comportamento esperado de complexidade O(log n) em buscas).

## Soluções e troubleshooting

- Se o nó falhar ao entrar no anel, verifique `./server/config.yaml` (IP/porta) e se a porta está livre.
- Para problemas de rede entre regiões, confirme regras de firewall/VPC e se o tráfego interno usa IPs privados.
- Se observar condições de corrida em ambiente de alta latência, aumentar tempos de retry/timeouts no `config.yaml` e garantir ordenação de operações de join/replicação.
- Para testes com muitos nós (>20), assegure recursos de VM (memória/CPU) suficientes; é recomendado usar múltiplas VMs ou containers para simular latência de rede real.

## Conclusões

- A implementação suporta realocação de responsabilidades quando nós saem do anel.
- Recomenda-se máquinas com memória e CPU adequadas para levantar >20 nós simultâneos.
- Testes em rede real mostram latências maiores que testes locais

## Localização dos arquivos importantes

- Código principal: `node.go`, `server/`, `client/`.
- Scripts de experimento: `experiments/`.
- Protobufs/gRPC: `chordpb/`.
