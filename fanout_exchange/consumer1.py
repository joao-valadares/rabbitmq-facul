"""
Consumer 1 para Fanout Exchange
Processa notificações de sistema
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
    SCENARIO_NAME = "fanout_exchange"
    COMPONENT_NAME = "consumer1"
    CONSUMER_ID = "NOTIFICATION_PROCESSOR"
    EXCHANGE_NAME = "fanout_exchange_demo"
    EXCHANGE_TYPE = "fanout"
    QUEUE_NAME = "fanout_queue_notifications"
    
    # Setup
    print_scenario_header(
        SCENARIO_NAME, 
        COMPONENT_NAME, 
        "Consumer especializado em processar notificações do sistema"
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
            
            logger.info(f"[{CONSUMER_ID}] 📢 NOTIFICAÇÃO RECEBIDA - ID: {message_data.get('id')}")
            logger.info(f"[{CONSUMER_ID}] Conteúdo: {message_data.get('content')}")
            logger.info(f"[{CONSUMER_ID}] Anúncio: {message_data.get('announcement')}")
            
            # Simula processamento de notificação
            logger.info(f"[{CONSUMER_ID}] Enviando notificação para interface de usuário...")
            time.sleep(1)
            
            # Confirma o processamento
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info(f"[{CONSUMER_ID}] ✅ Notificação processada e exibida")
            
        except Exception as e:
            logger.error(f"[{CONSUMER_ID}] ❌ Erro ao processar notificação: {str(e)}")
            # Rejeita a mensagem e não recoloca na fila
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    
    try:
        # Conecta ao RabbitMQ
        logger.info("Conectando ao RabbitMQ...")
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        # Configura QoS
        channel.basic_qos(prefetch_count=1)
        
        # Cria exchange e fila (idempotente)
        # Em fanout, routing_key é ignorada, mas ainda precisamos criar o binding
        create_exchange_and_queue(
            channel=channel,
            exchange_name=EXCHANGE_NAME,
            exchange_type=EXCHANGE_TYPE,
            queue_name=QUEUE_NAME,
            routing_key='',  # Ignorada em fanout
            durable=True
        )
        
        logger.info(f"Exchange '{EXCHANGE_NAME}' declarado")
        logger.info(f"Fila '{QUEUE_NAME}' declarada e vinculada ao exchange")
        
        # Configura o consumer
        channel.basic_consume(
            queue=QUEUE_NAME,
            on_message_callback=callback,
            auto_ack=False  # Confirmação manual
        )
        
        logger.info(f"[{CONSUMER_ID}] 🎯 Aguardando broadcasts. Para sair pressione Ctrl+C")
        
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
