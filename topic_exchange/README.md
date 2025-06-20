# Topic Exchange

## Descrição

O **Topic Exchange** é um tipo de exchange que permite roteamento flexível baseado em **padrões** (patterns) nas routing keys. Usa wildcards `*` (uma palavra) e `#` (zero ou mais palavras) para criar filtros sofisticados.

### Como Funciona

1. Producer envia mensagens com routing keys hierárquicas (ex: `system.error.database`)
2. Consumers definem padrões de binding (ex: `*.error.*`, `system.*`, `app.user.#`)
3. Exchange roteia mensagens para filas cujos padrões correspondam à routing key

### Wildcards

- `*` (asterisco): Substitui exatamente **uma** palavra
- `#` (hash): Substitui **zero ou mais** palavras

### Cenário Implementado

- **Producer**: Envia mensagens com routing keys hierárquicas
  - Sistema: `system.{info|warning|error}.{auth|database|api}`
  - Aplicação: `app.{user|order|payment}.{action}`

- **Consumer 1**: Monitora TODOS os erros (`*.error.*`)
- **Consumer 2**: Monitora mensagens de SISTEMA (`system.*`)
- **Consumer 3**: Rastreia atividades de USUÁRIO (`app.user.*`)

## Arquitetura

```
Producer → Topic Exchange → Filas por padrão → Consumers especializados
                ↓
    system.error.auth    → *.error.*     → Consumer 1 (Error Monitor)
    system.warning.api   → system.*      → Consumer 2 (System Monitor)  
    app.user.login       → app.user.*    → Consumer 3 (User Activity)
    app.order.created    → (nenhum match)
```

## Exemplos de Roteamento

| Routing Key | Consumer 1 (`*.error.*`) | Consumer 2 (`system.*`) | Consumer 3 (`app.user.*`) |
|-------------|--------------------------|--------------------------|----------------------------|
| `system.error.auth` | ✅ | ✅ | ❌ |
| `system.warning.api` | ❌ | ✅ | ❌ |
| `app.user.login` | ❌ | ❌ | ✅ |
| `app.order.created` | ❌ | ❌ | ❌ |
| `system.error.database` | ✅ | ✅ | ❌ |

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
cd topic_exchange
python producer.py

# Terminal 2 - Consumer Error Monitor
python consumer1.py

# Terminal 3 - Consumer System Monitor
python consumer2.py

# Terminal 4 - Consumer User Activity
python consumer3.py
```

## Comportamento Esperado

### Producer
- Envia mensagens com routing keys variadas:
  - `system.info.auth`, `system.error.database`, etc.
  - `app.user.login`, `app.payment.success`, etc.
- Cada mensagem tem estrutura hierárquica

### Consumers
- **Consumer 1**: Recebe apenas mensagens com "error" no meio (`*.error.*`)
- **Consumer 2**: Recebe todas as mensagens de sistema (`system.*`)
- **Consumer 3**: Recebe apenas atividades de usuário (`app.user.*`)

### Logs Esperados

```
# Producer
ENVIADO → Exchange: topic_exchange_demo | Routing Key: system.error.auth

# Consumer 1 (Error Monitor)
[ERROR_MONITOR] 🚨 ERRO DETECTADO! - system.error.auth

# Consumer 2 (System Monitor)  
[SYSTEM_MONITOR] ⚙️ SISTEMA - ERROR - system.error.auth

# Consumer 3 (User Activity) - Não recebe esta mensagem
```

## Características Técnicas

- **Exchange Type**: `topic`
- **Wildcards**: `*` (uma palavra), `#` (zero+ palavras)
- **Routing Keys**: Hierárquicas separadas por pontos
- **Binding Patterns**: Flexíveis com wildcards
- **Durability**: Exchanges e filas são duráveis

## Casos de Uso

### Logs Hierárquicos
```
logs.system.error.database  → logs.*.error.* (errors)
logs.app.info.user         → logs.app.* (app logs)
logs.#                     → logs.# (all logs)
```

### Monitoramento por Severidade
```
monitor.critical.*  → Alertas críticos
monitor.warning.*   → Alertas de warning
monitor.#           → Todos os alertas
```

### Eventos de E-commerce
```
ecommerce.order.created     → ecommerce.order.* (orders)
ecommerce.payment.success   → ecommerce.payment.* (payments)
ecommerce.#                → ecommerce.# (all events)
```

### Notificações por Região
```
notification.us.email    → notification.us.* (US only)
notification.*.sms      → notification.*.sms (SMS all regions)
notification.#          → notification.# (all notifications)
```

## Vantagens

- **Flexibilidade**: Roteamento baseado em padrões
- **Hierarquia**: Suporte a estruturas organizacionais
- **Wildcards**: Filtros poderosos com `*` e `#`
- **Escalabilidade**: Fácil adicionar novos padrões

## Limitações

- **Complexidade**: Pode ficar complexo com muitos padrões
- **Performance**: Matching de padrões tem overhead
- **Debugging**: Mais difícil rastrear roteamento

## Comparação com outros Exchanges

| Característica | Topic | Direct | Fanout |
|----------------|-------|--------|--------|
| Routing Key | Padrões com wildcards | Correspondência exata | Ignorada |
| Flexibilidade | Alta | Baixa | Nenhuma |
| Performance | Média | Alta | Alta |
| Complexidade | Alta | Baixa | Baixa |

## Padrões Comuns

### Logs por Severidade e Sistema
```
*.error.*     → Todos os erros
system.*      → Mensagens de sistema
app.user.*    → Atividades de usuário
*.*.database  → Eventos de database
#             → Todas as mensagens
```

### E-commerce Hierárquico
```
order.#           → Todos eventos de pedido
*.created         → Todos eventos de criação
payment.success.* → Pagamentos bem-sucedidos
user.login        → Login específico (sem wildcard)
```
