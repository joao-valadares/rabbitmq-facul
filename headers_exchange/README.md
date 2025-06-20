# Headers Exchange

## Descrição

O **Headers Exchange** é um tipo de exchange que roteia mensagens baseado nos **headers** (cabeçalhos) das mensagens ao invés da routing key. Oferece roteamento muito flexível usando múltiplos critérios.

### Como Funciona

1. Producer envia mensagens com headers customizados
2. Consumers definem bindings com critérios de headers
3. Exchange compara headers da mensagem com critérios dos bindings
4. Mensagem é entregue para filas cujos critérios correspondam

### Tipos de Matching

- **`x-match: all`**: **TODOS** os headers especificados devem corresponder (AND)
- **`x-match: any`**: **QUALQUER** header especificado deve corresponder (OR)

### Cenário Implementado

- **Producer**: Envia mensagens com headers variados:
  - `format`: json, xml, csv
  - `priority`: high, medium, low  
  - `region`: us, eu, br
  - `encrypted`: true
  - `source`: api, batch

- **Consumer 1**: JSON de alta prioridade (`format=json AND priority=high`)
- **Consumer 2**: Região US ou formato XML (`region=us OR format=xml`)
- **Consumer 3**: Dados criptografados (`encrypted=true`)

## Arquitetura

```
Producer → Headers Exchange → Filas por critério → Consumers especializados
                ↓
    {format=json, priority=high}     → x-match=all    → Consumer 1
    {region=us, format=xml}          → x-match=any    → Consumer 2
    {encrypted=true}                 → x-match=any    → Consumer 3
```

## Exemplos de Roteamento

| Headers da Mensagem | Consumer 1 (json+high) | Consumer 2 (us OR xml) | Consumer 3 (encrypted) |
|---------------------|-------------------------|-------------------------|-------------------------|
| `format=json, priority=high, region=us` | ✅ (all match) | ✅ (us match) | ❌ |
| `format=xml, priority=low, region=eu` | ❌ (priority≠high) | ✅ (xml match) | ❌ |
| `format=json, encrypted=true, region=us` | ❌ (no priority) | ✅ (us match) | ✅ (encrypted) |
| `format=csv, priority=high, source=api` | ❌ (format≠json) | ❌ (no match) | ❌ |

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
cd headers_exchange
python producer.py

# Terminal 2 - Consumer JSON High Priority
python consumer1.py

# Terminal 3 - Consumer US or XML
python consumer2.py

# Terminal 4 - Consumer Encrypted
python consumer3.py
```

## Comportamento Esperado

### Producer
- Envia mensagens com diferentes combinações de headers
- Routing key é ignorada (pode ser vazia)
- Headers determinam o roteamento

### Consumers
- **Consumer 1**: Recebe apenas JSON de alta prioridade (ambos critérios)
- **Consumer 2**: Recebe mensagens dos EUA ou em XML (qualquer critério)
- **Consumer 3**: Recebe apenas mensagens criptografadas

### Logs Esperados

```
# Producer
ENVIADO → Exchange: headers_exchange_demo | Headers: format=json, priority=high, region=us

# Consumer 1 (JSON High Priority)
[JSON_HIGH_PRIORITY_PROCESSOR] 🚀 PROCESSAMENTO PRIORITÁRIO!

# Consumer 2 (US or XML)  
[US_OR_XML_PROCESSOR] 🎯 CRITÉRIO ATENDIDO: REGIÃO=US

# Consumer 3 (Encrypted) - Não recebe esta mensagem
```

## Características Técnicas

- **Exchange Type**: `headers`
- **Routing Key**: Ignorada (pode ser vazia)
- **Critérios**: Baseados em headers da mensagem
- **Matching**: `x-match=all` (AND) ou `x-match=any` (OR)
- **Flexibilidade**: Múltiplos critérios por binding

## Casos de Uso

### Filtragem por Metadados
```python
headers = {
    "content_type": "video",
    "resolution": "4k", 
    "region": "us"
}
# Consumer: x-match=all, content_type=video, resolution=4k
```

### Roteamento por Prioridade e Formato
```python
headers = {
    "priority": "critical",
    "format": "json",
    "department": "finance"
}
# Consumer: x-match=any, priority=critical, department=finance
```

### Filtros de Segurança
```python
headers = {
    "classification": "confidential",
    "clearance_level": "top_secret",
    "encrypted": "true"
}
# Consumer: x-match=all (todos os critérios de segurança)
```

### Processamento Regional
```python
headers = {
    "region": "eu",
    "gdpr_compliant": "true",
    "language": "pt"
}
# Consumer: x-match=any, region=eu, gdpr_compliant=true
```

## Vantagens

- **Flexibilidade Máxima**: Múltiplos critérios de roteamento
- **Lógica Complexa**: Suporte a AND e OR nos critérios
- **Metadados Rica**: Roteamento baseado em contexto completo
- **Sem Limitações de Routing Key**: Headers podem ser ilimitados

## Limitações

- **Performance**: Matching de headers é mais lento que routing key
- **Complexidade**: Pode ficar muito complexo rapidamente
- **Debugging**: Difícil rastrear por que uma mensagem foi/não foi roteada
- **Overhead**: Headers aumentam o tamanho das mensagens

## Comparação x-match

### x-match: all (AND)
```python
binding_headers = {
    "x-match": "all",
    "format": "json",
    "priority": "high"
}
# Recebe APENAS se: format=json E priority=high
```

### x-match: any (OR)  
```python
binding_headers = {
    "x-match": "any", 
    "region": "us",
    "format": "xml"
}
# Recebe se: region=us OU format=xml (ou ambos)
```

## Comparação com outros Exchanges

| Característica | Headers | Topic | Direct | Fanout |
|----------------|---------|-------|--------|--------|
| Critério | Headers da mensagem | Padrões routing key | Routing key exata | Nenhum |
| Flexibilidade | Máxima | Alta | Baixa | Nenhuma |
| Performance | Baixa | Média | Alta | Alta |
| Complexidade | Muito Alta | Alta | Baixa | Baixa |
| Casos de Uso | Filtros complexos | Hierarquias | Roteamento simples | Broadcast |

## Melhores Práticas

### Headers Bem Definidos
```python
# ✅ Bom - Headers claros e consistentes
headers = {
    "content_type": "order",
    "priority": "high",
    "region": "us"
}

# ❌ Ruim - Headers inconsistentes
headers = {
    "type": "order",        # inconsistente com content_type
    "urgent": "yes",        # inconsistente com priority
    "country": "usa"        # inconsistente com region  
}
```

### Uso Moderado de Critérios
```python
# ✅ Bom - Poucos critérios claros
binding_headers = {
    "x-match": "all",
    "department": "finance",
    "priority": "high"
}

# ❌ Ruim - Muitos critérios
binding_headers = {
    "x-match": "all",
    "dept": "fin", "prio": "hi", "reg": "us", 
    "fmt": "json", "enc": "true", "src": "api"
}
```
