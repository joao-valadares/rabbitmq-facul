# Persistence (Persistência)

## Descrição

O cenário de **Persistence** demonstra a diferença entre mensagens **persistentes** e **transientes** no RabbitMQ. Esta é uma característica crucial para sistemas que precisam de diferentes níveis de garantia de entrega.

### Tipos de Persistência

#### Mensagens Persistentes (delivery_mode=2)
- Armazenadas em disco pelo RabbitMQ
- Sobrevivem a reinicializações do broker
- Maior overhead de performance
- Adequadas para dados críticos

#### Mensagens Transientes (delivery_mode=1)
- Mantidas apenas em memória
- Perdidas se o broker reiniciar
- Performance otimizada
- Adequadas para dados temporários

### Cenário Implementado

- **Producer**: Alterna entre mensagens persistentes e transientes
- **Consumer 1**: Processa mensagens **persistentes** (críticas)
- **Consumer 2**: Processa mensagens **transientes** (otimizadas)
- **Consumer 3**: Monitor que compara performance de ambos os tipos

## Arquitetura

```
Producer → Filas com Diferentes Persistências → Consumers Especializados
     ↓
Persistentes → persistent_messages_queue (durable=True)  → Consumer 1
Transientes  → transient_messages_queue (durable=False) → Consumer 2
Ambas        → Monitor de Performance                   → Consumer 3
```

## Como Executar

### Pré-requisitos
```powershell
pip install pika python-dotenv
```

### Configurar Variáveis de Ambiente
```powershell
$env:RABBITMQ_HOST="localhost"
$env:RABBITMQ_PORT="5672"
$env:RABBITMQ_USER="guest"
$env:RABBITMQ_PASSWORD="guest"
```

### Executar Componentes

**Em terminais separados (ou VMs diferentes):**

```powershell
# Terminal 1 - Producer
cd persistence
python producer.py

# Terminal 2 - Consumer Persistente
python consumer1.py

# Terminal 3 - Consumer Transiente
python consumer2.py

# Terminal 4 - Monitor de Performance
python consumer3.py
```

## Comportamento Esperado

### Producer
- Alterna entre mensagens persistentes (ímpares) e transientes (pares)
- Mensagens persistentes: `delivery_mode=2`
- Mensagens transientes: `delivery_mode=1`

### Consumers
- **Consumer 1**: Processamento seguro e completo (1.5s + auditoria)
- **Consumer 2**: Processamento rápido e otimizado (0.5s)
- **Consumer 3**: Coleta estatísticas de performance

### Logs Esperados

```
# Producer
💾 PERSISTENTE #1: Armazenada em disco, sobrevive a reinicializações
⚡ TRANSIENTE #2: Apenas em memória, performance otimizada

# Consumer 1 (Persistente)
[PERSISTENT_PROCESSOR] 💾 PROCESSANDO MENSAGEM PERSISTENTE #1
[PERSISTENT_PROCESSOR] 🔒 Iniciando processamento CRÍTICO...
[PERSISTENT_PROCESSOR] 🛡️ Dados críticos preservados

# Consumer 2 (Transiente)
[TRANSIENT_PROCESSOR] ⚡ PROCESSANDO MENSAGEM TRANSIENTE #2
[TRANSIENT_PROCESSOR] 🚀 Iniciando processamento RÁPIDO...
[TRANSIENT_PROCESSOR] 🏃 Performance otimizada
```

## Teste de Persistência

### Como Testar
1. Execute o producer por alguns minutos
2. Pare todos os consumers (mas deixe mensagens na fila)
3. **Reinicie o RabbitMQ**:
   ```powershell
   # Docker
   docker restart rabbitmq-server
   
   # Serviço Windows
   Restart-Service RabbitMQ
   ```
4. Execute os consumers novamente
5. **Observe**: Apenas mensagens PERSISTENTES permanecem na fila

### Resultado Esperado
- Fila `persistent_messages_queue`: Mensagens permanecem
- Fila `transient_messages_queue`: Fila é perdida ou vazia

## Características Técnicas

### Configuração de Fila

#### Fila Persistente
```python
channel.queue_declare(
    queue="persistent_messages_queue",
    durable=True  # Sobrevive a reinicializações
)
```

#### Fila Transiente
```python
channel.queue_declare(
    queue="transient_messages_queue", 
    durable=False  # Perdida se broker reiniciar
)
```

### Configuração de Mensagem

#### Mensagem Persistente
```python
properties = pika.BasicProperties(
    delivery_mode=2  # Persistente - armazenada em disco
)
```

#### Mensagem Transiente
```python
properties = pika.BasicProperties(
    delivery_mode=1  # Transiente - apenas em memória
)
```

## Casos de Uso

### Mensagens Persistentes
- **Transações financeiras**: Não podem ser perdidas
- **Pedidos de e-commerce**: Dados críticos do negócio
- **Logs de auditoria**: Requeridos por compliance
- **Backup/Recovery**: Operações de restauração
- **Notificações críticas**: SMS, emails importantes

### Mensagens Transientes
- **Cache updates**: Invalidação de cache
- **Métricas em tempo real**: Dados temporários
- **Heartbeats**: Verificações de saúde
- **Preview/Thumbnail**: Conteúdo temporário
- **Session data**: Dados de sessão web

## Performance

### Overhead de Persistência

| Tipo | Latência | Throughput | Uso de Disco | Caso de Uso |
|------|----------|------------|--------------|-------------|
| Persistente | Alta | Baixo | Alto | Dados críticos |
| Transiente | Baixa | Alto | Baixo | Dados temporários |

### Métricas Esperadas
- **Persistente**: ~1.5-3x mais lento que transiente
- **Transiente**: ~2-5x maior throughput
- **Disco**: Persistente usa storage, transiente apenas RAM

## Configurações Avançadas

### Lazy Queues (Recomendado para Persistência)
```python
# Para filas com muitas mensagens persistentes
channel.queue_declare(
    queue="large_persistent_queue",
    durable=True,
    arguments={"x-queue-mode": "lazy"}
)
```

### TTL (Time To Live)
```python
# Mensagens expiram após tempo determinado
properties = pika.BasicProperties(
    delivery_mode=2,
    expiration="60000"  # 60 segundos
)
```

### Confirmação de Publicação
```python
# Para garantir que mensagens persistentes foram escritas em disco
channel.confirm_delivery()
if channel.basic_publish(...):
    print("Mensagem confirmada como persistida")
```

## Monitoramento

### Via RabbitMQ Management
```
http://localhost:15672
- Queues → persistent_messages_queue
- Ver: Durable=True, Messages persistent/transient
```

### Métricas Importantes
- **Message rates**: Comparar throughput
- **Queue length**: Acúmulo de mensagens
- **Disk space**: Uso por mensagens persistentes
- **Memory usage**: Mensagens transientes em RAM

## Melhores Práticas

### Escolha do Tipo
```python
# ✅ Use PERSISTENTE para:
# - Dados financeiros
# - Pedidos de cliente  
# - Logs de auditoria
# - Operações críticas

# ✅ Use TRANSIENTE para:
# - Métricas temporárias
# - Cache invalidation
# - Heartbeats
# - Preview data
```

### Balanceamento
```python
# ✅ Misture conforme necessidade
if is_critical_data:
    delivery_mode = 2  # Persistente
else:
    delivery_mode = 1  # Transiente
```

### Cleanup
```python
# Para filas persistentes grandes
# Use TTL ou cleanup periódico
# para evitar crescimento descontrolado
```

## Troubleshooting

### Fila Persistente Cresce Muito
- Implemente TTL nas mensagens
- Use lazy queues
- Monitore espaço em disco
- Considere purge periódico

### Performance Degradada
- Verifique ratio persistente/transiente
- Monitore I/O de disco
- Considere SSD para persistência
- Ajuste prefetch_count

### Mensagens Perdidas
- Verifique se fila é durable=True
- Confirme delivery_mode=2
- Use publisher confirms
- Implemente retry logic
