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
# Executar qualquer cenário
cd direct_exchange/
python producer.py    # Terminal 1
python consumer1.py   # Terminal 2
python consumer2.py   # Terminal 3
python consumer3.py   # Terminal 4
```

## 📋 Cenários Implementados

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


## 🌐 Deployment no Azure

### Recursos Criados
- **Resource Group**: azure-rabbitmq-rg
- **Virtual Network 1**: 10.0.0.0/16
- **Virtual Network 2**: 10.1.0.0/16
- **VMs**: Standard_B1s (1 vCPUs, 1GB RAM)



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

## 🏆 Conclusão

Este projeto demonstra de forma prática e completa os principais padrões de mensageria distribuída usando RabbitMQ. Cada cenário foi projetado para ilustrar conceitos específicos e casos de uso reais, fornecendo uma base sólida para entender sistemas de mensageria em ambientes distribuídos.

A implementação distribuída no Azure simula condições reais de produção, onde diferentes componentes rodam em máquinas separadas, comunicando-se através da rede. Isso oferece uma experiência autêntica de desenvolvimento e deployment de sistemas distribuídos.

