# Direct Exchange

## Descrição

O **Direct Exchange** é um tipo de exchange que roteia mensagens baseado em uma correspondência exata entre a routing key da mensagem e a routing key do binding da fila.

### Como Funciona

1. O producer envia mensagens para o exchange com uma routing key específica
2. O exchange verifica qual fila está vinculada (bind) com essa routing key exata
3. A mensagem é entregue apenas para a fila que tem binding com a routing key correspondente

### Cenário Implementado

- **Producer**: Envia mensagens com routing keys `info`, `warning`, e `error`
- **Consumer 1**: Consome apenas mensagens com routing key `info`
- **Consumer 2**: Consome apenas mensagens com routing key `warning`  
- **Consumer 3**: Consome apenas mensagens com routing key `error`

## Arquitetura

```
Producer → Direct Exchange → Filas específicas → Consumers específicos
                ↓
     info  → direct_queue_info    → Consumer 1
     warning → direct_queue_warning → Consumer 2
     error → direct_queue_error   → Consumer 3
```

## Como Executar

### Pré-requisitos
```bash
pip install pika python-dotenv
```

### Configurar Variáveis de Ambiente
```bash
# Windows PowerShell
$env:RABBITMQ_HOST="localhost"
$env:RABBITMQ_PORT="5672"
$env:RABBITMQ_USER="guest"
$env:RABBITMQ_PASSWORD="guest"

# Linux/Mac
export RABBITMQ_HOST=localhost
export RABBITMQ_PORT=5672
export RABBITMQ_USER=guest
export RABBITMQ_PASSWORD=guest
```

### Executar Componentes

**Em terminais separados (ou VMs diferentes):**

```bash
# Terminal 1 - Producer
cd direct_exchange
python producer.py

# Terminal 2 - Consumer INFO
python consumer1.py

# Terminal 3 - Consumer WARNING  
python consumer2.py

# Terminal 4 - Consumer ERROR
python consumer3.py
```

## Comportamento Esperado

### Producer
- Envia mensagens ciclicamente com routing keys `info`, `warning`, `error`
- Cada mensagem contém timestamp e dados JSON
- Mensagens são persistentes (delivery_mode=2)

### Consumers
- **Consumer 1**: Recebe apenas mensagens `info`
- **Consumer 2**: Recebe apenas mensagens `warning` (processa mais lentamente)
- **Consumer 3**: Recebe apenas mensagens `error` (processa rapidamente)

### Logs Esperados

```
ENVIADO → Exchange: direct_exchange_demo | Routing Key: info | Mensagem: {"id": 1, "type": "info", ...
RECEBIDO [INFO_CONSUMER] ← Exchange: direct_exchange_demo | Routing Key: info | Mensagem: {"id": 1, ...
```

## Características Técnicas

- **Exchange Type**: `direct`
- **Durability**: Exchanges e filas são duráveis
- **Acknowledgments**: Confirmação manual para garantir processamento
- **QoS**: `prefetch_count=1` para processamento sequencial
- **Routing**: Baseado em correspondência exata da routing key

## Casos de Uso

- **Logs por Severidade**: Diferentes níveis de log para diferentes processadores
- **Tarefas por Tipo**: Diferentes tipos de trabalho para workers especializados
- **Notificações por Canal**: SMS, email, push notifications
- **Processamento por Prioridade**: Crítico, normal, baixa prioridade

## Vantagens

- Roteamento preciso e controlado
- Isolamento de responsabilidades
- Fácil scaling por tipo de mensagem
- Processamento especializado

## Limitações

- Routing key deve ser exata (sem wildcards)
- Não suporta roteamento baseado em padrões
- Requer conhecimento prévio das routing keys
