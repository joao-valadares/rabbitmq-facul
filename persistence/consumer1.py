"""
Consumer 1 para Persistence
Consome mensagens PERSISTENTES (críticas, sobrevivem a reinicializações)
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
    COMPONENT_NAME = "consumer1"
    CONSUMER_ID = "PERSISTENT_PROCESSOR"
    QUEUE_NAME = "persistent_messages_queue"
    
    # Setup
    print_scenario_header(
        SCENARIO_NAME, 
        COMPONENT_NAME, 
        "Consumer que processa mensagens PERSISTENTES (críticas)"
    )
    
    logger = setup_logging(SCENARIO_NAME, COMPONENT_NAME)
    print_config_info(logger)
    
    # Contador de mensagens processadas
    messages_processed = 0
    
    def callback(ch, method, properties, body):
        """Callback para processar mensagens recebidas"""
        nonlocal messages_processed
        try:
            # Log da mensagem recebida
            log_message_received(logger, method, properties, body, CONSUMER_ID)
            
            # Processa a mensagem
            message_data = json.loads(body.decode('utf-8'))
            messages_processed += 1
            
            message_id = message_data.get('message_id')
            durability = message_data.get('durability')
            content = message_data.get('content')
            important_data = message_data.get('important_data')
            delivery_mode = message_data.get('delivery_mode')
            
            logger.info(f"[{CONSUMER_ID}] 💾 PROCESSANDO MENSAGEM PERSISTENTE #{message_id}")
            logger.info(f"[{CONSUMER_ID}] Durabilidade: {durability}")
            logger.info(f"[{CONSUMER_ID}] Delivery Mode: {delivery_mode} (2=persistente)")
            logger.info(f"[{CONSUMER_ID}] Conteúdo: {content}")
            logger.info(f"[{CONSUMER_ID}] Dados importantes: {important_data}")
            logger.info(f"[{CONSUMER_ID}] Total processado: {messages_processed} mensagens")
            
            # Simula processamento crítico que não pode ser perdido
            logger.info(f"[{CONSUMER_ID}] 🔒 Iniciando processamento CRÍTICO...")
            logger.info(f"[{CONSUMER_ID}] 📊 Salvando dados importantes no banco de dados...")
            time.sleep(1.5)
            
            logger.info(f"[{CONSUMER_ID}] 📝 Registrando auditoria de processamento...")
            time.sleep(0.5)
            
            logger.info(f"[{CONSUMER_ID}] 🔐 Criando backup de segurança...")
            time.sleep(0.8)
            
            # Confirma o processamento
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info(f"[{CONSUMER_ID}] ✅ Mensagem persistente #{message_id} processada com segurança!")
            logger.info(f"[{CONSUMER_ID}] 🛡️ Dados críticos preservados mesmo em caso de falha do sistema")
            logger.info("")
            
        except Exception as e:
            logger.error(f"[{CONSUMER_ID}] ❌ Erro ao processar mensagem persistente: {str(e)}")
            # Rejeita mas recoloca na fila - mensagem crítica não pode ser perdida
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    try:
        # Conecta ao RabbitMQ
        logger.info("Conectando ao RabbitMQ...")
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        # Configura QoS
        channel.basic_qos(prefetch_count=1)
        
        # Declara a fila persistente (idempotente)
        channel.queue_declare(
            queue=QUEUE_NAME,
            durable=True  # Fila persistente
        )
        
        logger.info(f"Fila '{QUEUE_NAME}' declarada como PERSISTENTE")
        logger.info("Características da fila:")
        logger.info("  - durable=True: Sobrevive a reinicializações do RabbitMQ")
        logger.info("  - Mensagens com delivery_mode=2: Armazenadas em disco")
        logger.info("  - Adequada para dados críticos que não podem ser perdidos")
        logger.info("")
        
        # Configura o consumer
        channel.basic_consume(
            queue=QUEUE_NAME,
            on_message_callback=callback,
            auto_ack=False  # Confirmação manual para garantir processamento
        )
        
        logger.info(f"[{CONSUMER_ID}] 💾 Aguardando mensagens PERSISTENTES...")
        logger.info("🔒 Processamento seguro: dados não são perdidos mesmo com falhas")
        logger.info("Para sair pressione Ctrl+C")
        
        # Inicia o consumo
        channel.start_consuming()
        
    except KeyboardInterrupt:
        logger.info(f"Parando consumer... Total processado: {messages_processed} mensagens persistentes")
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
