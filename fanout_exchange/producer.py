"""
Producer para Fanout Exchange
Demonstra broadcast para todos os consumers conectados
"""
import sys
import os
import time
import json
from datetime import datetime

# Adiciona o diretório pai ao path para importar utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pika
from utils.common import (
    setup_logging, get_rabbitmq_connection, create_exchange_and_queue,
    log_message_sent, print_scenario_header, print_config_info
)

def main():
    # Configurações do cenário
    SCENARIO_NAME = "fanout_exchange"
    COMPONENT_NAME = "producer"
    EXCHANGE_NAME = "fanout_exchange_demo"
    EXCHANGE_TYPE = "fanout"
    
    # Setup
    print_scenario_header(
        SCENARIO_NAME, 
        COMPONENT_NAME, 
        "Producer que faz broadcast de mensagens para todos os consumers via Fanout Exchange"
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
        
        # Declara as filas que os consumers irão usar
        queue_names = [
            "fanout_queue_notifications",
            "fanout_queue_audit", 
            "fanout_queue_metrics"
        ]
        
        logger.info("Declarando filas para os consumers...")
        for queue_name in queue_names:
            channel.queue_declare(queue=queue_name, durable=True)
            channel.queue_bind(
                exchange=EXCHANGE_NAME,
                queue=queue_name,
                routing_key=''  # Ignorada em fanout
            )
            logger.info(f"Fila '{queue_name}' declarada e vinculada")
        
        logger.info("Producer iniciado. Fazendo broadcast a cada 4 segundos...")
        logger.info("Pressione Ctrl+C para parar")
        
        message_count = 1
        
        while True:
            # Prepara a mensagem de broadcast
            message_data = {
                "id": message_count,
                "type": "broadcast",
                "content": f"Mensagem de broadcast #{message_count}",
                "announcement": f"Esta é uma notificação global para todos os consumers",
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
                    'message_type': 'broadcast',
                    'priority': 'normal'
                }
            )
            
            # Publica a mensagem (routing_key é ignorada em fanout)
            channel.basic_publish(
                exchange=EXCHANGE_NAME,
                routing_key='',  # Ignorada em fanout exchange
                body=message_body,
                properties=properties
            )
            
            log_message_sent(logger, EXCHANGE_NAME, "broadcast", message_body, properties)
            logger.info(f"Broadcast #{message_count} enviado para TODOS os consumers")
            
            message_count += 1
            time.sleep(4)  # Pausa entre broadcasts
            
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
