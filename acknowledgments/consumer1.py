"""
Consumer 1 para Acknowledgments
Demonstra AUTO ACK (risco de perda de mensagem)
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
    COMPONENT_NAME = "consumer1"
    CONSUMER_ID = "AUTO_ACK_PROCESSOR"
    QUEUE_NAME = "auto_ack_queue"
    
    # Setup
    print_scenario_header(
        SCENARIO_NAME, 
        COMPONENT_NAME, 
        "Consumer com AUTO ACK - Rápido mas com risco de perda de mensagem"
    )
    
    logger = setup_logging(SCENARIO_NAME, COMPONENT_NAME)
    print_config_info(logger)
    
    # Contadores
    processed_count = 0
    failed_count = 0
    
    def callback(ch, method, properties, body):
        """Callback para processar tarefas com auto-ack"""
        nonlocal processed_count, failed_count
        
        try:
            # Log da tarefa recebida
            log_message_received(logger, method, properties, body, CONSUMER_ID)
            
            # IMPORTANTE: Com auto_ack=True, a mensagem JÁ FOI REMOVIDA da fila
            logger.info(f"[{CONSUMER_ID}] ⚠️ MENSAGEM JÁ REMOVIDA DA FILA (auto_ack=True)")
            
            # Processa a tarefa
            task_data = json.loads(body.decode('utf-8'))
            
            task_id = task_data.get('task_id')
            task_type = task_data.get('task_type')
            ack_type = task_data.get('ack_type')
            processing_time = task_data.get('processing_time', 2)
            failure_simulation = task_data.get('failure_simulation', False)
            
            logger.info(f"[{CONSUMER_ID}] ⚡ PROCESSANDO TAREFA AUTO-ACK #{task_id}")
            logger.info(f"[{CONSUMER_ID}] Tipo: {task_type}")
            logger.info(f"[{CONSUMER_ID}] ACK: {ack_type}")
            logger.info(f"[{CONSUMER_ID}] Tempo estimado: {processing_time}s")
            
            # Simula processamento
            logger.info(f"[{CONSUMER_ID}] 🚀 Iniciando processamento rápido...")
            
            for i in range(processing_time):
                time.sleep(1)
                
                # Simula falha durante processamento
                if failure_simulation and i == processing_time - 1:
                    raise Exception(f"Falha simulada durante processamento da tarefa {task_id}")
                
                logger.info(f"[{CONSUMER_ID}] 📊 Progresso: {i+1}/{processing_time}s")
            
            processed_count += 1
            logger.info(f"[{CONSUMER_ID}] ✅ Tarefa #{task_id} processada com sucesso!")
            logger.info(f"[{CONSUMER_ID}] 📈 Total processado: {processed_count}")
            
            # Nota: Não há basic_ack aqui porque auto_ack=True
            
        except Exception as e:
            failed_count += 1
            logger.error(f"[{CONSUMER_ID}] ❌ FALHA NA TAREFA #{task_data.get('task_id', 'unknown')}: {str(e)}")
            logger.error(f"[{CONSUMER_ID}] 💥 PROBLEMA: Mensagem já foi removida da fila!")
            logger.error(f"[{CONSUMER_ID}] 🚨 TAREFA PERDIDA - Não pode ser reprocessada!")
            logger.error(f"[{CONSUMER_ID}] 📉 Total falhado: {failed_count}")
            logger.error("")
            
            # Com auto_ack, não há como recuperar a mensagem perdida
    
    try:
        # Conecta ao RabbitMQ
        logger.info("Conectando ao RabbitMQ...")
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        # Configura QoS
        channel.basic_qos(prefetch_count=3)  # Mais mensagens para demonstrar risco
        
        # Declara a fila (idempotente)
        channel.queue_declare(
            queue=QUEUE_NAME,
            durable=True
        )
        
        logger.info(f"Fila '{QUEUE_NAME}' declarada")
        logger.info("Configuração AUTO ACK:")
        logger.info("  ✅ Vantagens: Processamento rápido, sem overhead de confirmação")
        logger.info("  ❌ Desvantagens: Risco de perda de mensagem em caso de falha")
        logger.info("  ⚠️ RISCO: Mensagem é removida da fila ANTES do processamento")
        logger.info("")
        
        # Configura o consumer com AUTO ACK
        channel.basic_consume(
            queue=QUEUE_NAME,
            on_message_callback=callback,
            auto_ack=True  # ⚠️ AUTO ACK - RISCO DE PERDA
        )
        
        logger.info(f"[{CONSUMER_ID}] ⚡ Consumer AUTO-ACK ativo...")
        logger.info("⚠️ ATENÇÃO: Mensagens são removidas IMEDIATAMENTE da fila")
        logger.info("Para sair pressione Ctrl+C")
        
        # Inicia o consumo
        channel.start_consuming()
        
    except KeyboardInterrupt:
        logger.info(f"Parando consumer...")
        logger.info(f"📊 Estatísticas finais:")
        logger.info(f"  ✅ Processado: {processed_count}")
        logger.info(f"  ❌ Falhado: {failed_count}")
        logger.info(f"  💥 Mensagens perdidas: {failed_count} (não podem ser recuperadas)")
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
