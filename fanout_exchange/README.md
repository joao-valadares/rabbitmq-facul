# Fanout Exchange

## Descrição

O **Fanout Exchange** é um tipo de exchange que implementa o padrão de **broadcast** (difusão). Todas as mensagens enviadas para um Fanout Exchange são entregues para **todas as filas** que estão vinculadas a ele, independentemente da routing key.

### Como Funciona

1. O producer envia mensagens para o exchange (routing key é ignorada)
2. O exchange entrega a mensagem para **todas** as filas vinculadas
3. Cada consumer conectado a uma fila recebe uma cópia da mensagem

### Cenário Implementado

- **Producer**: Envia mensagens de broadcast para notificações globais
- **Consumer 1**: Processa notificações para interface de usuário
- **Consumer 2**: Registra logs de auditoria
- **Consumer 3**: Coleta métricas e estatísticas

## Arquitetura

```
Producer → Fanout Exchange → TODAS as filas → TODOS os consumers
                ↓
            broadcast → fanout_queue_notifications → Consumer 1
                    → fanout_queue_audit         → Consumer 2  
                    → fanout_queue_metrics       → Consumer 3
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
cd fanout_exchange
python producer.py

# Terminal 2 - Consumer Notificações
python consumer1.py

# Terminal 3 - Consumer Auditoria
python consumer2.py

# Terminal 4 - Consumer Métricas
python consumer3.py
```

## Comportamento Esperado

### Producer
- Envia mensagens de broadcast a cada 4 segundos
- Cada mensagem é entregue para **todos** os consumers
- Routing key é ignorada (pode ser vazia)

### Consumers
- **Consumer 1**: Processa notificações para UI (1s de processamento)
- **Consumer 2**: Registra auditoria (0.8s de processamento)
- **Consumer 3**: Coleta métricas (0.5s de processamento)
- **Todos** recebem a **mesma** mensagem

### Logs Esperados

```
ENVIADO → Exchange: fanout_exchange_demo | Routing Key: broadcast | Mensagem: {"id": 1, "type": "broadcast", ...
[NOTIFICATION_PROCESSOR] 📢 NOTIFICAÇÃO RECEBIDA - ID: 1
[AUDIT_LOGGER] 📝 REGISTRANDO AUDITORIA - ID: 1  
[METRICS_COLLECTOR] 📊 COLETANDO MÉTRICAS - ID: 1
```

## Características Técnicas

- **Exchange Type**: `fanout`
- **Routing Key**: Ignorada (pode ser vazia)
- **Broadcast**: Uma mensagem → múltiplos consumers
- **Durability**: Exchanges e filas são duráveis
- **Acknowledgments**: Confirmação manual
- **QoS**: `prefetch_count=1` para cada consumer

## Casos de Uso

### Notificações Globais
- Alertas de sistema para todos os usuários
- Atualizações de status
- Mensagens de manutenção

### Logging e Auditoria
- Registrar todas as ações em múltiplos sistemas
- Backup de logs
- Compliance e auditoria

### Monitoramento
- Métricas em tempo real
- Alertas para múltiplos sistemas de monitoramento
- Dashboard updates

### Cache Invalidation
- Invalidar cache em múltiplos servidores
- Atualização de configurações
- Sincronização de dados

## Vantagens

- **Simplicidade**: Não precisa gerenciar routing keys
- **Broadcast Real**: Garante que todos recebem a mensagem
- **Desacoplamento**: Producers não precisam saber quem são os consumers
- **Escalabilidade**: Fácil adicionar novos consumers

## Limitações

- **Sem Filtros**: Todos recebem todas as mensagens
- **Overhead**: Múltiplas cópias da mesma mensagem
- **Sem Roteamento**: Não há controle granular sobre quem recebe o quê

## Comparação com outros Exchanges

| Característica | Fanout | Direct | Topic |
|----------------|--------|--------|-------|
| Routing Key    | Ignorada | Exata | Padrão |
| Entrega        | Todas filas | Fila específica | Filas que batem padrão |
| Uso            | Broadcast | Roteamento direto | Roteamento flexível |
