"""
Consumer 2 para Persistence
Consome mensagens TRANSIENTES (performance otimizada, não sobrevivem a reinicializações)
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
    COMPONENT_NAME = "consumer2"
    CONSUMER_ID = "TRANSIENT_PROCESSOR"
    QUEUE_NAME = "transient_messages_queue"
    
    # Setup
    print_scenario_header(
        SCENARIO_NAME, 
        COMPONENT_NAME, 
        "Consumer que processa mensagens TRANSIENTES (performance otimizada)"
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
            delivery_mode = message_data.get('delivery_mode')
            
            logger.info(f"[{CONSUMER_ID}] ⚡ PROCESSANDO MENSAGEM TRANSIENTE #{message_id}")
            logger.info(f"[{CONSUMER_ID}] Durabilidade: {durability}")
            logger.info(f"[{CONSUMER_ID}] Delivery Mode: {delivery_mode} (1=transiente)")
            logger.info(f"[{CONSUMER_ID}] Conteúdo: {content}")
            logger.info(f"[{CONSUMER_ID}] Total processado: {messages_processed} mensagens")
            
            # Simula processamento rápido e otimizado
            logger.info(f"[{CONSUMER_ID}] 🚀 Iniciando processamento RÁPIDO...")
            logger.info(f"[{CONSUMER_ID}] 📊 Cache em memória ativado...")
            time.sleep(0.5)  # Processamento mais rápido
            
            logger.info(f"[{CONSUMER_ID}] ⚡ Processamento otimizado concluído!")
            
            # Confirma o processamento
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info(f"[{CONSUMER_ID}] ✅ Mensagem transiente #{message_id} processada rapidamente!")
            logger.info(f"[{CONSUMER_ID}] 🏃 Performance otimizada: sem overhead de persistência")
            logger.info("")
            
        except Exception as e:
            logger.error(f"[{CONSUMER_ID}] ❌ Erro ao processar mensagem transiente: {str(e)}")
            # Para mensagens transientes, podemos ser menos rigorosos com requeue
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    
    try:
        # Conecta ao RabbitMQ
        logger.info("Conectando ao RabbitMQ...")
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        # Configura QoS
        channel.basic_qos(prefetch_count=3)  # Mais mensagens simultâneas para performance
        
        # Declara a fila transiente (idempotente)
        channel.queue_declare(
            queue=QUEUE_NAME,
            durable=False  # Fila transiente
        )
        
        logger.info(f"Fila '{QUEUE_NAME}' declarada como TRANSIENTE")
        logger.info("Características da fila:")
        logger.info("  - durable=False: Perdida se RabbitMQ reiniciar")
        logger.info("  - Mensagens com delivery_mode=1: Apenas em memória")
        logger.info("  - Performance otimizada para processamento rápido")
        logger.info("  - Adequada para dados temporários ou cache")
        logger.info("")
        
        # Configura o consumer
        channel.basic_consume(
            queue=QUEUE_NAME,
            on_message_callback=callback,
            auto_ack=False  # Confirmação manual
        )
        
        logger.info(f"[{CONSUMER_ID}] ⚡ Aguardando mensagens TRANSIENTES...")
        logger.info("🚀 Processamento rápido: otimizado para performance")
        logger.info("Para sair pressione Ctrl+C")
        
        # Inicia o consumo
        channel.start_consuming()
        
    except KeyboardInterrupt:
        logger.info(f"Parando consumer... Total processado: {messages_processed} mensagens transientes")
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
