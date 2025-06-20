# Priority Queue - Filas com Prioridade

## 📋 Descrição
Este cenário demonstra o uso de filas com prioridade no RabbitMQ, onde mensagens com maior prioridade são processadas antes das de menor prioridade, permitindo sistemas mais responsivos para eventos críticos.

## 🎯 Objetivos de Aprendizagem
- Implementar filas com sistema de prioridades (0-10)
- Compreender como prioridades afetam a ordem de processamento
- Demonstrar diferentes estratégias de processamento por prioridade
- Analisar impacto de prioridades no tempo de resposta

## 🏗️ Arquitetura

```
Producer → [priority_queue (x-max-priority: 10)] → Consumer1 (Alertas Críticos)
                                                 → Consumer2 (Operações Gerais)  
                                                 → Consumer3 (Processamento em Lote)
```

## 🎚️ Sistema de Prioridades

### Escala de Prioridades (0-10)
- **10**: 🚨 **CRITICAL** - Falhas críticas do sistema
- **9**: 🚨 **CRITICAL** - Violações de segurança
- **7**: ⚠️ **ERROR** - Erros de aplicação
- **5**: 🟡 **WARNING** - Avisos e alertas
- **3**: ℹ️ **INFO** - Logs informativos
- **1**: 🔍 **DEBUG** - Logs de debug
- **0**: 🔍 **DEBUG** - Processamento em lote

## 🔧 Componentes

### Producer (`producer.py`)
- Gera mensagens com diferentes tipos e prioridades
- Simula eventos reais: alertas críticos, violações de segurança, logs
- Distribui mensagens aleatoriamente para demonstrar priorização

### Consumer1 (`consumer1.py`) - Alertas Críticos
- **Foco**: Mensagens de alta prioridade (7-10)
- **Estratégia**: Processamento ultra-rápido para críticos
- **Capacidade**: 1 mensagem por vez (precisão)

### Consumer2 (`consumer2.py`) - Operações Gerais
- **Foco**: Processamento balanceado de todas as prioridades
- **Estratégia**: Tempo de processamento baseado na prioridade
- **Capacidade**: 2 mensagens simultâneas (equilibrio)

### Consumer3 (`consumer3.py`) - Processamento em Lote
- **Foco**: Tarefas de baixa prioridade e processamento em lote
- **Estratégia**: Otimizado para throughput e eficiência
- **Capacidade**: 3 mensagens simultâneas (volume)

## ⚙️ Configurações

### Variáveis de Ambiente
- `RABBITMQ_HOST`: Servidor RabbitMQ (padrão: localhost)
- `RABBITMQ_PORT`: Porta RabbitMQ (padrão: 5672)
- `RABBITMQ_USER`: Usuário (padrão: guest)
- `RABBITMQ_PASS`: Senha (padrão: guest)
- `LOG_LEVEL`: Nível de log (padrão: INFO)

### Fila
- **priority_queue**: Fila com `x-max-priority: 10`

## 🚀 Execução

### 1. Terminal 1 - Consumer Alertas Críticos
```bash
cd priority
python consumer1.py
```

### 2. Terminal 2 - Consumer Operações Gerais
```bash
cd priority
python consumer2.py
```

### 3. Terminal 3 - Consumer Processamento em Lote
```bash
cd priority
python consumer3.py
```

### 4. Terminal 4 - Producer
```bash
cd priority
python producer.py
```

## 📊 Teste de Prioridades

### Demonstrando Ordem de Processamento
1. **Envio em lote**: Execute o producer por 30 segundos
2. **Pare o producer**: Ctrl+C para acumular mensagens na fila
3. **Observe processamento**: Mensagens de alta prioridade são processadas primeiro
4. **Análise**: Verifique logs de tempo de espera

### Teste de Sobrecarga
1. **Execute apenas Consumer3** (lote)
2. **Envie muitas mensagens** de diferentes prioridades
3. **Inicie Consumer1** (críticos)
4. **Observe**: Consumer1 pega imediatamente mensagens críticas

## 📈 Métricas Observadas

### Tempo de Processamento por Prioridade

| Prioridade | Consumer1 | Consumer2 | Consumer3 |
|------------|-----------|-----------|-----------|
| 10 (CRIT)  | 0.1-0.3s  | 0.2-0.5s  | 0.1s      |
| 7-9 (ERR)  | 0.3-0.7s  | 0.4-1.0s  | 0.3s      |
| 5-6 (WARN) | 0.5-1.0s  | 0.8-1.5s  | 0.4s      |
| 1-4 (INFO) | 1.0-2.0s  | 1.0-2.5s  | 0.6-0.8s  |
| 0 (BATCH)  | 1.0-2.0s  | 2.0-3.0s  | 2.0s      |

### Estratégias de Processamento

#### Consumer1 - Especialista em Críticos
- ✅ **Velocidade**: Máxima para mensagens críticas
- ✅ **Precisão**: Processamento dedicado e cuidadoso
- ⚠️ **Volume**: Menor throughput total

#### Consumer2 - Balanceado
- ✅ **Flexibilidade**: Processa todos os tipos
- ✅ **Eficiência**: Boa relação velocidade/qualidade
- ✅ **Adaptabilidade**: Ajusta tempo por prioridade

#### Consumer3 - Alto Volume
- ✅ **Throughput**: Maior volume de mensagens processadas
- ✅ **Eficiência**: Otimizado para recursos computacionais
- ✅ **Lote**: Especializado em processamento em massa

## 🔄 Casos de Uso Demonstrados

### 1. Sistema de Monitoramento
```
Prioridade 10: Falha crítica de servidor
Prioridade 7:  Erro de aplicação
Prioridade 3:  Log de acesso normal
Prioridade 0:  Processamento de relatórios
```

### 2. Sistema de Segurança
```
Prioridade 9:  Tentativa de invasão
Prioridade 7:  Login suspeito
Prioridade 5:  Mudança de configuração
Prioridade 1:  Auditoria de rotina
```

### 3. Sistema de E-commerce
```
Prioridade 10: Falha no pagamento
Prioridade 8:  Estoque zerado
Prioridade 5:  Carrinho abandonado
Prioridade 0:  Análise de vendas
```

## 🎓 Conceitos Demonstrados

### 1. **Declaração de Fila com Prioridade**
```python
channel.queue_declare(
    queue='priority_queue',
    durable=True,
    arguments={'x-max-priority': 10}  # Prioridade máxima
)
```

### 2. **Envio com Prioridade**
```python
channel.basic_publish(
    exchange='',
    routing_key='priority_queue',
    body=message,
    properties=pika.BasicProperties(
        priority=message_priority,  # 0-10
        delivery_mode=2  # Persistente
    )
)
```

### 3. **Processamento Inteligente**
```python
def get_processing_time(priority):
    if priority >= 9:
        return 0.1  # Crítico - muito rápido
    elif priority >= 7:
        return 0.5  # Erro - rápido
    elif priority >= 5:
        return 1.0  # Warning - normal
    else:
        return 2.0  # Info/Debug - mais lento
```

## 🔍 Monitoramento

### Comandos úteis
```bash
# Ver mensagens por prioridade
sudo rabbitmqctl list_queues name messages_ready

# Monitorar consumers
sudo rabbitmqctl list_consumers

# Ver detalhes da fila
sudo rabbitmqctl list_queue_details priority_queue
```

### Logs Importantes
- Tempo de espera por prioridade
- Ordem de processamento
- Distribuição de carga entre consumers
- Eficiência por tipo de mensagem

## 🎯 Cenários de Teste

### Teste 1: Ordem de Prioridade
1. Envie 20 mensagens de diferentes prioridades
2. Pare o producer
3. Observe a ordem de processamento
4. Verifique se altas prioridades vêm primeiro

### Teste 2: Balanceamento por Especialização
1. Execute todos os consumers
2. Envie mix de mensagens
3. Observe qual consumer pega quais tipos
4. Analise eficiência por especialização

### Teste 3: Recuperação de Emergência
1. Acumule muitas mensagens de baixa prioridade
2. Envie algumas mensagens críticas
3. Observe como críticas "passam na frente"
4. Meça tempo de resposta para críticas

## 📚 Configurações Avançadas

### Otimização de Performance
```python
# Consumer otimizado para alta prioridade
channel.basic_qos(prefetch_count=1)  # Precisão

# Consumer otimizado para volume
channel.basic_qos(prefetch_count=5)  # Throughput
```

### Monitoramento de SLA
```python
# Tracking de tempo de resposta por prioridade
if priority >= 9:
    sla_target = 1.0  # 1 segundo para críticos
elif priority >= 7:
    sla_target = 5.0  # 5 segundos para erros
else:
    sla_target = 30.0  # 30 segundos para outros
```

## 🎯 Melhores Práticas

### 1. **Design de Prioridades**
- Use poucos níveis (3-5) para evitar complexidade
- Reserve prioridade máxima (10) para emergências
- Documente claramente critérios de prioridade

### 2. **Balanceamento de Consumers**
- Especialização por tipo de mensagem
- Capacidade ajustada à criticidade
- Monitoramento de SLA por prioridade

### 3. **Prevenção de Starvation**
- Limite tempo máximo de espera
- Consumers dedicados para baixa prioridade
- Escalamento baseado em backlog

## 📚 Referências
- [RabbitMQ Priority Queues](https://www.rabbitmq.com/priority.html)
- [Queue Arguments](https://www.rabbitmq.com/queues.html#optional-arguments)
- [Message Properties](https://www.rabbitmq.com/publishers.html#message-properties)
