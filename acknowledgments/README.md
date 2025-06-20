# Acknowledgments - Confirmação de Mensagens

## 📋 Descrição
Este cenário demonstra a importância dos acknowledgments (confirmações) em sistemas de mensageria. Compara diferentes estratégias de confirmação de processamento de mensagens e seus impactos na garantia de entrega.

## 🎯 Objetivos de Aprendizagem
- Entender a diferença entre auto-acknowledgment e manual acknowledgment
- Compreender os riscos de perda de mensagens
- Implementar estratégias de confirmação inteligentes
- Demonstrar recuperação de falhas no processamento

## 🏗️ Arquitetura

```
Producer → [auto_ack_queue] → Consumer1 (Auto ACK - Risco)
        → [manual_ack_queue] → Consumer2 (Manual ACK - Seguro)
                            → Consumer3 (Smart ACK - Inteligente)
```

## 🔧 Componentes

### Producer (`producer.py`)
- Envia mensagens críticas para duas filas diferentes
- Simula transações bancárias e processamentos importantes
- Mensagens numeradas para rastreamento

### Consumer1 (`consumer1.py`) - Auto ACK
- Usa auto-acknowledgment (risco de perda)
- Simula falhas aleatórias no processamento
- Demonstra perda de mensagens em caso de falha

### Consumer2 (`consumer2.py`) - Manual ACK
- Usa manual acknowledgment (seguro)
- Confirma apenas após processamento completo
- Garante que mensagens não sejam perdidas

### Consumer3 (`consumer3.py`) - Smart ACK
- Implementa estratégia inteligente de confirmação
- Retry automático em caso de falha temporária
- Reject com requeue para erros recuperáveis

## ⚙️ Configurações

### Variáveis de Ambiente
- `RABBITMQ_HOST`: Servidor RabbitMQ (padrão: localhost)
- `RABBITMQ_PORT`: Porta RabbitMQ (padrão: 5672)
- `RABBITMQ_USER`: Usuário (padrão: guest)
- `RABBITMQ_PASS`: Senha (padrão: guest)
- `LOG_LEVEL`: Nível de log (padrão: INFO)

### Filas
- **auto_ack_queue**: Fila para demonstrar auto-acknowledgment
- **manual_ack_queue**: Fila para demonstrar manual acknowledgment

## 🚀 Execução

### 1. Terminal 1 - Consumer Auto ACK
```bash
cd acknowledgments
python consumer1.py
```

### 2. Terminal 2 - Consumer Manual ACK
```bash
cd acknowledgments
python consumer2.py
```

### 3. Terminal 3 - Consumer Smart ACK
```bash
cd acknowledgments
python consumer3.py
```

### 4. Terminal 4 - Producer
```bash
cd acknowledgments
python producer.py
```

## 📊 Teste de Falhas

### Simulando Perda de Mensagens (Auto ACK)
1. Execute o Consumer1 (auto ACK)
2. Execute o Producer
3. Durante o processamento, interrompa o Consumer1 (Ctrl+C)
4. Observe que mensagens são perdidas

### Demonstrando Segurança (Manual ACK)
1. Execute o Consumer2 (manual ACK)
2. Execute o Producer
3. Durante o processamento, interrompa o Consumer2
4. Reinicie o Consumer2
5. Observe que mensagens não perdidas são reprocessadas

## 📈 Métricas Observadas

### Auto ACK (Consumer1)
- ✅ **Performance**: Maior throughput
- ❌ **Confiabilidade**: Risco de perda de mensagens
- ❌ **Recuperação**: Impossível recuperar mensagens perdidas

### Manual ACK (Consumer2)
- ✅ **Confiabilidade**: Zero perda de mensagens
- ✅ **Recuperação**: Mensagens não confirmadas são reprocessadas
- ⚠️ **Performance**: Overhead de confirmação

### Smart ACK (Consumer3)
- ✅ **Confiabilidade**: Estratégias de retry
- ✅ **Flexibilidade**: Diferentes ações por tipo de erro
- ✅ **Observabilidade**: Logs detalhados de decisões

## 🔄 Casos de Uso Demonstrados

### 1. Transações Bancárias (Critical)
- Usar sempre Manual ACK
- Zero tolerância à perda
- Retry em falhas temporárias

### 2. Logs e Métricas (Non-Critical)
- Auto ACK pode ser aceitável
- Performance mais importante que garantia
- Perda ocasional tolerável

### 3. Processamento de Imagens (Smart)
- Retry para falhas de rede
- Reject para arquivos corrompidos
- Confirmação após sucesso completo

## 🎓 Conceitos Demonstrados

### 1. **Auto Acknowledgment**
```python
channel.basic_consume(
    queue='auto_ack_queue',
    on_message_callback=callback,
    auto_ack=True  # Confirmação automática
)
```

### 2. **Manual Acknowledgment**
```python
def callback(ch, method, properties, body):
    try:
        # Processar mensagem
        process_message(body)
        # Confirmar apenas após sucesso
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        # Rejeitar em caso de erro
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
```

### 3. **Smart Acknowledgment**
```python
def smart_callback(ch, method, properties, body):
    try:
        result = process_with_retry(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except RecoverableError:
        # Requeue para retry
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    except FatalError:
        # Não requeue, enviar para DLQ
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
```

## 🔍 Debugging

### Monitoramento de Mensagens
```bash
# Ver mensagens em fila
sudo rabbitmqctl list_queues name messages_ready messages_unacknowledged

# Ver conexões ativas
sudo rabbitmqctl list_connections

# Ver consumers ativos
sudo rabbitmqctl list_consumers
```

### Logs Importantes
- Confirmações enviadas/recebidas
- Falhas no processamento
- Mensagens reprocessadas
- Tempos de processamento

## 🎯 Cenários de Teste

### Teste 1: Perda com Auto ACK
1. Start Consumer1 (auto ACK)
2. Send 10 mensagens
3. Kill Consumer1 durante processamento
4. Verificar mensagens perdidas

### Teste 2: Recuperação com Manual ACK
1. Start Consumer2 (manual ACK)
2. Send 10 mensagens
3. Kill Consumer2 durante processamento
4. Restart Consumer2
5. Verificar reprocessamento

### Teste 3: Smart ACK com Falhas
1. Start Consumer3 (smart ACK)
2. Send mensagens com diferentes tipos de erro
3. Observar estratégias de retry
4. Verificar logs de decisões

## 📚 Referências
- [RabbitMQ Acknowledgments](https://www.rabbitmq.com/confirms.html)
- [Consumer Acknowledgements](https://www.rabbitmq.com/consumers.html#acknowledgement-modes)
- [Delivery Guarantees](https://www.rabbitmq.com/reliability.html)
