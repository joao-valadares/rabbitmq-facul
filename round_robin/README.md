# Round Robin

## Descrição

O **Round Robin** é um padrão de balanceamento de carga onde múltiplos workers (consumers) compartilham uma única fila de trabalho. As tarefas são distribuídas de forma equitativa entre os workers disponíveis.

### Como Funciona

1. Producer envia tarefas para uma fila compartilhada
2. Múltiplos workers conectam-se à mesma fila
3. RabbitMQ distribui as mensagens de forma circular entre os workers
4. Cada tarefa é processada por apenas um worker

### Fair Dispatch

Usando `prefetch_count=1`, garantimos que cada worker processe apenas uma tarefa por vez, evitando sobrecarga de workers lentos.

### Cenário Implementado

- **Producer**: Envia diferentes tipos de tarefas com complexidades variadas
- **Worker 1**: Processa tarefas no tempo normal
- **Worker 2**: Processa tarefas 10% mais rápido (otimizado)
- **Worker 3**: Processa tarefas 10% mais lento (mais detalhado)

## Arquitetura

```
Producer → Fila Compartilhada → Workers em Round Robin
              ↓
         Work Queue  → Worker 1 (tarefa 1, 4, 7...)
                    → Worker 2 (tarefa 2, 5, 8...)
                    → Worker 3 (tarefa 3, 6, 9...)
```

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
cd round_robin
python producer.py

# Terminal 2 - Worker 1
python consumer1.py

# Terminal 3 - Worker 2
python consumer2.py

# Terminal 4 - Worker 3
python consumer3.py
```

## Comportamento Esperado

### Producer
- Envia tarefas continuamente para a fila
- Diferentes tipos: `image_processing`, `data_analysis`, `report_generation`, etc.
- Cada tarefa tem tempo estimado de processamento

### Workers
- **Worker 1**: Velocidade normal, logs padrão
- **Worker 2**: 10% mais rápido, processamento otimizado
- **Worker 3**: 10% mais lento, processamento detalhado com percentual
- Cada worker pega uma tarefa por vez (fair dispatch)

### Distribuição
```
Tarefa 1 → Worker 1
Tarefa 2 → Worker 2  
Tarefa 3 → Worker 3
Tarefa 4 → Worker 1
Tarefa 5 → Worker 2
...
```

### Logs Esperados

```
# Producer
Tarefa #1 (image_processing) enviada - Tempo estimado: 3s

# Worker 1
[WORKER_1] 🔧 PROCESSANDO TAREFA #1
[WORKER_1] 📊 Progresso: 1/3s
[WORKER_1] ✅ Tarefa #1 concluída com sucesso!

# Worker 2  
[WORKER_2] 🔧 PROCESSANDO TAREFA #2
[WORKER_2] ✅ Tarefa #2 concluída rapidamente!
```

## Características Técnicas

- **Exchange**: Padrão (default) - usa routing key = nome da fila
- **QoS**: `prefetch_count=1` (fair dispatch)
- **Acknowledgments**: Manual para garantir processamento
- **Durability**: Fila e mensagens são duráveis
- **Distribuição**: Automática pelo RabbitMQ

## Casos de Uso

### Processamento de Imagens
```python
# Tarefas: redimensionar, filtros, conversão
# Workers: servidores com GPUs diferentes
# Distribuição: automática conforme disponibilidade
```

### Análise de Dados
```python
# Tarefas: ETL, relatórios, machine learning
# Workers: servidores com capacidades diferentes  
# Distribuição: baseada em velocidade de processamento
```

### Envio de Emails
```python
# Tarefas: emails promocionais, notificações
# Workers: servidores SMTP diferentes
# Distribuição: para balancear carga dos servidores
```

### Backup de Arquivos
```python
# Tarefas: backup de diferentes diretórios
# Workers: servidores com acesso a storage
# Distribuição: conforme disponibilidade de recursos
```

## Vantagens

- **Balanceamento Automático**: RabbitMQ distribui automaticamente
- **Escalabilidade**: Fácil adicionar/remover workers
- **Fault Tolerance**: Se um worker falha, outros continuam
- **Fair Dispatch**: Evita sobrecarga de workers lentos

## Limitações

- **Sem Priorização**: Todas as tarefas têm mesma prioridade
- **Sem Afinidade**: Tarefas não podem ser direcionadas a workers específicos
- **Single Point**: Uma fila para todas as tarefas

## Configurações Importantes

### Fair Dispatch (Recomendado)
```python
# Cada worker pega apenas uma tarefa por vez
channel.basic_qos(prefetch_count=1)
```

### Unfair Dispatch (NÃO recomendado)
```python
# Workers podem acumular tarefas (pode sobrecarregar workers lentos)
# Não usar prefetch_count ou usar valor alto
```

### Acknowledgments
```python
# Manual (recomendado) - tarefa só sai da fila após confirmação
auto_ack=False
ch.basic_ack(delivery_tag=method.delivery_tag)

# Automático (risco) - tarefa sai da fila imediatamente  
auto_ack=True
```

## Monitoramento

### Métricas Importantes
- **Queue Depth**: Quantas tarefas estão na fila
- **Consumer Count**: Quantos workers estão ativos
- **Message Rate**: Taxa de processamento
- **Unacked Messages**: Tarefas em processamento

### Via RabbitMQ Management
```
http://localhost:15672
- Queues → round_robin_work_queue
- Ver: Messages, Consumers, Message rates
```

### Via Logs
```python
# Cada worker reporta:
# - Tarefas processadas
# - Tempo de processamento
# - Status de cada tarefa
```

## Escalabilidade

### Adicionar Workers
```powershell
# Simplesmente execute mais consumers
python consumer1.py  # Em nova VM/container
python consumer2.py  # Em nova VM/container
```

### Remover Workers
```powershell
# Pare o consumer (Ctrl+C)
# Tarefas em processamento serão requeued
# Outros workers assumem automaticamente
```

### Auto-scaling
```python
# Baseado na profundidade da fila
if queue_depth > 100:
    start_new_worker()
elif queue_depth < 10:
    stop_worker()
```

## Comparação com outros Padrões

| Padrão | Distribuição | Casos de Uso | Complexidade |
|--------|--------------|--------------|--------------|
| Round Robin | Equitativa | Workers homogêneos | Baixa |
| Weighted Round Robin | Baseada em capacidade | Workers heterogêneos | Média |
| Priority Queue | Por prioridade | Tarefas críticas | Média |
| Topic Routing | Por tipo/categoria | Especialização | Alta |
