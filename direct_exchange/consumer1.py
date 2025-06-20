"""
Consumer 1 para Direct Exchange
Consome mensagens com routing key 'info'
"""
import sys
import os
import json
import time

# Adiciona o diretório pai ao path para importar utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pika
from utils.common import (
    setup_logging, get_rabbitmq_connection, create_exchange_and_queue,
    log_message_received, print_scenario_header, print_config_info
)

def main():
    # Configurações do cenário
    SCENARIO_NAME = "direct_exchange"
    COMPONENT_NAME = "consumer1"
    CONSUMER_ID = "INFO_CONSUMER"
    EXCHANGE_NAME = "direct_exchange_demo"
    EXCHANGE_TYPE = "direct"
    QUEUE_NAME = "direct_queue_info"
    ROUTING_KEY = "info"
    
    # Setup
    print_scenario_header(
        SCENARIO_NAME, 
        COMPONENT_NAME, 
        f"Consumer que processa mensagens com routing key '{ROUTING_KEY}'"
    )
    
    logger = setup_logging(SCENARIO_NAME, COMPONENT_NAME)
    print_config_info(logger)
    
    def callback(ch, method, properties, body):
        """Callback para processar mensagens recebidas"""
        try:
            # Log da mensagem recebida
            log_message_received(logger, method, properties, body, CONSUMER_ID)
            
            # Processa a mensagem
            message_data = json.loads(body.decode('utf-8'))
            
            logger.info(f"[{CONSUMER_ID}] Processando mensagem ID: {message_data.get('id')}")
            logger.info(f"[{CONSUMER_ID}] Conteúdo: {message_data.get('content')}")
            
            # Simula processamento
            time.sleep(1)
            
            # Confirma o processamento
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info(f"[{CONSUMER_ID}] Mensagem processada e confirmada")
            
        except Exception as e:
            logger.error(f"[{CONSUMER_ID}] Erro ao processar mensagem: {str(e)}")
            # Rejeita a mensagem e não recoloca na fila
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    
    try:
        # Conecta ao RabbitMQ
        logger.info("Conectando ao RabbitMQ...")
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        # Configura QoS - processa uma mensagem por vez
        channel.basic_qos(prefetch_count=1)
        
        # Cria exchange, fila e binding (idempotente)
        create_exchange_and_queue(
            channel=channel,
            exchange_name=EXCHANGE_NAME,
            exchange_type=EXCHANGE_TYPE,
            queue_name=QUEUE_NAME,
            routing_key=ROUTING_KEY,
            durable=True
        )
        
        logger.info(f"Exchange '{EXCHANGE_NAME}' declarado")
        logger.info(f"Fila '{QUEUE_NAME}' declarada e vinculada com routing key '{ROUTING_KEY}'")
        
        # Configura o consumer
        channel.basic_consume(
            queue=QUEUE_NAME,
            on_message_callback=callback,
            auto_ack=False  # Confirmação manual
        )
        
        logger.info(f"[{CONSUMER_ID}] Aguardando mensagens. Para sair pressione Ctrl+C")
        
        # Inicia o consumo
        channel.start_consuming()
        
    except KeyboardInterrupt:
        logger.info("Parando consumer...")
        if 'channel' in locals():
            channel.stop_consuming()
    except Exception as e:
        logger.error(f"Erro no consumer: {str(e)}")
    finally:
        if 'connection' in locals() and not connection.is_closed:
            connection.close()
            logger.info("Conexão fechada")

if __name__ == "__main__":
    main()
