"""
Producer Python para Interoperabilidade
Demonstra envio de mensagens que serão consumidas por diferentes linguagens
"""
import sys
import os
import time
import json
from datetime import datetime
import random
import uuid

# Adiciona o diretório pai ao path para importar utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pika
from utils.common import (
    setup_logging, get_rabbitmq_connection, create_exchange_and_queue,
    log_message_sent, print_scenario_header, print_config_info
)

def main():
    # Configurações do cenário
    SCENARIO_NAME = "interoperability"
    COMPONENT_NAME = "producer"
    EXCHANGE_NAME = "interop_exchange"
      # Filas para diferentes linguagens
    PYTHON_QUEUE = "python_queue"
    NODEJS_QUEUE = "nodejs_queue"
    JAVASCRIPT_QUEUE = "javascript_queue"
    
    # Setup
    print_scenario_header(
        SCENARIO_NAME, 
        COMPONENT_NAME, 
        "Producer Python que envia para consumers em múltiplas linguagens"
    )
    
    logger = setup_logging(SCENARIO_NAME, COMPONENT_NAME)
    print_config_info(logger)
    
    try:
        # Conecta ao RabbitMQ
        logger.info("Conectando ao RabbitMQ...")
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        # Declara exchange e filas
        logger.info(f"Declarando exchange '{EXCHANGE_NAME}' tipo direct...")
        channel.exchange_declare(
            exchange=EXCHANGE_NAME,
            exchange_type='direct',
            durable=True
        )
          # Declara filas para cada linguagem
        queues = [PYTHON_QUEUE, NODEJS_QUEUE, JAVASCRIPT_QUEUE]
        routing_keys = ["python", "nodejs", "javascript"]
        
        for queue, routing_key in zip(queues, routing_keys):
            logger.info(f"Declarando fila '{queue}' com routing key '{routing_key}'...")
            channel.queue_declare(queue=queue, durable=True)
            channel.queue_bind(
                exchange=EXCHANGE_NAME,
                queue=queue,
                routing_key=routing_key
            )
        
        # Tipos de mensagens para demonstrar interoperabilidade
        message_templates = [
            {
                "type": "USER_REGISTRATION",
                "description": "Novo usuário registrado",
                "schema": {
                    "user_id": "string",
                    "email": "string", 
                    "name": "string",
                    "timestamp": "datetime",
                    "metadata": "object"
                }
            },
            {
                "type": "ORDER_CREATED",
                "description": "Novo pedido criado",
                "schema": {
                    "order_id": "string",
                    "customer_id": "string",
                    "items": "array",
                    "total": "float",
                    "currency": "string"
                }
            },
            {
                "type": "PAYMENT_PROCESSED",
                "description": "Pagamento processado",
                "schema": {
                    "payment_id": "string",
                    "order_id": "string",
                    "amount": "float",
                    "status": "string",
                    "gateway": "string"
                }
            },
            {
                "type": "INVENTORY_UPDATE",
                "description": "Atualização de estoque",
                "schema": {
                    "product_id": "string",
                    "sku": "string",
                    "quantity": "integer",
                    "operation": "string",
                    "warehouse": "string"
                }
            },
            {
                "type": "NOTIFICATION_SEND",
                "description": "Envio de notificação",
                "schema": {
                    "notification_id": "string",
                    "recipient": "string",
                    "channel": "string",
                    "message": "string",
                    "priority": "integer"
                }
            }
        ]
        logger.info("Iniciando envio de mensagens interoperáveis...")
        print(f"\n🌐 CENÁRIO: Interoperabilidade entre linguagens")
        print(f"🐍 Python → 🟢 Node.js → 🟡 JavaScript")
        print(f"📋 Formato: JSON padronizado")
        print(f"🔄 Pressione Ctrl+C para parar\n")
        
        message_count = 0
        
        # Loop principal de envio
        while True:
            # Escolhe template de mensagem
            template = random.choice(message_templates)
              # Escolhe linguagem de destino
            target_lang = random.choice(["python", "nodejs", "javascript"])
            target_queue = f"{target_lang}_queue"
            
            message_count += 1
            
            # Cria mensagem baseada no template
            message = create_message_from_template(template, message_count)
            
            # Adiciona metadados de interoperabilidade
            message["_meta"] = {
                "producer": "python",
                "target": target_lang,
                "version": "1.0",
                "encoding": "utf-8",
                "timestamp": datetime.now().isoformat(),
                "message_id": str(uuid.uuid4()),
                "correlation_id": f"msg-{message_count:06d}",
                "format": "json"
            }
            
            # Serializa para JSON (formato universal)
            message_body = json.dumps(message, indent=2, ensure_ascii=False)
            
            # Headers para interoperabilidade
            headers = {
                'content-type': 'application/json',
                'encoding': 'utf-8',
                'producer-language': 'python',
                'target-language': target_lang,
                'message-type': template["type"],
                'schema-version': '1.0',
                'correlation-id': message["_meta"]["correlation_id"]
            }
            
            # Publica mensagem
            channel.basic_publish(
                exchange=EXCHANGE_NAME,
                routing_key=target_lang,
                body=message_body,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Persistente
                    content_type='application/json',
                    content_encoding='utf-8',
                    message_id=message["_meta"]["message_id"],
                    correlation_id=message["_meta"]["correlation_id"],
                    timestamp=int(time.time()),
                    headers=headers
                )
            )
              # Log detalhado
            lang_icons = {"python": "🐍", "nodejs": "🟢", "javascript": "🟡"}
            lang_icon = lang_icons.get(target_lang, "📝")
            
            log_message_sent(
                logger, 
                message_count, 
                f"{lang_icon} {target_lang.upper()}: {template['type']}"
            )
            
            print(f"📤 MSG #{message_count:03d} | "
                  f"{lang_icon} {target_lang:6s} | "
                  f"{template['type']:20s} | "
                  f"{template['description']}")
            
            # Aguarda antes da próxima mensagem
            time.sleep(1.0)
            
    except KeyboardInterrupt:
        logger.info(f"Interrompido pelo usuário. Total de mensagens enviadas: {message_count}")
        print(f"\n✅ Finalizando producer. Total: {message_count} mensagens enviadas")
        
    except Exception as e:
        logger.error(f"Erro no producer: {e}")
        print(f"❌ Erro: {e}")
        
    finally:
        if 'connection' in locals() and connection.is_open:
            connection.close()
            logger.info("Conexão fechada")

def create_message_from_template(template, message_count):
    """Cria mensagem baseada no template"""
    msg_type = template["type"]
    
    if msg_type == "USER_REGISTRATION":
        return {
            "type": msg_type,
            "user_id": f"user_{message_count:06d}",
            "email": f"user{message_count}@example.com",
            "name": f"User {message_count}",
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "source": "web_app",
                "ip_address": f"192.168.1.{random.randint(1, 255)}",
                "user_agent": "Mozilla/5.0 (compatible)",
                "referrer": random.choice(["google", "facebook", "direct", "email"])
            }
        }
    
    elif msg_type == "ORDER_CREATED":
        num_items = random.randint(1, 5)
        items = []
        total = 0.0
        
        for i in range(num_items):
            price = round(random.uniform(10.0, 100.0), 2)
            quantity = random.randint(1, 3)
            item_total = price * quantity
            total += item_total
            
            items.append({
                "product_id": f"prod_{i+1:03d}",
                "name": f"Product {i+1}",
                "price": price,
                "quantity": quantity,
                "subtotal": item_total
            })
        
        return {
            "type": msg_type,
            "order_id": f"order_{message_count:06d}",
            "customer_id": f"customer_{random.randint(1, 1000):04d}",
            "items": items,
            "total": round(total, 2),
            "currency": "USD",
            "status": "pending"
        }
    
    elif msg_type == "PAYMENT_PROCESSED":
        return {
            "type": msg_type,
            "payment_id": f"pay_{message_count:06d}",
            "order_id": f"order_{random.randint(1, message_count):06d}",
            "amount": round(random.uniform(50.0, 500.0), 2),
            "status": random.choice(["success", "failed", "pending"]),
            "gateway": random.choice(["stripe", "paypal", "square", "adyen"]),
            "transaction_id": f"txn_{uuid.uuid4().hex[:12]}"
        }
    
    elif msg_type == "INVENTORY_UPDATE":
        return {
            "type": msg_type,
            "product_id": f"prod_{random.randint(1, 100):03d}",
            "sku": f"SKU-{random.randint(10000, 99999)}",
            "quantity": random.randint(0, 1000),
            "operation": random.choice(["add", "remove", "set", "reserve"]),
            "warehouse": random.choice(["WH001", "WH002", "WH003", "WH004"]),
            "reason": random.choice(["sale", "return", "damage", "restock"])
        }
    
    elif msg_type == "NOTIFICATION_SEND":
        return {
            "type": msg_type,
            "notification_id": f"notif_{message_count:06d}",
            "recipient": f"user_{random.randint(1, 1000):04d}",
            "channel": random.choice(["email", "sms", "push", "webhook"]),
            "message": f"Important notification #{message_count}",
            "priority": random.randint(1, 5),
            "template": random.choice(["welcome", "order_confirmation", "payment_receipt", "alert"])
        }
    
    else:
        return {
            "type": msg_type,
            "id": message_count,
            "data": f"Generic data for message {message_count}",
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    main()
