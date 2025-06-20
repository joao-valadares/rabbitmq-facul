"""
Producer para Acknowledgments
Demonstra cenário onde confirmação de mensagem é crítica
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
    SCENARIO_NAME = "acknowledgments"
    COMPONENT_NAME = "producer"
    EXCHANGE_NAME = ""  # Exchange padrão
    AUTO_ACK_QUEUE = "auto_ack_queue"
    MANUAL_ACK_QUEUE = "manual_ack_queue"
    
    # Setup
    print_scenario_header(
        SCENARIO_NAME, 
        COMPONENT_NAME, 
        "Producer que demonstra importância de acknowledgments em diferentes cenários"
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
        
        # Fila para auto-acknowledgment (risco de perda)
        channel.queue_declare(
            queue=AUTO_ACK_QUEUE,
            durable=True
        )
        
        # Fila para manual acknowledgment (seguro)
        channel.queue_declare(
            queue=MANUAL_ACK_QUEUE,
            durable=True
        )
        
        logger.info(f"Fila '{AUTO_ACK_QUEUE}' - Auto ACK (risco de perda)")
        logger.info(f"Fila '{MANUAL_ACK_QUEUE}' - Manual ACK (processamento seguro)")
        logger.info("")
        logger.info("Producer iniciado. Enviando tarefas críticas...")
        logger.info("AUTO ACK: Mensagem removida imediatamente da fila (risco)")
        logger.info("MANUAL ACK: Mensagem removida apenas após confirmação (seguro)")
        logger.info("Pressione Ctrl+C para parar")
        
        task_id = 1
        
        while True:
            # Alterna entre tipos de acknowledgment
            is_manual_ack = (task_id % 2 == 1)
            
            if is_manual_ack:
                queue_name = MANUAL_ACK_QUEUE
                ack_type = "MANUAL"
                description = "Processamento seguro com confirmação manual"
                risk_level = "BAIXO"
            else:
                queue_name = AUTO_ACK_QUEUE
                ack_type = "AUTO"
                description = "Processamento rápido mas com risco de perda"
                risk_level = "ALTO"
            
            # Simula diferentes tipos de tarefas críticas
            critical_tasks = [
                "payment_processing",
                "order_fulfillment", 
                "user_registration",
                "inventory_update",
                "email_notification"
            ]
            
            task_type = random.choice(critical_tasks)
            
            # Prepara a tarefa
            task_data = {
                "task_id": task_id,
                "task_type": task_type,
                "ack_type": ack_type,
                "description": description,
                "risk_level": risk_level,
                "content": f"Tarefa crítica {task_type} #{task_id}",
                "processing_time": random.randint(2, 5),
                "failure_simulation": random.choice([False, False, False, True]),  # 25% chance de falha
                "timestamp": datetime.now().isoformat(),
                "scenario": SCENARIO_NAME
            }
            
            message_body = json.dumps(task_data, ensure_ascii=False)
            
            # Propriedades da mensagem
            properties = pika.BasicProperties(
                delivery_mode=2,  # Mensagem persistente
                content_type='application/json',
                timestamp=int(time.time()),
                headers={
                    'ack_type': ack_type,
                    'task_type': task_type,
                    'risk_level': risk_level
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
            
            # Log específico sobre acknowledgment
            if is_manual_ack:
                logger.info(f"🔒 MANUAL ACK #{task_id}: Tarefa {task_type} - Processamento SEGURO")
                logger.info(f"   Risco: {risk_level} - Mensagem só sai da fila após confirmação")
            else:
                logger.info(f"⚡ AUTO ACK #{task_id}: Tarefa {task_type} - Processamento RÁPIDO")
                logger.info(f"   Risco: {risk_level} - Mensagem sai da fila IMEDIATAMENTE")
            
            logger.info("")
            task_id += 1
            time.sleep(3)  # Pausa entre tarefas
            
    except KeyboardInterrupt:
        logger.info("Parando producer...")
        logger.info("")
        logger.info("DICA: Para testar acknowledgments:")
        logger.info("1. Execute os consumers")
        logger.info("2. Observe comportamento quando consumers falham")
        logger.info("3. Auto ACK: mensagens são perdidas")
        logger.info("4. Manual ACK: mensagens retornam à fila")
    except Exception as e:
        logger.error(f"Erro no producer: {str(e)}")
    finally:
        if 'connection' in locals() and not connection.is_closed:
            connection.close()
            logger.info("Conexão fechada")

if __name__ == "__main__":
    main()
