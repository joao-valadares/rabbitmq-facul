# Interoperability - Interoperabilidade entre Linguagens

## 📋 Descrição
Este cenário demonstra a interoperabilidade entre diferentes linguagens de programação usando RabbitMQ como broker de mensagens. Um producer Python envia mensagens que são consumidas por applications escritas em Python, Node.js e JavaScript.

## 🎯 Objetivos de Aprendizagem
- Demonstrar interoperabilidade entre Python, Node.js e JavaScript
- Implementar protocolos de comunicação padronizados
- Compreender serialização/deserialização JSON
- Explorar idiomas específicos de cada linguagem
- Validar headers e metadados para compatibilidade

## 🏗️ Arquitetura

```
Producer (Python) → [interop_exchange] → python_queue → Consumer1 (Python)
                                        → nodejs_queue → Consumer2 (Node.js)
                                        → javascript_queue → Consumer3 (JavaScript)
```

## 🌐 Stack Tecnológica

### Producer - Python 🐍
- **Runtime**: Python 3.8+
- **Biblioteca**: pika
- **Funcionalidades**: JSON serialization, metadata injection

### Consumer1 - Python 🐍
- **Runtime**: Python 3.8+
- **Biblioteca**: pika
- **Recursos demonstrados**: List/dict comprehensions, f-strings, type hints

### Consumer2 - Node.js 🟢
- **Runtime**: Node.js 16+
- **Biblioteca**: amqplib
- **Recursos demonstrados**: async/await, destructuring, map/filter/reduce

### Consumer3 - JavaScript 🟡
- **Runtime**: Node.js 16+
- **Biblioteca**: amqplib
- **Recursos demonstrados**: ES6+ features, async/await, Promise.all, modern JS patterns

## 🔧 Componentes

### Producer (`producer.py`)
- Gera mensagens padronizadas em JSON
- Inclui metadados de interoperabilidade
- Roteia para diferentes filas por linguagem
- Demonstra tipos de dados complexos

### Consumer1 (`consumer1.py`) - Python
- Processa mensagens usando idiomas Python
- Demonstra recursos específicos da linguagem
- Validação de dados com estruturas nativas

### Consumer2 (`consumer2.js`) - Node.js
- Processa mensagens usando recursos JavaScript modernos
- Async/await para operações não-bloqueantes
- Manipulação de JSON nativa

### Consumer3 (`consumer3.js`) - JavaScript
- Processa mensagens usando recursos JavaScript modernos
- ES6+ features como destructuring, async/await
- Promise.all para processamento paralelo

## ⚙️ Configurações

### Variáveis de Ambiente
- `RABBITMQ_HOST`: Servidor RabbitMQ (padrão: localhost)
- `RABBITMQ_PORT`: Porta RabbitMQ (padrão: 5672)
- `RABBITMQ_USER`: Usuário (padrão: guest)
- `RABBITMQ_PASS`: Senha (padrão: guest)
- `LOG_LEVEL`: Nível de log (padrão: INFO)

### Exchange e Filas
- **Exchange**: `interop_exchange` (tipo: direct)
- **Routing Keys**: `python`, `nodejs`, `javascript`
- **Filas**: `python_queue`, `nodejs_queue`, `javascript_queue`

## 🚀 Setup e Execução

### 1. Preparação Python
```bash
# Já configurado - usar o ambiente existente
cd interoperability
```

### 2. Setup Node.js
```bash
cd interoperability
npm install
```

### 3. Execução dos Consumers

#### Terminal 1 - Consumer Python
```bash
cd interoperability
python consumer1.py
```

#### Terminal 2 - Consumer Node.js
```bash
cd interoperability
npm start
# ou diretamente: node consumer2.js
```

#### Terminal 3 - Consumer JavaScript
```bash
cd interoperability
node consumer3.js
```

#### Terminal 4 - Producer
```bash
cd interoperability
python producer.py
```

## 📨 Formato de Mensagens

### Estrutura Padrão
```json
{
  "type": "USER_REGISTRATION",
  "user_id": "user_000001",
  "email": "user1@example.com",
  "name": "User 1",
  "timestamp": "2024-01-15T10:30:00",
  "metadata": {
    "source": "web_app",
    "ip_address": "192.168.1.100"
  },
  "_meta": {
    "producer": "python",
    "target": "nodejs",
    "version": "1.0",
    "encoding": "utf-8",
    "message_id": "uuid-here",
    "correlation_id": "msg-000001"
  }
}
```

### Tipos de Mensagens Suportadas

#### 1. USER_REGISTRATION
```json
{
  "type": "USER_REGISTRATION",
  "user_id": "string",
  "email": "string",
  "name": "string",
  "metadata": {
    "source": "string",
    "ip_address": "string"
  }
}
```

#### 2. ORDER_CREATED
```json
{
  "type": "ORDER_CREATED",
  "order_id": "string",
  "customer_id": "string",
  "items": [
    {
      "product_id": "string",
      "name": "string",
      "price": 99.99,
      "quantity": 2
    }
  ],
  "total": 199.98
}
```

#### 3. PAYMENT_PROCESSED
```json
{
  "type": "PAYMENT_PROCESSED",
  "payment_id": "string",
  "order_id": "string",
  "amount": 199.98,
  "status": "success|failed|pending",
  "gateway": "stripe|paypal"
}
```

## 🔍 Recursos Demonstrados por Linguagem

### Python 🐍
```python
# List comprehensions
domains = [email.split('@')[1] for email in emails if '@' in email]

# Dictionary comprehensions
user_info = {k: v for k, v in message.items() if not k.startswith('_')}

# F-string formatting
logger.info(f"Processando {len(items)} itens: {', '.join(product_ids)}")

# Set operations
missing_fields = required_fields - present_fields

# Exception handling específico
try:
    process_data()
except json.JSONDecodeError as e:
    logger.error(f"JSON inválido: {e}")
```

### Node.js 🟢
```javascript
// Destructuring assignment
const { user_id, email, name, metadata = {} } = message;

// Array methods
const totalItems = items.reduce((sum, item) => sum + item.quantity, 0);
const productIds = items.map(item => item.product_id);

// Template literals
console.log(`Processando pedido ${orderId} - Total: $${total.toFixed(2)}`);

// Async/await
await Promise.all([
    validateStock(),
    calculateShipping(),
    generateInvoice()
]);

// Modern error handling
try {
    await processPayment();
} catch (error) {
    console.error(`Erro no pagamento: ${error.message}`);
}
```

### JavaScript 🟡
```javascript
// Destructuring and modern syntax
const { user_id, email, name } = message;

// Array methods and chaining
const productIds = items
    .filter(item => item.product_id)
    .map(item => item.product_id);

// Async/await and Promises
await Promise.all(tasks.map(async task => {
    console.log(`${task.name}...`);
    await sleep(task.delay);
}));

// Optional chaining
const domain = email?.split('@')?.[1] || 'unknown';

// Template literals
console.log(`Processing: ${item.name}`);

// Modern error handling
try {
    await processMessage();
} catch (error) {
    console.error(`Processing error: ${error.message}`);
}
```

## 📊 Métricas de Interoperabilidade

### Throughput por Linguagem
- **Python**: ~15-25 msg/s (interpretado, alto nível)
- **Node.js**: ~20-35 msg/s (V8 engine, async)
- **JavaScript**: ~20-35 msg/s (V8 engine, modern features)

### Uso de Memória
- **Python**: ~15-30 MB (base + interpreter)
- **Node.js**: ~25-45 MB (V8 heap)
- **JavaScript**: ~25-45 MB (V8 heap, shared runtime)

### Tempo de Inicialização
- **Python**: ~0.5-1s (import time)
- **Node.js**: ~0.2-0.5s (fast startup)
- **JavaScript**: ~0.2-0.5s (fast startup, shared runtime)

## 🧪 Testes de Compatibilidade

### Teste 1: Serialização/Deserialização
1. Producer Python envia dados complexos
2. Cada consumer processa corretamente
3. Verificar integridade dos dados

### Teste 2: Encoding de Caracteres
1. Enviar mensagens com caracteres especiais (UTF-8)
2. Verificar processamento correto em todas as linguagens
3. Testar emojis e acentos

### Teste 3: Tipos de Dados
1. Numbers (int, float, decimal)
2. Strings (ASCII, Unicode)
3. Arrays e Objects aninhados
4. Booleans e null values

### Teste 4: Headers e Metadados
1. Verificar propagação de headers
2. Testar correlation IDs
3. Validar content-type e encoding

## 🔧 Configurações de Build

### Node.js Dependencies
```json
{
  "dependencies": {
    "amqplib": "^0.10.3"
  },
  "scripts": {
    "start": "node consumer2.js"
  }
}
```

## 🎯 Casos de Uso Práticos

### 1. Sistema de E-commerce
- **Producer**: API Gateway (Python/Django)
- **Consumer 1**: Order Service (Python)
- **Consumer 2**: Notification Service (Node.js)
- **Consumer 3**: Analytics Service (JavaScript)

### 2. Sistema de Monitoramento
- **Producer**: Log Collector (Python)
- **Consumer 1**: Real-time Dashboard (Node.js)
- **Consumer 2**: Alert Engine (Python)
- **Consumer 3**: Data Warehouse (JavaScript)

### 3. Pipeline de Dados
- **Producer**: Data Ingestion (Python)
- **Consumer 1**: Preprocessing (Python/Pandas)
- **Consumer 2**: Stream Processing (Node.js)
- **Consumer 3**: Batch Analytics (JavaScript)

## 🔍 Debugging e Monitoramento

### Logs Padronizados
Cada consumer gera logs no formato:
```
📥 MSG #001 | 🐍→🟢 | USER_REGISTRATION     | Processing...
✅ MSG #001 | 🟢 Node.js | 0.45s | ID: msg-000001 | Uptime: 0:05
📥 MSG #002 | 🐍→🟡 | ORDER_CREATED        | Processing...
✅ MSG #002 | 🟡 JavaScript | 0.32s | ID: msg-000002 | Uptime: 0:10
```

### Métricas Importantes
- Taxa de processamento por linguagem
- Tempo médio de processamento
- Taxa de erro por tipo de mensagem
- Uso de recursos (CPU/Memória)

### Ferramentas de Debug
```bash
# RabbitMQ Management
http://localhost:15672

# Logs detalhados
export LOG_LEVEL=DEBUG

# Monitoring de filas
rabbitmqctl list_queues name messages_ready messages_unacknowledged consumers
```

## 🎓 Melhores Práticas

### 1. **Formato de Dados**
- Use JSON para máxima compatibilidade
- Inclua versioning nos schemas
- Valide entrada em todos os consumers

### 2. **Error Handling**
- Implemente retry com backoff
- Use dead letter queues
- Log erros com contexto

### 3. **Performance**
- Ajuste prefetch por linguagem
- Use connection pooling
- Monitor uso de recursos

### 4. **Manutenibilidade**
- Documente schemas de mensagem
- Versionamento de APIs
- Testes de compatibilidade

## 📚 Referências
- [RabbitMQ Tutorials](https://www.rabbitmq.com/tutorials/)
- [Python pika Documentation](https://pika.readthedocs.io/)
- [Node.js amqplib Documentation](https://www.squaremobius.net/amqp.node/)
- [JavaScript ES6+ Features](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
- [Modern JavaScript Patterns](https://addyosmani.com/resources/essentialjsdesignpatterns/book/)
