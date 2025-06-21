# 🌐 Projeto de Mensageria Distribuída com RabbitMQ

Este projeto acadêmico demonstra **10 cenários obrigatórios** de mensageria distribuída utilizando RabbitMQ em ambiente distribuído (múltiplas VMs Azure). Cada cenário possui 1 producer e 3 consumers, com código idempotente e documentação completa.

## 🎯 Objetivos Acadêmicos

- Demonstrar padrões de mensageria em sistemas distribuídos
- Implementar diferentes tipos de exchanges e routing
- Comparar estratégias de balanceamento de carga
- Explorar durabilidade e acknowledgments
- Demonstrar interoperabilidade entre linguagens
- Configurar ambiente distribuído na nuvem (Azure)

## 🏗️ Arquitetura Distribuída

```
ProducerSubnet (Brazil South)
+-----------------+
|   VM2 - Producer|  -->   BrokerSubnet (Brazil South)
+-----------------+            |
                               v
                         +-----------------+
                         |  VM1 - Broker   |
                         |  RabbitMQ       | - - - - - - - - - - - 
                         +-----------------+                     |
                               |                                 |
                               v                                 v
                ConsumersSubnet-1(Brazil South)         ConsumerSubnet2 (East US)
                      |         |                                |
                      v         v                                v
         +----------------+  +----------------+            +----------------+
         | VM3 - Consumer1|  | VM4 - Consumer2|            |VM5 - Consumer3 |
         +----------------+  +----------------+            +----------------+

```

### 3. Configuração Manual
```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar ambiente
cp .env.example .env
# Editar .env com suas configurações

# Executar qualquer cenário
cd direct_exchange/
python producer.py    # Terminal 1
python consumer1.py   # Terminal 2
python consumer2.py   # Terminal 3
python consumer3.py   # Terminal 4
```

## 📋 Cenários Implementados (10/10)

### ✅ 1. Direct Exchange (`direct_exchange/`)
**Conceito**: Roteamento baseado em routing key exata
- **Caso de uso**: Sistema de notificações por categoria
- **Routing Keys**: `user.notification`, `admin.alert`, `system.log`
- **Demonstração**: Mensagens direcionadas por tipo específico

### ✅ 2. Fanout Exchange (`fanout_exchange/`)
**Conceito**: Broadcast para todos os consumers
- **Caso de uso**: Atualizações de cache e notificações gerais
- **Comportamento**: Todas as filas recebem todas as mensagens
- **Demonstração**: Sincronização de dados entre múltiplos serviços

### ✅ 3. Topic Exchange (`topic_exchange/`)
**Conceito**: Roteamento por padrões com wildcards
- **Caso de uso**: Sistema de logs hierárquico
- **Padrões**: `app.*.error`, `system.#`, `*.warning.*`
- **Demonstração**: Filtragem flexível de mensagens

### ✅ 4. Headers Exchange (`headers_exchange/`)
**Conceito**: Roteamento baseado em headers da mensagem
- **Caso de uso**: Processamento de pedidos por região e prioridade
- **Headers**: `region`, `priority`, `customer_type`
- **Demonstração**: Matching com `x-match=any/all`

### ✅ 5. Round Robin (`round_robin/`)
**Conceito**: Balanceamento simples entre workers
- **Caso de uso**: Processamento de tarefas distribuído
- **Comportamento**: Distribuição sequencial uniforme
- **Demonstração**: Load balancing básico

### ✅ 6. Round Robin Weighted (`round_robin_weighted/`)
**Conceito**: Balanceamento ponderado com prefetch diferente
- **Caso de uso**: Workers com capacidades diferentes
- **Configuração**: prefetch_count variável por consumer
- **Demonstração**: Distribuição proporcional à capacidade

### ✅ 7. Persistence (`persistence/`)
**Conceito**: Mensagens persistentes vs transientes
- **Caso de uso**: Garantia de durabilidade de dados críticos
- **Teste**: Restart do broker com mensagens em fila
- **Demonstração**: Recovery de mensagens persistentes

### ✅ 8. Acknowledgments (`acknowledgments/`)
**Conceito**: Diferentes estratégias de confirmação
- **Auto ACK**: Rápido mas com risco de perda
- **Manual ACK**: Seguro mas com overhead
- **Smart ACK**: Estratégias inteligentes com retry
- **Demonstração**: Comportamento em falhas

### ✅ 9. Priority Queue (`priority/`)
**Conceito**: Filas com prioridade (0-10)
- **Caso de uso**: Sistema de alertas com diferentes criticidades
- **Prioridades**: CRITICAL(10), ERROR(7), WARNING(5), INFO(3), DEBUG(1)
- **Demonstração**: Processamento preferencial por prioridade

### ✅ 10. Interoperability (`interoperability/`)
**Conceito**: Comunicação entre diferentes linguagens
- **Producer**: Python (pika)
- **Consumer1**: Python (recursos nativos)
- **Consumer2**: Node.js (amqplib)
- **Consumer3**: JavaScript (amqplib + ES6+)
- **Demonstração**: JSON como formato universal

## 🔧 Configuração de Ambiente

### Variáveis de Ambiente (.env)
```env
# RabbitMQ Configuration
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASS=guest
RABBITMQ_VHOST=/

# Application Configuration
LOG_LEVEL=INFO
APP_ENV=development


### Dependências por Tecnologia

#### Python
```bash
pip install pika python-dotenv colorama
```

#### Node.js
```bash
npm install amqplib
```

## 🌐 Deployment no Azure

### Recursos Criados
- **Resource Group**: azure-rabbitmq-rg
- **Virtual Network 1**: 10.0.0.0/16
- **Virtual Network 2**: 10.1.0.0/16
- **VMs**: Standard_B1s (1 vCPUs, 1GB RAM)
- **Network Security Group**: Portas 22, 5672, 15672 abertas


## 📊 Cenários de Teste e Validação
Broadcast para todos os consumers conectados.

### 3. Topic Exchange (`topic_exchange/`)
Roteamento baseado em padrões de routing key.

### 4. Headers Exchange (`headers_exchange/`)
Roteamento baseado em headers das mensagens.

### 5. Round Robin (`round_robin/`)
Balanceamento de carga simples entre consumers.

### 6. Round Robin Ponderado (`round_robin_weighted/`)
Balanceamento usando prefetch diferente por consumer.

### 7. Persistência (`persistence/`)
Demonstra mensagens persistentes vs transientes.

### 8. Acknowledgments (`acknowledgments/`)
Confirmação manual vs automática de mensagens.

### Testes de Funcionalidade

#### 1. Teste de Conectividade
```bash
# Testar conectividade básica
python -c "import pika; print('✅ pika OK')"
ping rabbitmq-host  # Teste de rede
```

#### 2. Teste de Throughput
```bash
# Executar cada cenário por 2 minutos
# Medir: mensagens/segundo, latência, uso de recursos
```

#### 3. Teste de Failover
```bash
# 1. Parar broker durante envio
docker stop rabbitmq-server

# 2. Verificar comportamento dos clients
# 3. Reiniciar broker
docker start rabbitmq-server

# 4. Verificar recuperação de mensagens
```

#### 4. Teste de Interoperabilidade
```bash
# Executar producer Python + consumers em 3 linguagens
cd interoperability/
python producer.py &           # Terminal 1
python consumer1.py &          # Terminal 2  
node consumer2.js &            # Terminal 3
node consumer3.js              # Terminal 4
```

## 📁 Estrutura Completa do Projeto

```
rabbitmq-facul/
├── 📋 README.md                    # Documentação principal
├── 📋 .env.example                 # Template de configuração
├── 📋 requirements.txt             # Dependências Python
│
├── 🔧 utils/                       # Utilitários compartilhados
│   ├── common.py                   # Funções comuns (conexão, logging)
│   └── README.md                   # Documentação dos utilitários
│
├── 🎯 direct_exchange/             # Cenário 1: Roteamento direto
│   ├── producer.py                 # Producer com routing keys específicas
│   ├── consumer1.py                # Consumer para user notifications
│   ├── consumer2.py                # Consumer para admin alerts
│   ├── consumer3.py                # Consumer para system logs
│   └── README.md                   # Documentação do cenário
│
├── 📡 fanout_exchange/             # Cenário 2: Broadcast
│   ├── producer.py                 # Producer para updates gerais
│   ├── consumer1.py                # Consumer cache service
│   ├── consumer2.py                # Consumer analytics service
│   ├── consumer3.py                # Consumer notification service
│   └── README.md                   # Documentação do cenário
│
├── 🔀 topic_exchange/              # Cenário 3: Roteamento por padrão
│   ├── producer.py                 # Producer com routing patterns
│   ├── consumer1.py                # Consumer para *.error.*
│   ├── consumer2.py                # Consumer para app.#
│   ├── consumer3.py                # Consumer para system.*.warning
│   └── README.md                   # Documentação do cenário
│
├── 🏷️ headers_exchange/             # Cenário 4: Roteamento por headers
│   ├── producer.py                 # Producer com headers dinâmicos
│   ├── consumer1.py                # Consumer para região BR + alta prioridade
│   ├── consumer2.py                # Consumer para customer_type = premium
│   ├── consumer3.py                # Consumer com x-match=any
│   └── README.md                   # Documentação do cenário
│
├── ⚖️ round_robin/                  # Cenário 5: Balanceamento simples
│   ├── producer.py                 # Producer de tarefas uniformes
│   ├── consumer1.py                # Worker 1 (processamento básico)
│   ├── consumer2.py                # Worker 2 (processamento básico)
│   ├── consumer3.py                # Worker 3 (processamento básico)
│   └── README.md                   # Documentação do cenário
│
├── ⚖️ round_robin_weighted/         # Cenário 6: Balanceamento ponderado
│   ├── producer.py                 # Producer de tarefas variadas
│   ├── consumer1.py                # Worker rápido (prefetch=5)
│   ├── consumer2.py                # Worker médio (prefetch=3)
│   ├── consumer3.py                # Worker lento (prefetch=1)
│   └── README.md                   # Documentação do cenário
│
├── 💾 persistence/                 # Cenário 7: Durabilidade
│   ├── producer.py                 # Producer com mensagens persistentes/transientes
│   ├── consumer1.py                # Consumer para dados críticos
│   ├── consumer2.py                # Consumer para dados temporários
│   ├── consumer3.py                # Consumer para teste de recovery
│   └── README.md                   # Documentação do cenário
│
├── ✅ acknowledgments/             # Cenário 8: Confirmações
│   ├── producer.py                 # Producer para testes de ACK
│   ├── consumer1.py                # Consumer com auto ACK (risco)
│   ├── consumer2.py                # Consumer com manual ACK (seguro)
│   ├── consumer3.py                # Consumer com smart ACK (inteligente)
│   └── README.md                   # Documentação do cenário
│
├── 🎚️ priority/                    # Cenário 9: Filas com prioridade
│   ├── producer.py                 # Producer com mensagens priorizadas
│   ├── consumer1.py                # Consumer para alertas críticos
│   ├── consumer2.py                # Consumer para operações gerais
│   ├── consumer3.py                # Consumer para processamento em lote
│   └── README.md                   # Documentação do cenário
│
├── 🌐 interoperability/            # Cenário 10: Múltiplas linguagens
│   ├── producer.py                 # Producer Python (JSON universal)
│   ├── consumer1.py                # Consumer Python (recursos nativos)
│   ├── consumer2.js                # Consumer Node.js (async/await)
│   ├── consumer3.js                # Consumer JavaScript (ES6+)
│   ├── package.json                # Dependências Node.js
│   └── README.md                   # Documentação do cenário
```

## 🎓 Casos de Uso Acadêmicos por Cenário

### Direct Exchange - E-commerce
- **Pedidos**: routing key `order.created`
- **Pagamentos**: routing key `payment.processed`
- **Estoque**: routing key `inventory.updated`

### Fanout Exchange - Cache Invalidation
- **Producer**: Sistema principal
- **Consumers**: Multiple cache layers, CDNs, database replicas

### Topic Exchange - Sistema de Logs
- **Patterns**: `app.*.error`, `system.#`, `*.warning.*`
- **Consumers**: Error handling, system monitoring, warning aggregation

### Headers Exchange - Multi-tenant SaaS
- **Headers**: `tenant_id`, `region`, `subscription_level`
- **Consumers**: Region-specific processors, tier-based handlers

### Round Robin - Task Queue
- **Uso**: Image processing, email sending, report generation
- **Workers**: Identical processing capability

### Weighted Round Robin - Heterogeneous Workers
- **Uso**: Different server capacities, varying processing times
- **Workers**: High-end server (prefetch=10), medium (prefetch=5), basic (prefetch=1)

### Persistence - Critical Data
- **Transient**: Temporary notifications, cache updates
- **Persistent**: Financial transactions, user data, audit logs

### Acknowledgments - Reliability Patterns
- **Auto ACK**: High-throughput, loss-tolerant (metrics, logs)
- **Manual ACK**: Critical processing (payments, orders)
- **Smart ACK**: Intelligent retry with circuit breaker

### Priority Queue - Alert System
- **P10**: System down, security breach
- **P7**: Application errors
- **P5**: Warnings
- **P1**: Debug info, batch jobs

### Interoperability - Microservices
- **Python**: Data processing service
- **Node.js**: Real-time API service  
- **JavaScript**: Modern web service integration
---

## 🏆 Conclusão

Este projeto demonstra de forma prática e completa os principais padrões de mensageria distribuída usando RabbitMQ. Cada cenário foi cuidadosamente projetado para ilustrar conceitos específicos e casos de uso reais, fornecendo uma base sólida para entender sistemas de mensageria em ambientes distribuídos.

A implementação distribuída no Azure simula condições reais de produção, onde diferentes componentes rodam em máquinas separadas, comunicando-se através da rede. Isso oferece uma experiência autêntica de desenvolvimento e deployment de sistemas distribuídos.

**Principais aprendizados:**
- Diferentes padrões de roteamento e suas aplicações
- Estratégias de balanceamento de carga
- Importância de durabilidade e acknowledgments
- Interoperabilidade entre linguagens
- Deployment e operação em ambiente cloud

Este projeto serve como uma excelente base para estudos avançados em arquiteturas distribuídas, microsserviços e sistemas de alta disponibilidade.

---

**Desenvolvido para fins acadêmicos** | **Licença: MIT** | **Versão: 1.0.0**

## Características dos Scripts

- **Idempotentes**: Criam recursos necessários se não existirem
- **Isolados**: Cada cenário usa nomes únicos
- **Configuráveis**: Usam variáveis de ambiente
- **Documentados**: Comentários explicativos detalhados

## Deployment em Azure VMs

### 1. Preparação das VMs
```bash
# Em cada VM
sudo apt update
sudo apt install python3 python3-pip
pip3 install pika python-dotenv
```

### 2. Configuração de Rede
- Liberação da porta 5672 (AMQP)
- Liberação da porta 15672 (Management UI)
- Configuração de Security Groups

### 3. Variáveis de Ambiente
```bash
export RABBITMQ_HOST=<IP_DO_BROKER_VM>
export RABBITMQ_PORT=5672
export RABBITMQ_USER=guest
export RABBITMQ_PASSWORD=guest
```
