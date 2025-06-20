"""
Consumer 1 para Round Robin
Worker que processa tarefas da fila compartilhada
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
    SCENARIO_NAME = "round_robin"
    COMPONENT_NAME = "consumer1"
    CONSUMER_ID = "WORKER_1"
    QUEUE_NAME = "round_robin_work_queue"
    
    # Setup
    print_scenario_header(
        SCENARIO_NAME, 
        COMPONENT_NAME, 
        "Worker 1 - Processa tarefas da fila compartilhada em round-robin"
    )
    
    logger = setup_logging(SCENARIO_NAME, COMPONENT_NAME)
    print_config_info(logger)
    
    # Contador de tarefas processadas
    tasks_processed = 0
    
    def callback(ch, method, properties, body):
        """Callback para processar tarefas recebidas"""
        nonlocal tasks_processed
        try:
            # Log da tarefa recebida
            log_message_received(logger, method, properties, body, CONSUMER_ID)
            
            # Processa a tarefa
            task_data = json.loads(body.decode('utf-8'))
            tasks_processed += 1
            
            task_id = task_data.get('task_id')
            task_type = task_data.get('task_type')
            description = task_data.get('description')
            estimated_time = task_data.get('estimated_time', 1)
            
            logger.info(f"[{CONSUMER_ID}] 🔧 PROCESSANDO TAREFA #{task_id}")
            logger.info(f"[{CONSUMER_ID}] Tipo: {task_type}")
            logger.info(f"[{CONSUMER_ID}] Descrição: {description}")
            logger.info(f"[{CONSUMER_ID}] Tempo estimado: {estimated_time}s")
            logger.info(f"[{CONSUMER_ID}] Total processado: {tasks_processed} tarefas")
            
            # Simula o processamento da tarefa
            logger.info(f"[{CONSUMER_ID}] 🚀 Iniciando processamento...")
            for i in range(estimated_time):
                time.sleep(1)
                logger.info(f"[{CONSUMER_ID}] 📊 Progresso: {i+1}/{estimated_time}s")
            
            logger.info(f"[{CONSUMER_ID}] ✅ Tarefa #{task_id} concluída com sucesso!")
            
            # Confirma o processamento
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info(f"[{CONSUMER_ID}] 📝 Tarefa confirmada e removida da fila")
            
        except Exception as e:
            logger.error(f"[{CONSUMER_ID}] ❌ Erro ao processar tarefa: {str(e)}")
            # Rejeita a tarefa e recoloca na fila para outro worker
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    try:
        # Conecta ao RabbitMQ
        logger.info("Conectando ao RabbitMQ...")
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        # Configura QoS - processa uma tarefa por vez (fair dispatch)
        channel.basic_qos(prefetch_count=1)
        logger.info("QoS configurado: prefetch_count=1 (uma tarefa por vez)")
        
        # Declara a fila (idempotente)
        channel.queue_declare(
            queue=QUEUE_NAME,
            durable=True
        )
        
        logger.info(f"Fila '{QUEUE_NAME}' declarada")
        logger.info("Configuração Round Robin: Cada worker pega uma tarefa por vez")
        
        # Configura o consumer
        channel.basic_consume(
            queue=QUEUE_NAME,
            on_message_callback=callback,
            auto_ack=False  # Confirmação manual para garantir processamento
        )
        
        logger.info(f"[{CONSUMER_ID}] 👷 Worker ativo e aguardando tarefas...")
        logger.info("Para sair pressione Ctrl+C")
        
        # Inicia o consumo
        channel.start_consuming()
        
    except KeyboardInterrupt:
        logger.info(f"Parando worker... Total processado: {tasks_processed} tarefas")
        if 'channel' in locals():
            channel.stop_consuming()
    except Exception as e:
        logger.error(f"Erro no worker: {str(e)}")
    finally:
        if 'connection' in locals() and not connection.is_closed:
            connection.close()
            logger.info("Conexão fechada")

if __name__ == "__main__":
    main()
