"""
Producer para Topic Exchange
Demonstra roteamento baseado em padrões de routing key
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
    setup_logging, get_rabbitmq_connection, create_exchange_and_queue,
    log_message_sent, print_scenario_header, print_config_info
)

def main():
    # Configurações do cenário
    SCENARIO_NAME = "topic_exchange"
    COMPONENT_NAME = "producer"
    EXCHANGE_NAME = "topic_exchange_demo"
    EXCHANGE_TYPE = "topic"
    
    # Routing keys com padrões hierárquicos
    ROUTING_PATTERNS = [
        # Sistema.Severidade.Módulo
        "system.info.auth",
        "system.warning.auth",
        "system.error.auth",
        "system.info.database",
        "system.warning.database",
        "system.error.database",
        "system.info.api",
        "system.warning.api",
        "system.error.api",
        # Aplicação.Evento.Local
        "app.user.login",
        "app.user.logout",
        "app.order.created",
        "app.order.updated",
        "app.payment.success",
        "app.payment.failed"
    ]
    
    # Setup
    print_scenario_header(
        SCENARIO_NAME, 
        COMPONENT_NAME, 
        "Producer que envia mensagens com routing keys hierárquicas para Topic Exchange"
    )
    
    logger = setup_logging(SCENARIO_NAME, COMPONENT_NAME)
    print_config_info(logger)
    
    try:
        # Conecta ao RabbitMQ
        logger.info("Conectando ao RabbitMQ...")
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        # Declara o exchange (idempotente)
        logger.info(f"Declarando exchange '{EXCHANGE_NAME}' do tipo '{EXCHANGE_TYPE}'")
        channel.exchange_declare(
            exchange=EXCHANGE_NAME,
            exchange_type=EXCHANGE_TYPE,
            durable=True
        )
        
        logger.info("Producer iniciado. Enviando mensagens com padrões variados...")
        logger.info("Padrões de routing key:")
        for pattern in ROUTING_PATTERNS:
            logger.info(f"  - {pattern}")
        logger.info("Pressione Ctrl+C para parar")
        
        message_count = 1
        
        while True:
            # Escolhe uma routing key aleatória
            routing_key = random.choice(ROUTING_PATTERNS)
            
            # Extrai informações da routing key
            parts = routing_key.split('.')
            category = parts[0]
            subcategory = parts[1]
            detail = parts[2] if len(parts) > 2 else "general"
            
            # Prepara a mensagem
            message_data = {
                "id": message_count,
                "routing_key": routing_key,
                "category": category,
                "subcategory": subcategory,
                "detail": detail,
                "content": f"Mensagem {routing_key} #{message_count}",
                "timestamp": datetime.now().isoformat(),
                "scenario": SCENARIO_NAME
            }
            
            message_body = json.dumps(message_data, ensure_ascii=False)
            
            # Propriedades da mensagem
            properties = pika.BasicProperties(
                delivery_mode=2,  # Mensagem persistente
                content_type='application/json',
                timestamp=int(time.time()),
                headers={
                    'category': category,
                    'subcategory': subcategory,
                    'detail': detail
                }
            )
            
            # Publica a mensagem
            channel.basic_publish(
                exchange=EXCHANGE_NAME,
                routing_key=routing_key,
                body=message_body,
                properties=properties
            )
            
            log_message_sent(logger, EXCHANGE_NAME, routing_key, message_body, properties)
            logger.info(f"Enviado: {category}.{subcategory}.{detail}")
            
            message_count += 1
            time.sleep(2)  # Pausa entre mensagens
            
    except KeyboardInterrupt:
        logger.info("Parando producer...")
    except Exception as e:
        logger.error(f"Erro no producer: {str(e)}")
    finally:
        if 'connection' in locals() and not connection.is_closed:
            connection.close()
            logger.info("Conexão fechada")

if __name__ == "__main__":
    main()
