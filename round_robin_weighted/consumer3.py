"""
Consumer 3 para Round Robin Ponderado
Worker avançado com alta capacidade (prefetch=5)
"""
import sys
import os
import json
import time
import threading

# Adiciona o diretório pai ao path para importar utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pika
from utils.common import (
    setup_logging, get_rabbitmq_connection, 
    log_message_received, print_scenario_header, print_config_info
)

def main():
    # Configurações do cenário
    SCENARIO_NAME = "round_robin_weighted"
    COMPONENT_NAME = "consumer3"
    CONSUMER_ID = "ADVANCED_WORKER"
    QUEUE_NAME = "weighted_round_robin_queue"
    PREFETCH_COUNT = 5  # Alta capacidade - 5 tarefas simultâneas
    
    # Setup
    print_scenario_header(
        SCENARIO_NAME, 
        COMPONENT_NAME, 
        f"Worker Avançado - Alta capacidade (prefetch={PREFETCH_COUNT})"
    )
    
    logger = setup_logging(SCENARIO_NAME, COMPONENT_NAME)
    print_config_info(logger)
    
    # Contadores e locks para thread safety
    tasks_processed = 0
    tasks_in_progress = 0
    lock = threading.Lock()
    
    def callback(ch, method, properties, body):
        """Callback para processar tarefas recebidas"""
        nonlocal tasks_processed, tasks_in_progress
        
        with lock:
            tasks_in_progress += 1
            current_in_progress = tasks_in_progress
        
        try:
            # Log da tarefa recebida
            log_message_received(logger, method, properties, body, CONSUMER_ID)
            
            # Processa a tarefa
            task_data = json.loads(body.decode('utf-8'))
            
            task_id = task_data.get('task_id')
            task_type = task_data.get('task_type')
            description = task_data.get('description')
            processing_time = task_data.get('processing_time', 1)
            complexity = task_data.get('complexity', 'low')
            
            logger.info(f"[{CONSUMER_ID}] 🔧 PROCESSANDO TAREFA #{task_id}")
            logger.info(f"[{CONSUMER_ID}] Tipo: {task_type}")
            logger.info(f"[{CONSUMER_ID}] Descrição: {description}")
            logger.info(f"[{CONSUMER_ID}] Complexidade: {complexity}")
            logger.info(f"[{CONSUMER_ID}] Tempo estimado: {processing_time}s")
            logger.info(f"[{CONSUMER_ID}] Tarefas em progresso: {current_in_progress}/{PREFETCH_COUNT}")
            
            # Worker avançado - processamento altamente otimizado (30% mais rápido)
            logger.info(f"[{CONSUMER_ID}] 🚀 Iniciando processamento avançado...")
            optimized_time = max(1, int(processing_time * 0.7))  # 30% mais rápido
            
            # Processamento paralelo simulado para tarefas complexas
            if complexity == 'high':
                logger.info(f"[{CONSUMER_ID}] 🔥 Modo TURBO ativado para tarefa complexa!")
                optimized_time = max(1, int(optimized_time * 0.8))  # Ainda mais rápido para tarefas complexas
            
            for i in range(optimized_time):
                time.sleep(0.8)  # 20% mais rápido que tempo normal
                progress = ((i + 1) / optimized_time) * 100
                efficiency = "TURBO" if complexity == 'high' else "OTIMIZADO"
                logger.info(f"[{CONSUMER_ID}] 📊 Progresso {efficiency}: {progress:.0f}% ({i+1}/{optimized_time}s)")
            
            with lock:
                tasks_processed += 1
                tasks_in_progress -= 1
                total_processed = tasks_processed
            
            logger.info(f"[{CONSUMER_ID}] ✅ Tarefa #{task_id} concluída com performance AVANÇADA!")
            logger.info(f"[{CONSUMER_ID}] Total processado: {total_processed} tarefas")
            
            # Log de performance
            original_time = task_data.get('processing_time', 1)
            time_saved = original_time - optimized_time
            efficiency_gain = (time_saved / original_time) * 100 if original_time > 0 else 0
            logger.info(f"[{CONSUMER_ID}] 📈 Eficiência: {efficiency_gain:.0f}% mais rápido "
                       f"({time_saved}s economizado)")
            
            # Confirma o processamento
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info(f"[{CONSUMER_ID}] 📝 Tarefa confirmada e removida da fila")
            
        except Exception as e:
            logger.error(f"[{CONSUMER_ID}] ❌ Erro ao processar tarefa: {str(e)}")
            with lock:
                tasks_in_progress -= 1
            # Rejeita a tarefa e recoloca na fila para outro worker
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    try:
        # Conecta ao RabbitMQ
        logger.info("Conectando ao RabbitMQ...")
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        # Configura QoS - worker avançado com alta capacidade
        channel.basic_qos(prefetch_count=PREFETCH_COUNT)
        logger.info(f"QoS configurado: prefetch_count={PREFETCH_COUNT} (worker AVANÇADO)")
        
        # Declara a fila (idempotente)
        channel.queue_declare(
            queue=QUEUE_NAME,
            durable=True
        )
        
        logger.info(f"Fila '{QUEUE_NAME}' declarada")
        logger.info(f"Worker Avançado: Processa até {PREFETCH_COUNT} tarefas simultaneamente")
        logger.info("Características: Altamente otimizado, velocidade +30%, alta capacidade, modo TURBO")
        
        # Configura o consumer
        channel.basic_consume(
            queue=QUEUE_NAME,
            on_message_callback=callback,
            auto_ack=False  # Confirmação manual
        )
        
        logger.info(f"[{CONSUMER_ID}] 👷 Worker AVANÇADO ativo e aguardando tarefas...")
        logger.info("Para sair pressione Ctrl+C")
        
        # Inicia o consumo
        channel.start_consuming()
        
    except KeyboardInterrupt:
        logger.info(f"Parando worker avançado... Total processado: {tasks_processed} tarefas")
        if 'channel' in locals():
            channel.stop_consuming()
    except Exception as e:
        logger.error(f"Erro no worker avançado: {str(e)}")
    finally:
        if 'connection' in locals() and not connection.is_closed:
            connection.close()
            logger.info("Conexão fechada")

if __name__ == "__main__":
    main()
