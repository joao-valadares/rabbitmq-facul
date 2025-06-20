"""
Consumer 3 para Persistence
Demonstra monitoramento de ambos os tipos de mensagem (persistente e transiente)
"""
import sys
import os
import json
import time

# Adiciona o diretório pai ao path para importar utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pika
from utils.common import (
    setup_logging, get_rabbitmq_connection, 
    log_message_received, print_scenario_header, print_config_info
)

def main():
    # Configurações do cenário
    SCENARIO_NAME = "persistence"
    COMPONENT_NAME = "consumer3"
    CONSUMER_ID = "PERSISTENCE_MONITOR"
    PERSISTENT_QUEUE = "persistent_messages_queue"
    TRANSIENT_QUEUE = "transient_messages_queue"
    
    # Setup
    print_scenario_header(
        SCENARIO_NAME, 
        COMPONENT_NAME, 
        "Monitor que observa diferenças entre mensagens persistentes e transientes"
    )
    
    logger = setup_logging(SCENARIO_NAME, COMPONENT_NAME)
    print_config_info(logger)
    
    # Contadores
    stats = {
        'persistent': {'count': 0, 'total_time': 0},
        'transient': {'count': 0, 'total_time': 0}
    }
    
    def callback_persistent(ch, method, properties, body):
        """Callback para mensagens persistentes"""
        start_time = time.time()
        try:
            log_message_received(logger, method, properties, body, f"{CONSUMER_ID}_PERSISTENT")
            
            message_data = json.loads(body.decode('utf-8'))
            message_id = message_data.get('message_id')
            
            stats['persistent']['count'] += 1
            
            logger.info(f"[{CONSUMER_ID}] 💾 PERSISTENTE #{message_id} - Monitorando...")
            time.sleep(0.3)  # Simula monitoramento
            
            processing_time = time.time() - start_time
            stats['persistent']['total_time'] += processing_time
            avg_time = stats['persistent']['total_time'] / stats['persistent']['count']
            
            logger.info(f"[{CONSUMER_ID}] 📊 Stats PERSISTENTE: Count={stats['persistent']['count']}, "
                       f"Avg Time={avg_time:.2f}s")
            
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except Exception as e:
            logger.error(f"[{CONSUMER_ID}] ❌ Erro monitoramento persistente: {str(e)}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    def callback_transient(ch, method, properties, body):
        """Callback para mensagens transientes"""
        start_time = time.time()
        try:
            log_message_received(logger, method, properties, body, f"{CONSUMER_ID}_TRANSIENT")
            
            message_data = json.loads(body.decode('utf-8'))
            message_id = message_data.get('message_id')
            
            stats['transient']['count'] += 1
            
            logger.info(f"[{CONSUMER_ID}] ⚡ TRANSIENTE #{message_id} - Monitorando...")
            time.sleep(0.1)  # Monitoramento mais rápido
            
            processing_time = time.time() - start_time
            stats['transient']['total_time'] += processing_time
            avg_time = stats['transient']['total_time'] / stats['transient']['count']
            
            logger.info(f"[{CONSUMER_ID}] 📊 Stats TRANSIENTE: Count={stats['transient']['count']}, "
                       f"Avg Time={avg_time:.2f}s")
            
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except Exception as e:
            logger.error(f"[{CONSUMER_ID}] ❌ Erro monitoramento transiente: {str(e)}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    
    try:
        # Conecta ao RabbitMQ
        logger.info("Conectando ao RabbitMQ...")
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        # Configura QoS
        channel.basic_qos(prefetch_count=2)
        
        # Declara ambas as filas
        channel.queue_declare(queue=PERSISTENT_QUEUE, durable=True)
        channel.queue_declare(queue=TRANSIENT_QUEUE, durable=False)
        
        logger.info("Monitor configurado para ambas as filas:")
        logger.info(f"  - {PERSISTENT_QUEUE} (persistente)")
        logger.info(f"  - {TRANSIENT_QUEUE} (transiente)")
        logger.info("")
        
        # Configura consumers para ambas as filas
        channel.basic_consume(
            queue=PERSISTENT_QUEUE,
            on_message_callback=callback_persistent,
            auto_ack=False
        )
        
        channel.basic_consume(
            queue=TRANSIENT_QUEUE,
            on_message_callback=callback_transient,
            auto_ack=False
        )
        
        logger.info(f"[{CONSUMER_ID}] 📊 Monitor ativo para ambos os tipos de mensagem...")
        logger.info("Para sair pressione Ctrl+C")
        
        # Inicia o consumo
        channel.start_consuming()
        
    except KeyboardInterrupt:
        logger.info("Parando monitor...")
        logger.info("\n=== ESTATÍSTICAS FINAIS ===")
        logger.info(f"PERSISTENTES: {stats['persistent']['count']} mensagens")
        if stats['persistent']['count'] > 0:
            avg_persistent = stats['persistent']['total_time'] / stats['persistent']['count']
            logger.info(f"  Tempo médio: {avg_persistent:.2f}s")
        
        logger.info(f"TRANSIENTES: {stats['transient']['count']} mensagens")
        if stats['transient']['count'] > 0:
            avg_transient = stats['transient']['total_time'] / stats['transient']['count']
            logger.info(f"  Tempo médio: {avg_transient:.2f}s")
        
        if 'channel' in locals():
            channel.stop_consuming()
    except Exception as e:
        logger.error(f"Erro no monitor: {str(e)}")
    finally:
        if 'connection' in locals() and not connection.is_closed:
            connection.close()
            logger.info("Conexão fechada")

if __name__ == "__main__":
    main()
