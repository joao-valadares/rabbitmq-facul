"""
Consumer 2 para Fanout Exchange
Processa logs de auditoria
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
    COMPONENT_NAME = "consumer2"
    CONSUMER_ID = "AUDIT_LOGGER"
    EXCHANGE_NAME = "fanout_exchange_demo"
    EXCHANGE_TYPE = "fanout"
    QUEUE_NAME = "fanout_queue_audit"
    
    # Setup
    print_scenario_header(
        SCENARIO_NAME, 
        COMPONENT_NAME, 
        "Consumer especializado em registrar logs de auditoria"
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
            
            logger.info(f"[{CONSUMER_ID}] 📝 REGISTRANDO AUDITORIA - ID: {message_data.get('id')}")
            logger.info(f"[{CONSUMER_ID}] Timestamp: {message_data.get('timestamp')}")
            logger.info(f"[{CONSUMER_ID}] Tipo: {message_data.get('type')}")
            
            # Simula gravação em log de auditoria
            audit_record = {
                "audit_id": f"audit_{message_data.get('id')}",
                "original_message": message_data,
                "processed_at": time.time(),
                "processor": CONSUMER_ID
            }
            
            logger.info(f"[{CONSUMER_ID}] Gravando registro de auditoria...")
            time.sleep(0.8)  # Simula I/O de gravação
            
            # Confirma o processamento
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info(f"[{CONSUMER_ID}] ✅ Auditoria registrada com sucesso")
            
        except Exception as e:
            logger.error(f"[{CONSUMER_ID}] ❌ Erro ao registrar auditoria: {str(e)}")
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
        
        logger.info(f"[{CONSUMER_ID}] 📋 Aguardando broadcasts para auditoria. Para sair pressione Ctrl+C")
        
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
