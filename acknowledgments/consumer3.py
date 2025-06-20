"""
Consumer 3 para Acknowledgments
Demonstra diferentes estratégias de ACK (accept, reject, requeue)
"""
import sys
import os
import json
import time
import random

# Adiciona o diretório pai ao path para importar utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pika
from utils.common import (
    setup_logging, get_rabbitmq_connection, 
    log_message_received, print_scenario_header, print_config_info
)

def main():
    # Configurações do cenário
    SCENARIO_NAME = "acknowledgments"
    COMPONENT_NAME = "consumer3"
    CONSUMER_ID = "SMART_ACK_PROCESSOR"
    QUEUE_NAME = "manual_ack_queue"  # Compartilha com consumer2
    
    # Setup
    print_scenario_header(
        SCENARIO_NAME, 
        COMPONENT_NAME, 
        "Consumer inteligente com estratégias avançadas de ACK"
    )
    
    logger = setup_logging(SCENARIO_NAME, COMPONENT_NAME)
    print_config_info(logger)
    
    # Contadores e controle
    stats = {
        'processed': 0,
        'rejected': 0,
        'requeued': 0,
        'retries': {}  # tracking de tentativas por task_id
    }
    
    MAX_RETRIES = 3
    
    def callback(ch, method, properties, body):
        """Callback inteligente com diferentes estratégias de ACK"""
        try:
            # Log da tarefa recebida
            log_message_received(logger, method, properties, body, CONSUMER_ID)
            
            # Processa a tarefa
            task_data = json.loads(body.decode('utf-8'))
            
            task_id = task_data.get('task_id')
            task_type = task_data.get('task_type')
            processing_time = task_data.get('processing_time', 2)
            failure_simulation = task_data.get('failure_simulation', False)
            
            # Rastreia tentativas de reprocessamento
            retry_count = stats['retries'].get(str(task_id), 0)
            stats['retries'][str(task_id)] = retry_count + 1
            
            logger.info(f"[{CONSUMER_ID}] 🧠 PROCESSAMENTO INTELIGENTE #{task_id}")
            logger.info(f"[{CONSUMER_ID}] Tipo: {task_type}")
            logger.info(f"[{CONSUMER_ID}] Tentativa: {retry_count + 1}/{MAX_RETRIES + 1}")
            logger.info(f"[{CONSUMER_ID}] Tempo estimado: {processing_time}s")
            
            # Simula processamento
            logger.info(f"[{CONSUMER_ID}] 🧠 Analisando tarefa antes do processamento...")
            time.sleep(0.5)
            
            # Estratégia baseada no número de tentativas
            if retry_count >= MAX_RETRIES:
                logger.error(f"[{CONSUMER_ID}] 🚫 LIMITE DE TENTATIVAS atingido para tarefa #{task_id}")
                logger.error(f"[{CONSUMER_ID}] 🗑️ REJEITANDO tarefa permanentemente")
                
                # REJECT sem requeue - descarta a mensagem problemática
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                stats['rejected'] += 1
                
                logger.error(f"[{CONSUMER_ID}] ❌ Tarefa #{task_id} REJEITADA (dead letter)")
                logger.error(f"[{CONSUMER_ID}] Total rejeitado: {stats['rejected']}")
                return
            
            # Processamento normal
            for i in range(processing_time):
                time.sleep(0.8)
                
                # Decisão inteligente sobre falhas
                if failure_simulation and i == processing_time - 1:
                    # Simula diferentes tipos de erro
                    error_types = [
                        "network_timeout",
                        "database_error", 
                        "invalid_data",
                        "service_unavailable"
                    ]
                    error_type = random.choice(error_types)
                    
                    logger.error(f"[{CONSUMER_ID}] ⚠️ Erro detectado: {error_type}")
                    
                    # Estratégia baseada no tipo de erro
                    if error_type in ["network_timeout", "service_unavailable"]:
                        logger.error(f"[{CONSUMER_ID}] 🔄 Erro temporário - REQUEUING para nova tentativa")
                        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                        stats['requeued'] += 1
                        return
                    elif error_type == "invalid_data":
                        logger.error(f"[{CONSUMER_ID}] 🚫 Dados inválidos - REJEITANDO permanentemente")
                        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                        stats['rejected'] += 1
                        return
                    else:
                        # database_error - tentar algumas vezes
                        raise Exception(f"Erro de banco: {error_type}")
                
                logger.info(f"[{CONSUMER_ID}] 📊 Progresso: {i+1}/{processing_time}s")
            
            # Sucesso - ACK normal
            ch.basic_ack(delivery_tag=method.delivery_tag)
            stats['processed'] += 1
            
            # Remove do controle de retry
            if str(task_id) in stats['retries']:
                del stats['retries'][str(task_id)]
            
            logger.info(f"[{CONSUMER_ID}] ✅ Tarefa #{task_id} processada com SUCESSO!")
            logger.info(f"[{CONSUMER_ID}] 📈 Total processado: {stats['processed']}")
            
        except Exception as e:
            logger.error(f"[{CONSUMER_ID}] ❌ Erro no processamento: {str(e)}")
            logger.error(f"[{CONSUMER_ID}] 🔄 REQUEUING para nova tentativa...")
            
            # NACK com requeue para tentar novamente
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            stats['requeued'] += 1
            
            logger.error(f"[{CONSUMER_ID}] Total recolocado: {stats['requeued']}")
    
    try:
        # Conecta ao RabbitMQ
        logger.info("Conectando ao RabbitMQ...")
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        # Configura QoS
        channel.basic_qos(prefetch_count=1)
        
        # Declara a fila (idempotente)
        channel.queue_declare(
            queue=QUEUE_NAME,
            durable=True
        )
        
        logger.info(f"Fila '{QUEUE_NAME}' declarada")
        logger.info("Estratégias INTELIGENTES de ACK:")
        logger.info("  ✅ ACK: Processamento bem-sucedido")
        logger.info("  🔄 NACK + Requeue: Erro temporário, tentar novamente")
        logger.info("  🚫 NACK + No Requeue: Erro permanente, descartar")
        logger.info(f"  📊 Limite de tentativas: {MAX_RETRIES}")
        logger.info("")
        
        # Configura o consumer
        channel.basic_consume(
            queue=QUEUE_NAME,
            on_message_callback=callback,
            auto_ack=False
        )
        
        logger.info(f"[{CONSUMER_ID}] 🧠 Consumer INTELIGENTE ativo...")
        logger.info("🎯 Estratégias baseadas no tipo de erro e número de tentativas")
        logger.info("Para sair pressione Ctrl+C")
        
        # Inicia o consumo
        channel.start_consuming()
        
    except KeyboardInterrupt:
        logger.info(f"Parando consumer...")
        logger.info(f"📊 Estatísticas finais:")
        logger.info(f"  ✅ Processado: {stats['processed']}")
        logger.info(f"  🔄 Recolocado: {stats['requeued']}")
        logger.info(f"  🚫 Rejeitado: {stats['rejected']}")
        logger.info(f"  🔄 Em retry: {len(stats['retries'])} tarefas")
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
