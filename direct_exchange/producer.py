"""
Producer para Direct Exchange
Demonstra roteamento baseado em routing key exata
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
    SCENARIO_NAME = "direct_exchange"
    COMPONENT_NAME = "producer"
    EXCHANGE_NAME = "direct_exchange_demo"
    EXCHANGE_TYPE = "direct"
    
    # Routing keys para diferentes tipos de mensagem
    ROUTING_KEYS = ["info", "warning", "error"]
    
    # Setup
    print_scenario_header(
        SCENARIO_NAME, 
        COMPONENT_NAME, 
        "Producer que envia mensagens com routing keys específicas para Direct Exchange"
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
        
        logger.info("Producer iniciado. Enviando mensagens a cada 3 segundos...")
        logger.info("Pressione Ctrl+C para parar")
        
        message_count = 1
        
        while True:
            for routing_key in ROUTING_KEYS:
                # Prepara a mensagem
                message_data = {
                    "id": message_count,
                    "type": routing_key,
                    "content": f"Mensagem {routing_key} #{message_count}",
                    "timestamp": datetime.now().isoformat(),
                    "scenario": SCENARIO_NAME
                }
                
                message_body = json.dumps(message_data, ensure_ascii=False)
                
                # Propriedades da mensagem
                properties = pika.BasicProperties(
                    delivery_mode=2,  # Mensagem persistente
                    content_type='application/json',
                    timestamp=int(time.time())
                )
                
                # Publica a mensagem
                channel.basic_publish(
                    exchange=EXCHANGE_NAME,
                    routing_key=routing_key,
                    body=message_body,
                    properties=properties
                )
                
                log_message_sent(logger, EXCHANGE_NAME, routing_key, message_body, properties)
                message_count += 1
                
                time.sleep(1)  # Pausa entre mensagens do mesmo tipo
            
            time.sleep(2)  # Pausa entre ciclos
            
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
