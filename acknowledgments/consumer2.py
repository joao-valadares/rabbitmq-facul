"""
Consumer 2 para Acknowledgments
Demonstra MANUAL ACK (processamento seguro)
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
    SCENARIO_NAME = "acknowledgments"
    COMPONENT_NAME = "consumer2"
    CONSUMER_ID = "MANUAL_ACK_PROCESSOR"
    QUEUE_NAME = "manual_ack_queue"
    
    # Setup
    print_scenario_header(
        SCENARIO_NAME, 
        COMPONENT_NAME, 
        "Consumer com MANUAL ACK - Seguro, não perde mensagens"
    )
    
    logger = setup_logging(SCENARIO_NAME, COMPONENT_NAME)
    print_config_info(logger)
    
    # Contadores
    processed_count = 0
    failed_count = 0
    requeued_count = 0
    
    def callback(ch, method, properties, body):
        """Callback para processar tarefas com manual-ack"""
        nonlocal processed_count, failed_count, requeued_count
        
        try:
            # Log da tarefa recebida
            log_message_received(logger, method, properties, body, CONSUMER_ID)
            
            # Com manual ack, mensagem permanece na fila até confirmação
            logger.info(f"[{CONSUMER_ID}] 🔒 MENSAGEM PERMANECE NA FILA (manual_ack)")
            
            # Processa a tarefa
            task_data = json.loads(body.decode('utf-8'))
            
            task_id = task_data.get('task_id')
            task_type = task_data.get('task_type')
            ack_type = task_data.get('ack_type')
            processing_time = task_data.get('processing_time', 2)
            failure_simulation = task_data.get('failure_simulation', False)
            
            logger.info(f"[{CONSUMER_ID}] 🔒 PROCESSANDO TAREFA MANUAL-ACK #{task_id}")
            logger.info(f"[{CONSUMER_ID}] Tipo: {task_type}")
            logger.info(f"[{CONSUMER_ID}] ACK: {ack_type}")
            logger.info(f"[{CONSUMER_ID}] Tempo estimado: {processing_time}s")
            
            # Simula processamento
            logger.info(f"[{CONSUMER_ID}] 🛡️ Iniciando processamento seguro...")
            
            for i in range(processing_time):
                time.sleep(1)
                
                # Simula falha durante processamento
                if failure_simulation and i == processing_time - 1:
                    raise Exception(f"Falha simulada durante processamento da tarefa {task_id}")
                
                logger.info(f"[{CONSUMER_ID}] 📊 Progresso: {i+1}/{processing_time}s")
            
            # Sucesso - confirma o processamento
            ch.basic_ack(delivery_tag=method.delivery_tag)
            processed_count += 1
            
            logger.info(f"[{CONSUMER_ID}] ✅ Tarefa #{task_id} processada e CONFIRMADA!")
            logger.info(f"[{CONSUMER_ID}] 📝 Mensagem removida da fila com segurança")
            logger.info(f"[{CONSUMER_ID}] 📈 Total processado: {processed_count}")
            
        except Exception as e:
            failed_count += 1
            
            logger.error(f"[{CONSUMER_ID}] ❌ FALHA NA TAREFA #{task_data.get('task_id', 'unknown')}: {str(e)}")
            logger.error(f"[{CONSUMER_ID}] 🔄 RECOLOCANDO mensagem na fila para reprocessamento")
            
            # Falha - rejeita e recoloca na fila
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            requeued_count += 1
            
            logger.error(f"[{CONSUMER_ID}] 🔄 Mensagem recolocada na fila (tentativa: {requeued_count})")
            logger.error(f"[{CONSUMER_ID}] 💪 TAREFA PRESERVADA - Pode ser reprocessada!")
            logger.error(f"[{CONSUMER_ID}] 📉 Total falhado: {failed_count}")
            logger.error("")
    
    try:
        # Conecta ao RabbitMQ
        logger.info("Conectando ao RabbitMQ...")
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        # Configura QoS
        channel.basic_qos(prefetch_count=1)  # Processamento seguro, uma por vez
        
        # Declara a fila (idempotente)
        channel.queue_declare(
            queue=QUEUE_NAME,
            durable=True
        )
        
        logger.info(f"Fila '{QUEUE_NAME}' declarada")
        logger.info("Configuração MANUAL ACK:")
        logger.info("  ✅ Vantagens: Segurança, não perde mensagens, reprocessamento automático")
        logger.info("  ❌ Desvantagens: Overhead de confirmação, processamento mais lento")
        logger.info("  🔒 SEGURANÇA: Mensagem só é removida após confirmação explícita")
        logger.info("")
        
        # Configura o consumer com MANUAL ACK
        channel.basic_consume(
            queue=QUEUE_NAME,
            on_message_callback=callback,
            auto_ack=False  # 🔒 MANUAL ACK - SEGURO
        )
        
        logger.info(f"[{CONSUMER_ID}] 🔒 Consumer MANUAL-ACK ativo...")
        logger.info("🛡️ SEGURANÇA: Mensagens permanecem na fila até confirmação")
        logger.info("Para sair pressione Ctrl+C")
        
        # Inicia o consumo
        channel.start_consuming()
        
    except KeyboardInterrupt:
        logger.info(f"Parando consumer...")
        logger.info(f"📊 Estatísticas finais:")
        logger.info(f"  ✅ Processado: {processed_count}")
        logger.info(f"  ❌ Falhado: {failed_count}")
        logger.info(f"  🔄 Recolocado na fila: {requeued_count}")
        logger.info(f"  🛡️ Mensagens preservadas: {requeued_count} (podem ser reprocessadas)")
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
