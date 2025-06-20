# Round Robin Ponderado (Weighted)

## Descrição

O **Round Robin Ponderado** é uma evolução do round robin simples que considera as **diferentes capacidades** dos workers. Usando diferentes valores de `prefetch_count`, workers mais poderosos recebem mais tarefas simultaneamente.

### Como Funciona

1. Workers com maior capacidade configuram `prefetch_count` maior
2. RabbitMQ distribui mais mensagens para workers com maior prefetch
3. Balanceamento automático baseado na capacidade de processamento
4. Workers lentos não ficam sobrecarregados

### Cenário Implementado

- **Producer**: Envia tarefas com complexidades variadas
- **Worker Básico**: `prefetch=1` (1 tarefa simultânea)
- **Worker Médio**: `prefetch=3` (3 tarefas simultâneas) + 15% mais rápido
- **Worker Avançado**: `prefetch=5` (5 tarefas simultâneas) + 30% mais rápido + modo TURBO

## Arquitetura

```
Producer → Fila Compartilhada → Workers com Capacidades Diferentes
              ↓
         Work Queue  → Worker Básico    (prefetch=1, velocidade 100%)
                    → Worker Médio     (prefetch=3, velocidade 115%)
                    → Worker Avançado  (prefetch=5, velocidade 130%+)
```

## Distribuição de Carga

### Baseada em Capacidade
```
Worker Básico:    ▓           (1 tarefa)
Worker Médio:     ▓▓▓         (3 tarefas)
Worker Avançado:  ▓▓▓▓▓       (5 tarefas)
```

### Throughput Esperado
- **Worker Básico**: ~1 tarefa/minuto (baseline)
- **Worker Médio**: ~4-5 tarefas/minuto (3x prefetch + 15% velocidade)
- **Worker Avançado**: ~8-10 tarefas/minuto (5x prefetch + 30% velocidade)

## Como Executar

### Pré-requisitos
```powershell
pip install pika python-dotenv
```

### Configurar Variáveis de Ambiente
```powershell
# Windows PowerShell
$env:RABBITMQ_HOST="localhost"
$env:RABBITMQ_PORT="5672"
$env:RABBITMQ_USER="guest"
$env:RABBITMQ_PASSWORD="guest"
```

### Executar Componentes

**Em terminais separados (ou VMs diferentes):**

```powershell
# Terminal 1 - Producer
cd round_robin_weighted
python producer.py

# Terminal 2 - Worker Básico
python consumer1.py

# Terminal 3 - Worker Médio  
python consumer2.py

# Terminal 4 - Worker Avançado
python consumer3.py
```

## Comportamento Esperado

### Producer
- Envia tarefas com diferentes complexidades
- Tipos: `quick_task`, `medium_task`, `complex_task`, `batch_job`, `heavy_processing`
- Tempo de processamento: 1-5 segundos

### Workers

#### Worker Básico (prefetch=1)
- Processa 1 tarefa por vez
- Velocidade padrão (100%)
- Adequado para recursos limitados

#### Worker Médio (prefetch=3)
- Processa até 3 tarefas simultaneamente
- 15% mais rápido que o básico
- Balanceamento moderado

#### Worker Avançado (prefetch=5)
- Processa até 5 tarefas simultaneamente  
- 30% mais rápido que o básico
- Modo TURBO para tarefas complexas (ainda mais rápido)

### Logs Esperados

```
# Worker Básico
[BASIC_WORKER] Tarefas em progresso: 1/1

# Worker Médio
[MEDIUM_WORKER] Tarefas em progresso: 3/3
[MEDIUM_WORKER] Progresso otimizado: 100%

# Worker Avançado
[ADVANCED_WORKER] Tarefas em progresso: 5/5
[ADVANCED_WORKER] Modo TURBO ativado para tarefa complexa!
[ADVANCED_WORKER] Eficiência: 30% mais rápido
```

## Características Técnicas

### Configuração de Prefetch
```python
# Worker Básico
channel.basic_qos(prefetch_count=1)

# Worker Médio  
channel.basic_qos(prefetch_count=3)

# Worker Avançado
channel.basic_qos(prefetch_count=5)
```

### Acknowledgments
- **Manual**: Garante que tarefas não são perdidas
- **Requeue**: Em caso de erro, tarefa volta para a fila

### Durability
- Fila e mensagens são duráveis
- Sobrevive a reinicializações do RabbitMQ

## Casos de Uso

### Data Centers Heterogêneos
```python
# Servidores com capacidades diferentes
old_server: prefetch=1    # Hardware antigo
new_server: prefetch=5    # Hardware moderno
cloud_instance: prefetch=10  # Instância escalável
```

### Processamento de Mídia
```python
# Baseado em recursos de GPU/CPU
cpu_only: prefetch=1      # Sem aceleração
gpu_basic: prefetch=3     # GPU básica
gpu_high_end: prefetch=8  # GPU profissional
```

### Microserviços
```python
# Instâncias com recursos diferentes
micro_instance: prefetch=1   # 1 CPU, 1GB RAM
small_instance: prefetch=3   # 2 CPU, 4GB RAM  
large_instance: prefetch=8   # 8 CPU, 16GB RAM
```

### Machine Learning
```python
# Baseado em capacidade de modelo
inference_cpu: prefetch=1    # CPU inference
inference_gpu: prefetch=5    # GPU inference
training_cluster: prefetch=20 # Cluster dedicado
```

## Vantagens

- **Eficiência Máxima**: Workers poderosos são melhor utilizados
- **Prevenção de Gargalos**: Workers lentos não limitam o sistema
- **Adaptabilidade**: Fácil ajustar capacidades conforme recursos
- **Auto-balanceamento**: Distribuição automática baseada em capacidade

## Limitações

- **Complexidade de Configuração**: Precisa conhecer capacidade dos workers
- **Monitoramento**: Mais difícil acompanhar performance individual
- **Memory Usage**: Workers com alto prefetch usam mais memória

## Configurações Recomendadas

### Por Tipo de Hardware

#### Hardware Limitado
```python
prefetch_count = 1
# Garante estabilidade e não sobrecarrega
```

#### Hardware Padrão
```python
prefetch_count = 2-4
# Balanceamento entre throughput e estabilidade
```

#### Hardware Avançado
```python
prefetch_count = 5-10
# Maximiza utilização de recursos
```

#### Clusters/Cloud
```python
prefetch_count = 10-50
# Baseado em auto-scaling e disponibilidade
```

### Por Tipo de Tarefa

#### I/O Intensivo
```python
prefetch_count = 10-20
# Tarefas de rede/disco podem ser paralelizadas
```

#### CPU Intensivo
```python
prefetch_count = num_cores
# Uma tarefa por core disponível
```

#### Memory Intensivo
```python
prefetch_count = 1-2
# Evita problemas de memória
```

## Monitoramento

### Métricas Importantes
- **Queue Depth**: Profundidade da fila
- **Consumer Utilization**: % de uso de cada worker
- **Processing Rate**: Taxa de processamento por worker
- **Unacked Messages**: Mensagens em processamento por worker

### Alertas Recomendados
```python
# Worker sobrecarregado
if unacked_messages > prefetch_count * 0.8:
    alert("Worker próximo do limite")

# Worker ocioso
if processing_rate < expected_rate * 0.5:
    alert("Worker subutilizado")

# Fila crescendo
if queue_depth > threshold:
    scale_up_workers()
```

## Otimização

### Ajuste Dinâmico
```python
# Baseado em performance
if avg_processing_time < target:
    increase_prefetch()
elif error_rate > threshold:
    decrease_prefetch()
```

### A/B Testing
```python
# Teste diferentes configurações
group_a_prefetch = 3
group_b_prefetch = 5
# Meça throughput e latência
```

### Auto-scaling
```python
# Baseado em carga
if queue_depth > 100:
    spawn_new_worker(prefetch=optimal_prefetch)
elif queue_depth < 10:
    terminate_excess_workers()
```
