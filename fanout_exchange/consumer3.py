"""
Consumer 3 para Fanout Exchange
Processa métricas e estatísticas
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
    COMPONENT_NAME = "consumer3"
    CONSUMER_ID = "METRICS_COLLECTOR"
    EXCHANGE_NAME = "fanout_exchange_demo"
    EXCHANGE_TYPE = "fanout"
    QUEUE_NAME = "fanout_queue_metrics"
    
    # Setup
    print_scenario_header(
        SCENARIO_NAME, 
        COMPONENT_NAME, 
        "Consumer especializado em coletar métricas e estatísticas"
    )
    
    logger = setup_logging(SCENARIO_NAME, COMPONENT_NAME)
    print_config_info(logger)
    
    # Contador de mensagens processadas
    message_count = 0
    
    def callback(ch, method, properties, body):
        """Callback para processar mensagens recebidas"""
        nonlocal message_count
        try:
            # Log da mensagem recebida
            log_message_received(logger, method, properties, body, CONSUMER_ID)
            
            # Processa a mensagem
            message_data = json.loads(body.decode('utf-8'))
            message_count += 1
            
            logger.info(f"[{CONSUMER_ID}] 📊 COLETANDO MÉTRICAS - ID: {message_data.get('id')}")
            logger.info(f"[{CONSUMER_ID}] Total processado: {message_count} mensagens")
            
            # Simula coleta de métricas
            metrics = {
                "message_id": message_data.get('id'),
                "received_at": time.time(),
                "message_size": len(body),
                "total_processed": message_count,
                "scenario": message_data.get('scenario')
            }
            
            logger.info(f"[{CONSUMER_ID}] Métricas coletadas: Size={metrics['message_size']} bytes")
            time.sleep(0.5)  # Simula processamento de métricas
            
            # Confirma o processamento
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info(f"[{CONSUMER_ID}] ✅ Métricas processadas e armazenadas")
            
        except Exception as e:
            logger.error(f"[{CONSUMER_ID}] ❌ Erro ao processar métricas: {str(e)}")
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
        
        logger.info(f"[{CONSUMER_ID}] 📈 Aguardando broadcasts para coleta de métricas. Para sair pressione Ctrl+C")
        
        # Inicia o consumo
        channel.start_consuming()
        
    except KeyboardInterrupt:
        logger.info(f"Parando consumer... Total processado: {message_count} mensagens")
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
