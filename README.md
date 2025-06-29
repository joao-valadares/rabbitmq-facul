
## Arquitetura 

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

### Execução
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


## Deployment no Azure

### Recursos Criados
- **Resource Group**: azure-rabbitmq-rg
- **Virtual Network 1**: 10.0.0.0/16
- **Virtual Network 2**: 10.1.0.0/16
- **VMs**: Standard_B1s (1 vCPUs, 1GB RAM)


## Conclusão

Este projeto demonstra de forma prática e completa os principais padrões de mensageria distribuída usando RabbitMQ. Cada cenário foi projetado para demonstrar conceitos específicos e casos de uso reais, fornecendo uma base sólida para entender sistemas de mensageria em ambientes distribuídos.

A implementação distribuída no Azure simula condições reais de produção, onde diferentes componentes rodam em máquinas separadas, comunicando-se através da rede. Isso oferece uma experiência autêntica de desenvolvimento e deployment de sistemas distribuídos.

