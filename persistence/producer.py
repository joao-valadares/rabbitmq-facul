"""
Producer para Persistence
Demonstra diferença entre mensagens persistentes e transientes
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
    SCENARIO_NAME = "persistence"
    COMPONENT_NAME = "producer"
    EXCHANGE_NAME = ""  # Exchange padrão
    PERSISTENT_QUEUE = "persistent_messages_queue"
    TRANSIENT_QUEUE = "transient_messages_queue"
    
    # Setup
    print_scenario_header(
        SCENARIO_NAME, 
        COMPONENT_NAME, 
        "Producer que demonstra diferença entre mensagens persistentes e transientes"
    )
    
    logger = setup_logging(SCENARIO_NAME, COMPONENT_NAME)
    print_config_info(logger)
    
    try:
        # Conecta ao RabbitMQ
        logger.info("Conectando ao RabbitMQ...")
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        # Declara as filas (idempotente)
        logger.info("Declarando filas...")
        
        # Fila para mensagens persistentes (durable=True)
        channel.queue_declare(
            queue=PERSISTENT_QUEUE,
            durable=True  # Fila sobrevive a reinicializações do broker
        )
        
        # Fila para mensagens transientes (durable=False)
        channel.queue_declare(
            queue=TRANSIENT_QUEUE,
            durable=False  # Fila é perdida se broker reiniciar
        )
        
        logger.info(f"Fila persistente '{PERSISTENT_QUEUE}' declarada (durable=True)")
        logger.info(f"Fila transiente '{TRANSIENT_QUEUE}' declarada (durable=False)")
        logger.info("")
        logger.info("Producer iniciado. Enviando mensagens alternando entre persistente e transiente...")
        logger.info("PERSISTENTE: Sobrevive a reinicializações do RabbitMQ")
        logger.info("TRANSIENTE: Perdida se RabbitMQ reiniciar")
        logger.info("Pressione Ctrl+C para parar")
        
        message_id = 1
        
        while True:
            # Alterna entre persistente e transiente
            is_persistent = (message_id % 2 == 1)
            
            if is_persistent:
                queue_name = PERSISTENT_QUEUE
                delivery_mode = 2  # Mensagem persistente
                durability_type = "PERSISTENTE"
                durability_description = "Sobrevive a reinicializações do broker"
            else:
                queue_name = TRANSIENT_QUEUE
                delivery_mode = 1  # Mensagem transiente (default)
                durability_type = "TRANSIENTE"
                durability_description = "Perdida se broker reiniciar"
            
            # Prepara a mensagem
            message_data = {
                "message_id": message_id,
                "type": durability_type.lower(),
                "durability": durability_type,
                "description": durability_description,
                "content": f"Mensagem {durability_type} #{message_id}",
                "important_data": f"Dados críticos do sistema - ID {message_id}",
                "timestamp": datetime.now().isoformat(),
                "scenario": SCENARIO_NAME,
                "delivery_mode": delivery_mode
            }
            
            message_body = json.dumps(message_data, ensure_ascii=False)
            
            # Propriedades da mensagem
            properties = pika.BasicProperties(
                delivery_mode=delivery_mode,  # 1=transiente, 2=persistente
                content_type='application/json',
                timestamp=int(time.time()),
                headers={
                    'durability': durability_type,
                    'message_type': 'demo'
                }
            )
            
            # Publica a mensagem
            channel.basic_publish(
                exchange=EXCHANGE_NAME,
                routing_key=queue_name,
                body=message_body,
                properties=properties
            )
            
            log_message_sent(logger, "default", queue_name, message_body, properties)
            
            # Log específico sobre persistência
            if is_persistent:
                logger.info(f"💾 PERSISTENTE #{message_id}: Armazenada em disco, sobrevive a reinicializações")
            else:
                logger.info(f"⚡ TRANSIENTE #{message_id}: Apenas em memória, performance otimizada")
            
            logger.info("")
            message_id += 1
            time.sleep(3)  # Pausa para observar diferenças
            
    except KeyboardInterrupt:
        logger.info("Parando producer...")
        logger.info("")
        logger.info("DICA: Para testar persistência:")
        logger.info("1. Deixe mensagens na fila")
        logger.info("2. Reinicie o RabbitMQ")
        logger.info("3. Observe que apenas mensagens PERSISTENTES permanecem")
    except Exception as e:
        logger.error(f"Erro no producer: {str(e)}")
    finally:
        if 'connection' in locals() and not connection.is_closed:
            connection.close()
            logger.info("Conexão fechada")

if __name__ == "__main__":
    main()
