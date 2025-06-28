"""
Consumer 2 para Topic Exchange
Consome mensagens do sistema específico (system.*)
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
    SCENARIO_NAME = "topic_exchange"
    COMPONENT_NAME = "consumer2"
    CONSUMER_ID = "SYSTEM_MONITOR"
    EXCHANGE_NAME = "topic_exchange_demo"
    EXCHANGE_TYPE = "topic"
    QUEUE_NAME = "topic_queue_system"
    ROUTING_PATTERN = "system.*"  # Todas as mensagens do sistema
    
    # Setup
    print_scenario_header(
        SCENARIO_NAME, 
        COMPONENT_NAME, 
        f"Consumer que monitora mensagens do SISTEMA (padrão: {ROUTING_PATTERN})"
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
            
            logger.info(f"[{CONSUMER_ID}] ⚙️ SISTEMA - {message_data.get('subcategory').upper()}")
            logger.info(f"[{CONSUMER_ID}] ID: {message_data.get('id')}")
            logger.info(f"[{CONSUMER_ID}] Routing Key: {message_data.get('routing_key')}")
            logger.info(f"[{CONSUMER_ID}] Módulo: {message_data.get('detail')}")
            logger.info(f"[{CONSUMER_ID}] Conteúdo: {message_data.get('content')}")
            
            # Processamento baseado na severidade
            severity = message_data.get('subcategory')
            if severity == 'error':
                logger.info(f"[{CONSUMER_ID}] 🔴 Processamento de erro de sistema...")
                time.sleep(2)
            elif severity == 'warning':
                logger.info(f"[{CONSUMER_ID}] 🟡 Processamento de warning de sistema...")
                time.sleep(1)
            else:
                logger.info(f"[{CONSUMER_ID}] 🟢 Processamento de info de sistema...")
                time.sleep(0.5)
            
            # Confirma o processamento
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info(f"[{CONSUMER_ID}] ✅ Mensagem de sistema processada")
            
        except Exception as e:
            logger.error(f"[{CONSUMER_ID}] ❌ Erro ao processar mensagem: {str(e)}")
            # Rejeita a mensagem e não recoloca na fila
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    
    try:
        # Conecta ao RabbitMQ
        logger.info("Conectando ao RabbitMQ...")
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        # Configura QoS
        channel.basic_qos(prefetch_count=1)
        
        # Declara o exchange (idempotente)
        channel.exchange_declare(
            exchange=EXCHANGE_NAME,
            exchange_type=EXCHANGE_TYPE,
            durable=True
        )
        
        # Declara a fila (idempotente)
        channel.queue_declare(
            queue=QUEUE_NAME,
            durable=True
        )
        
        # Cria o binding para Topic Exchange
        channel.queue_bind(
            exchange=EXCHANGE_NAME,
            queue=QUEUE_NAME,
            routing_key=ROUTING_PATTERN
        )
        
        logger.info(f"Exchange '{EXCHANGE_NAME}' declarado")
        logger.info(f"Fila '{QUEUE_NAME}' declarada e vinculada com padrão '{ROUTING_PATTERN}'")
        logger.info(f"Receberá: system.info.*, system.warning.*, system.error.*")
        
        # Configura o consumer
        channel.basic_consume(
            queue=QUEUE_NAME,
            on_message_callback=callback,
            auto_ack=False  # Confirmação manual
        )
        
        logger.info(f"[{CONSUMER_ID}] 🖥️ Monitorando mensagens de SISTEMA. Para sair pressione Ctrl+C")
        
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
