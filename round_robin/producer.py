"""
Producer para Round Robin
Demonstra balanceamento de carga simples entre múltiplos consumers
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
    SCENARIO_NAME = "round_robin"
    COMPONENT_NAME = "producer"
    EXCHANGE_NAME = ""  # Exchange padrão (default)
    QUEUE_NAME = "round_robin_work_queue"
    
    # Setup
    print_scenario_header(
        SCENARIO_NAME, 
        COMPONENT_NAME, 
        "Producer que distribui tarefas para workers em round-robin"
    )
    
    logger = setup_logging(SCENARIO_NAME, COMPONENT_NAME)
    print_config_info(logger)
    
    try:
        # Conecta ao RabbitMQ
        logger.info("Conectando ao RabbitMQ...")
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        # Declara a fila de trabalho (idempotente)
        logger.info(f"Declarando fila de trabalho '{QUEUE_NAME}'")
        channel.queue_declare(
            queue=QUEUE_NAME,
            durable=True  # Fila persistente
        )
        
        logger.info("Producer iniciado. Enviando tarefas para distribuição...")
        logger.info("As tarefas serão distribuídas em round-robin entre os workers")
        logger.info("Pressione Ctrl+C para parar")
        
        task_id = 1
        
        while True:
            # Simula diferentes tipos de tarefas
            task_types = ["image_processing", "data_analysis", "report_generation", "email_sending", "backup_task"]
            task_type = task_types[(task_id - 1) % len(task_types)]
            
            # Simula diferentes complexidades (tempo de processamento)
            complexities = {
                "image_processing": {"time": 3, "description": "Processamento de imagem"},
                "data_analysis": {"time": 5, "description": "Análise de dados"},
                "report_generation": {"time": 2, "description": "Geração de relatório"},
                "email_sending": {"time": 1, "description": "Envio de email"},
                "backup_task": {"time": 4, "description": "Tarefa de backup"}
            }
            
            task_info = complexities[task_type]
            
            # Prepara a tarefa
            task_data = {
                "task_id": task_id,
                "task_type": task_type,
                "description": task_info["description"],
                "estimated_time": task_info["time"],
                "created_at": datetime.now().isoformat(),
                "scenario": SCENARIO_NAME,
                "payload": f"Dados da tarefa #{task_id} - {task_type}"
            }
            
            message_body = json.dumps(task_data, ensure_ascii=False)
            
            # Propriedades da mensagem
            properties = pika.BasicProperties(
                delivery_mode=2,  # Mensagem persistente
                content_type='application/json',
                timestamp=int(time.time()),
                headers={
                    'task_type': task_type,
                    'estimated_time': task_info["time"]
                }
            )
            
            # Publica na fila (usando exchange padrão)
            channel.basic_publish(
                exchange=EXCHANGE_NAME,  # Exchange padrão
                routing_key=QUEUE_NAME,  # Nome da fila como routing key
                body=message_body,
                properties=properties
            )
            
            log_message_sent(logger, "default", QUEUE_NAME, message_body, properties)
            logger.info(f"Tarefa #{task_id} ({task_type}) enviada - Tempo estimado: {task_info['time']}s")
            
            task_id += 1
            time.sleep(2)  # Pausa entre tarefas
            
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
