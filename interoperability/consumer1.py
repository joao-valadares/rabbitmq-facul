"""
Consumer Python para Interoperabilidade
Demonstra consumo de mensagens enviadas pelo producer Python
"""
import sys
import os
import time
import json
from datetime import datetime
import random

# Adiciona o diretório pai ao path para importar utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pika
from utils.common import (
    setup_logging, get_rabbitmq_connection,
    print_scenario_header, print_config_info
)

def main():
    # Configurações do cenário
    SCENARIO_NAME = "interoperability"
    COMPONENT_NAME = "consumer1-python"
    QUEUE_NAME = "python_queue"
    
    # Setup
    print_scenario_header(
        SCENARIO_NAME, 
        COMPONENT_NAME, 
        "Consumer Python para demonstração de interoperabilidade"
    )
    
    logger = setup_logging(SCENARIO_NAME, COMPONENT_NAME)
    print_config_info(logger)
    
    try:
        # Conecta ao RabbitMQ
        logger.info("Conectando ao RabbitMQ...")
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        # Declara a fila (idempotente)
        logger.info(f"Declarando fila '{QUEUE_NAME}'...")
        channel.queue_declare(queue=QUEUE_NAME, durable=True)
        
        # Configurações do consumer
        channel.basic_qos(prefetch_count=1)
        
        # Estatísticas
        stats = {
            'processed': 0,
            'by_type': {},
            'errors': 0,
            'processing_times': [],
            'start_time': datetime.now()
        }
        
        logger.info("Iniciando consumer Python...")
        print(f"\n🐍 CONSUMER PYTHON: Processador Nativo")
        print(f"📋 Fila: {QUEUE_NAME}")
        print(f"🔧 Linguagem: Python 3.x")
        print(f"📦 Biblioteca: pika")
        print(f"🔄 Pressione Ctrl+C para parar\n")
        
        def callback(ch, method, properties, body):
            try:
                start_time = time.time()
                
                # Decodifica mensagem JSON
                message = json.loads(body.decode('utf-8'))
                stats['processed'] += 1
                
                # Extrai metadados
                msg_type = message.get('type', 'UNKNOWN')
                meta = message.get('_meta', {})
                
                producer_lang = meta.get('producer', 'unknown')
                message_id = meta.get('message_id', 'unknown')
                correlation_id = meta.get('correlation_id', 'unknown')
                
                # Atualiza estatísticas por tipo
                if msg_type not in stats['by_type']:
                    stats['by_type'][msg_type] = 0
                stats['by_type'][msg_type] += 1
                
                # Log de recebimento
                print(f"📥 MSG #{stats['processed']:03d} | "
                      f"🐍→🐍 | "
                      f"{msg_type:20s} | "
                      f"Processing...")
                
                # Processamento específico por tipo em Python
                if msg_type == "USER_REGISTRATION":
                    process_user_registration_python(message, logger)
                elif msg_type == "ORDER_CREATED":
                    process_order_created_python(message, logger)
                elif msg_type == "PAYMENT_PROCESSED":
                    process_payment_processed_python(message, logger)
                elif msg_type == "INVENTORY_UPDATE":
                    process_inventory_update_python(message, logger)
                elif msg_type == "NOTIFICATION_SEND":
                    process_notification_send_python(message, logger)
                else:
                    process_generic_message_python(message, logger)
                
                # Simula tempo de processamento
                processing_time = random.uniform(0.3, 0.8)
                time.sleep(processing_time)
                
                end_time = time.time()
                actual_time = end_time - start_time
                stats['processing_times'].append(actual_time)
                
                # Log de conclusão
                elapsed = datetime.now() - stats['start_time']
                uptime = str(elapsed).split('.')[0]
                
                print(f"✅ MSG #{stats['processed']:03d} | "
                      f"🐍 Python | "
                      f"{actual_time:.2f}s | "
                      f"ID: {correlation_id} | "
                      f"Uptime: {uptime}")
                
                # Confirma processamento
                ch.basic_ack(delivery_tag=method.delivery_tag)
                
                # Log estatísticas a cada 10 mensagens
                if stats['processed'] % 10 == 0:
                    print_stats(stats, logger)
                
            except json.JSONDecodeError as e:
                stats['errors'] += 1
                logger.error(f"Erro ao decodificar JSON: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                
            except Exception as e:
                stats['errors'] += 1
                logger.error(f"Erro no processamento: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        
        # Configura consumer
        channel.basic_consume(
            queue=QUEUE_NAME,
            on_message_callback=callback,
            auto_ack=False
        )
        
        logger.info("Aguardando mensagens. Para sair, pressione CTRL+C")
        channel.start_consuming()
        
    except KeyboardInterrupt:
        logger.info("Interrompido pelo usuário")
        print(f"\n✅ Finalizando consumer Python...")
        print_final_stats(stats)
        
    except Exception as e:
        logger.error(f"Erro no consumer: {e}")
        print(f"❌ Erro: {e}")
        
    finally:
        if 'channel' in locals() and channel.is_open:
            channel.stop_consuming()
        if 'connection' in locals() and connection.is_open:
            connection.close()
            logger.info("Conexão fechada")

def process_user_registration_python(message, logger):
    """Processa registro de usuário usando recursos Python"""
    user_id = message.get('user_id')
    email = message.get('email')
    name = message.get('name')
    metadata = message.get('metadata', {})
    
    logger.info(f"🆕 Novo usuário registrado: {name} ({email})")
    
    # Demonstra recursos específicos do Python
    # List comprehension
    domains = [email.split('@')[1] if '@' in email else 'unknown']
    
    # Dictionary comprehension
    user_info = {k: v for k, v in message.items() if k not in ['_meta', 'type']}
    
    # String formatting moderno
    logger.info(f"Dados processados: {len(user_info)} campos")
    logger.info(f"Domínio de email: {domains[0]}")
    
    # Uso de sets para verificação
    required_fields = {'user_id', 'email', 'name'}
    present_fields = set(message.keys())
    missing_fields = required_fields - present_fields
    
    if missing_fields:
        logger.warning(f"Campos obrigatórios ausentes: {missing_fields}")
    else:
        logger.info("✅ Todos os campos obrigatórios presentes")
    
    # Simulação de processamento específico Python
    logger.info("Executando validações Python...")
    logger.info("Salvando no banco de dados...")
    logger.info("Enviando email de boas-vindas...")

def process_order_created_python(message, logger):
    """Processa criação de pedido usando recursos Python"""
    order_id = message.get('order_id')
    items = message.get('items', [])
    total = message.get('total', 0)
    
    logger.info(f"📦 Novo pedido: {order_id} - Total: ${total:.2f}")
    
    # Uso de funcções built-in Python
    total_items = sum(item.get('quantity', 0) for item in items)
    avg_price = total / total_items if total_items > 0 else 0
    
    # Uso de map e filter
    product_ids = list(map(lambda x: x.get('product_id'), items))
    expensive_items = list(filter(lambda x: x.get('price', 0) > 50, items))
    
    logger.info(f"Itens totais: {total_items}")
    logger.info(f"Preço médio: ${avg_price:.2f}")
    logger.info(f"Itens caros (>$50): {len(expensive_items)}")
    logger.info(f"Produtos: {', '.join(product_ids)}")
    
    # Simulação de processamento
    logger.info("Validando estoque...")
    logger.info("Calculando frete...")
    logger.info("Gerando nota fiscal...")

def process_payment_processed_python(message, logger):
    """Processa pagamento usando recursos Python"""
    payment_id = message.get('payment_id')
    amount = message.get('amount', 0)
    status = message.get('status')
    gateway = message.get('gateway')
    
    logger.info(f"💳 Pagamento {payment_id}: {status} - ${amount:.2f} via {gateway}")
    
    # Uso de match/case (Python 3.10+) ou if/elif
    if status == 'success':
        logger.info("✅ Pagamento aprovado - Liberando pedido")
    elif status == 'failed':
        logger.warning("❌ Pagamento rejeitado - Notificando cliente")
    elif status == 'pending':
        logger.info("⏳ Pagamento pendente - Aguardando confirmação")
    else:
        logger.warning(f"⚠️ Status desconhecido: {status}")
    
    # Formatação de moeda usando locale
    try:
        import locale
        locale.setlocale(locale.LC_ALL, '')
        formatted_amount = locale.currency(amount, grouping=True)
        logger.info(f"Valor formatado: {formatted_amount}")
    except:
        logger.info(f"Valor: ${amount:.2f}")
    
    # Simulação de processamento
    logger.info("Atualizando status do pedido...")
    logger.info("Registrando transação...")

def process_inventory_update_python(message, logger):
    """Processa atualização de estoque usando recursos Python"""
    product_id = message.get('product_id')
    quantity = message.get('quantity', 0)
    operation = message.get('operation')
    warehouse = message.get('warehouse')
    
    logger.info(f"📦 Estoque {product_id}: {operation} {quantity} unidades em {warehouse}")
    
    # Uso de enums simulado com dicionário
    OPERATIONS = {
        'add': 'Adicionando ao estoque',
        'remove': 'Removendo do estoque',
        'set': 'Definindo estoque',
        'reserve': 'Reservando itens'
    }
    
    operation_desc = OPERATIONS.get(operation, f'Operação desconhecida: {operation}')
    logger.info(operation_desc)
    
    # Uso de range e list comprehension para simulação
    if operation == 'add' and quantity > 100:
        batches = [quantity // 10] * 10
        logger.info(f"Processando em lotes: {batches[:3]}... (total: {len(batches)} lotes)")
    
    # Simulação de processamento
    logger.info("Validando produto...")
    logger.info("Atualizando banco de dados...")
    logger.info("Notificando sistema de compras...")

def process_notification_send_python(message, logger):
    """Processa envio de notificação usando recursos Python"""
    notif_id = message.get('notification_id')
    recipient = message.get('recipient')
    channel = message.get('channel')
    msg_text = message.get('message')
    priority = message.get('priority', 1)
    
    logger.info(f"📱 Notificação {notif_id}: {channel} para {recipient}")
    
    # Uso de f-strings avançadas
    priority_emoji = "🔴" if priority >= 4 else "🟡" if priority >= 2 else "🟢"
    logger.info(f"Prioridade: {priority_emoji} {priority}/5")
    
    # Uso de bytes e encoding
    msg_bytes = msg_text.encode('utf-8')
    logger.info(f"Tamanho da mensagem: {len(msg_bytes)} bytes")
    
    # Uso de try/except específico
    try:
        if channel == 'email':
            logger.info("📧 Preparando envio por email...")
        elif channel == 'sms':
            logger.info("📱 Preparando envio por SMS...")
        elif channel == 'push':
            logger.info("🔔 Preparando push notification...")
        elif channel == 'webhook':
            logger.info("🔗 Preparando webhook HTTP...")
        else:
            raise ValueError(f"Canal não suportado: {channel}")
        
        logger.info("✅ Notificação enviada com sucesso")
        
    except ValueError as e:
        logger.error(f"Erro de configuração: {e}")

def process_generic_message_python(message, logger):
    """Processa mensagem genérica mostrando recursos Python"""
    msg_type = message.get('type', 'UNKNOWN')
    
    logger.info(f"🔧 Processamento genérico Python: {msg_type}")
    
    # Uso de vars() e dir() para introspecção
    fields = [k for k in message.keys() if not k.startswith('_')]
    logger.info(f"Campos disponíveis: {', '.join(fields)}")
    
    # Uso de any() e all()
    has_string_fields = any(isinstance(v, str) for v in message.values())
    all_fields_present = all(message.get(f) for f in ['type'])
    
    logger.info(f"Tem campos string: {has_string_fields}")
    logger.info(f"Campos obrigatórios: {all_fields_present}")

def print_stats(stats, logger):
    """Imprime estatísticas do consumer Python"""
    elapsed = datetime.now() - stats['start_time']
    rate = stats['processed'] / elapsed.total_seconds() if elapsed.total_seconds() > 0 else 0
    
    avg_time = sum(stats['processing_times']) / len(stats['processing_times']) if stats['processing_times'] else 0
    
    print(f"\n📊 ESTATÍSTICAS PYTHON CONSUMER:")
    print(f"   🐍 Total processadas: {stats['processed']}")
    print(f"   ❌ Erros: {stats['errors']}")
    print(f"   📈 Taxa: {rate:.2f} msg/s")
    print(f"   ⏱️ Tempo médio: {avg_time:.2f}s")
    print(f"   📋 Distribuição por tipo:")
    
    for msg_type, count in sorted(stats['by_type'].items()):
        percentage = (count / stats['processed']) * 100
        print(f"      {msg_type}: {count} ({percentage:.1f}%)")
    
    print(f"   ⏱️ Uptime: {str(elapsed).split('.')[0]}\n")

def print_final_stats(stats):
    """Imprime estatísticas finais do consumer Python"""
    elapsed = datetime.now() - stats['start_time']
    rate = stats['processed'] / elapsed.total_seconds() if elapsed.total_seconds() > 0 else 0
    
    avg_time = sum(stats['processing_times']) / len(stats['processing_times']) if stats['processing_times'] else 0
    min_time = min(stats['processing_times']) if stats['processing_times'] else 0
    max_time = max(stats['processing_times']) if stats['processing_times'] else 0
    
    print(f"\n📈 ESTATÍSTICAS FINAIS - PYTHON CONSUMER:")
    print(f"   🐍 Linguagem: Python 3.x")
    print(f"   📦 Biblioteca: pika")
    print(f"   📊 Total processadas: {stats['processed']}")
    print(f"   ❌ Erros: {stats['errors']}")
    print(f"   ⏱️ Tempo total: {str(elapsed).split('.')[0]}")
    print(f"   📈 Taxa média: {rate:.2f} msg/s")
    print(f"   ⏱️ Tempos de processamento:")
    print(f"      Médio: {avg_time:.2f}s")
    print(f"      Mínimo: {min_time:.2f}s")
    print(f"      Máximo: {max_time:.2f}s")
    
    if stats['processed'] > 0:
        success_rate = ((stats['processed'] - stats['errors']) / stats['processed']) * 100
        print(f"   ✅ Taxa de sucesso: {success_rate:.1f}%")
    
    print(f"\n   🔧 Recursos Python demonstrados:")
    print(f"      • List/Dict comprehensions")
    print(f"      • Map, filter, reduce")
    print(f"      • F-strings avançadas")
    print(f"      • Exception handling específico")
    print(f"      • Introspection (vars, dir)")
    print(f"      • Built-in functions (any, all, sum)")

if __name__ == "__main__":
    main()
