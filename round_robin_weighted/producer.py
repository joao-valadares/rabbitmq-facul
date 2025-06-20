"""
Producer para Round Robin Ponderado
Demonstra balanceamento de carga ponderado usando prefetch diferente por consumer
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
    SCENARIO_NAME = "round_robin_weighted"
    COMPONENT_NAME = "producer"
    EXCHANGE_NAME = ""  # Exchange padrão (default)
    QUEUE_NAME = "weighted_round_robin_queue"
    
    # Setup
    print_scenario_header(
        SCENARIO_NAME, 
        COMPONENT_NAME, 
        "Producer que distribui tarefas para workers com capacidades diferentes (ponderado)"
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
        
        logger.info("Producer iniciado. Enviando tarefas para distribuição ponderada...")
        logger.info("Workers têm capacidades diferentes:")
        logger.info("  - Worker 1 (Básico): prefetch=1 (1 tarefa simultânea)")
        logger.info("  - Worker 2 (Médio): prefetch=3 (3 tarefas simultâneas)")
        logger.info("  - Worker 3 (Avançado): prefetch=5 (5 tarefas simultâneas)")
        logger.info("Pressione Ctrl+C para parar")
        
        task_id = 1
        
        while True:
            # Simula diferentes tipos de tarefas com complexidades variadas
            task_types = [
                {"type": "quick_task", "time": 1, "description": "Tarefa rápida"},
                {"type": "medium_task", "time": 2, "description": "Tarefa média"},
                {"type": "complex_task", "time": 3, "description": "Tarefa complexa"},
                {"type": "batch_job", "time": 4, "description": "Job de lote"},
                {"type": "heavy_processing", "time": 5, "description": "Processamento pesado"}
            ]
            
            # Escolhe tipo de tarefa baseado no ID (para variedade)
            task_info = task_types[(task_id - 1) % len(task_types)]
            
            # Prepara a tarefa
            task_data = {
                "task_id": task_id,
                "task_type": task_info["type"],
                "description": task_info["description"],
                "processing_time": task_info["time"],
                "complexity": "high" if task_info["time"] > 3 else "medium" if task_info["time"] > 1 else "low",
                "created_at": datetime.now().isoformat(),
                "scenario": SCENARIO_NAME,
                "payload": f"Dados da tarefa #{task_id} - {task_info['type']}"
            }
            
            message_body = json.dumps(task_data, ensure_ascii=False)
            
            # Propriedades da mensagem
            properties = pika.BasicProperties(
                delivery_mode=2,  # Mensagem persistente
                content_type='application/json',
                timestamp=int(time.time()),
                headers={
                    'task_type': task_info["type"],
                    'processing_time': task_info["time"],
                    'complexity': task_data["complexity"]
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
            logger.info(f"Tarefa #{task_id} ({task_info['type']}) enviada - "
                       f"Tempo: {task_info['time']}s, Complexidade: {task_data['complexity']}")
            
            task_id += 1
            time.sleep(1.5)  # Pausa menor para gerar mais carga
            
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
