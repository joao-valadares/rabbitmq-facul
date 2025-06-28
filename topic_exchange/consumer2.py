"""
Consumer 2 para Topic Exchange
Consome mensagens do sistema específico (system.*)
"""
import sys
import os
import json
import time

# Adiciona o diretório pai ao path para importar utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pika
from utils.common import (
    setup_logging, get_rabbitmq_connection, create_exchange_and_queue,
    log_message_received, print_scenario_header, print_config_info
)

def main():
    # Configurações do cenário
    SCENARIO_NAME = "topic_exchange"
    COMPONENT_NAME = "consumer2"
    CONSUMER_ID = "SYSTEM_MONITOR"
    EXCHANGE_NAME = "topic_exchange_demo"
    EXCHANGE_TYPE = "topic"
    QUEUE_NAME = "topic_queue_system"
    ROUTING_PATTERN = "system.*"  # Todas as mensagens do sistema
    
    # Setup
    print_scenario_header(
        SCENARIO_NAME, 
        COMPONENT_NAME, 
        f"Consumer que monitora mensagens do SISTEMA (padrão: {ROUTING_PATTERN})"
    )
    
    logger = setup_logging(SCENARIO_NAME, COMPONENT_NAME)
    print_config_info(logger)
    
    def callback(ch, method, properties, body):
        """Callback para processar mensagens recebidas"""
        try:
            # Log imediato para confirmar que a função foi chamada
            logger.info("🔔 CALLBACK EXECUTADO!")
            print(f"🔔 CALLBACK EXECUTADO! - {time.strftime('%H:%M:%S')}")
            
            # Log da mensagem recebida
            log_message_received(logger, method, properties, body, CONSUMER_ID)
            
            # Processa a mensagem
            message_data = json.loads(body.decode('utf-8'))
            
            print(f"\n{'='*50}")
            print(f"🖥️  CONSUMER 2 - SISTEMA")
            print(f"{'='*50}")
            print(f"⏰ Recebido em: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"🏷️  Routing Key: {method.routing_key}")
            print(f"📨 Tipo: {message_data.get('subcategory', 'N/A')}")
            print(f"💬 Mensagem: {message_data.get('content', 'N/A')}")
            print(f"🔗 ID: {message_data.get('id', 'N/A')}")
            print(f"{'='*50}\n")
            
            logger.info(f"[{CONSUMER_ID}] ⚙️ SISTEMA - {message_data.get('subcategory', 'N/A').upper()}")
            logger.info(f"[{CONSUMER_ID}] ID: {message_data.get('id')}")
            logger.info(f"[{CONSUMER_ID}] Routing Key: {message_data.get('routing_key')}")
            logger.info(f"[{CONSUMER_ID}] Módulo: {message_data.get('detail')}")
            logger.info(f"[{CONSUMER_ID}] Conteúdo: {message_data.get('content')}")
            
            # Processamento baseado na severidade
            severity = message_data.get('subcategory')
            if severity == 'error':
                logger.info(f"[{CONSUMER_ID}] 🔴 Processamento de erro de sistema...")
                time.sleep(2)
            elif severity == 'warning':
                logger.info(f"[{CONSUMER_ID}] 🟡 Processamento de warning de sistema...")
                time.sleep(1)
            else:
                logger.info(f"[{CONSUMER_ID}] 🟢 Processamento de info de sistema...")
                time.sleep(0.5)
            
            # Confirma o processamento
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info(f"[{CONSUMER_ID}] ✅ Mensagem de sistema processada")
            
        except Exception as e:
            logger.error(f"[{CONSUMER_ID}] ❌ Erro ao processar mensagem: {str(e)}")
            # Rejeita a mensagem e não recoloca na fila
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    
    try:
        # Conecta ao RabbitMQ
        logger.info("🔌 Conectando ao RabbitMQ...")
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        logger.info("✅ Conectado ao RabbitMQ!")
        
        # Configura QoS
        channel.basic_qos(prefetch_count=1)
        
        # Declara o exchange (idempotente)
        logger.info(f"📢 Declarando exchange '{EXCHANGE_NAME}'...")
        channel.exchange_declare(
            exchange=EXCHANGE_NAME,
            exchange_type=EXCHANGE_TYPE,
            durable=True
        )
        logger.info("✅ Exchange declarado!")
        
        # Declara a fila (idempotente)
        logger.info(f"📥 Declarando fila '{QUEUE_NAME}'...")
        queue_result = channel.queue_declare(
            queue=QUEUE_NAME,
            durable=True
        )
        logger.info(f"✅ Fila declarada! Mensagens na fila: {queue_result.method.message_count}")
        
        # Cria o binding para Topic Exchange
        logger.info(f"🔗 Criando binding com padrão '{ROUTING_PATTERN}'...")
        channel.queue_bind(
            exchange=EXCHANGE_NAME,
            queue=QUEUE_NAME,
            routing_key=ROUTING_PATTERN
        )
        logger.info("✅ Binding criado!")
        
        logger.info(f"Exchange '{EXCHANGE_NAME}' declarado")
        logger.info(f"Fila '{QUEUE_NAME}' declarada e vinculada com padrão '{ROUTING_PATTERN}'")
        logger.info(f"Receberá: system.info.*, system.warning.*, system.error.*")
        
        # Configura o consumer
        logger.info("👂 Configurando consumer...")
        channel.basic_consume(
            queue=QUEUE_NAME,
            on_message_callback=callback,
            auto_ack=False  # Confirmação manual
        )
        
        print(f"\n{'='*60}")
        print(f"🖥️  CONSUMER 2 - AGUARDANDO MENSAGENS DO SISTEMA")
        print(f"{'='*60}")
        print(f"📢 Exchange: {EXCHANGE_NAME}")
        print(f"📥 Fila: {QUEUE_NAME}")
        print(f"🏷️  Padrão: {ROUTING_PATTERN}")
        print(f"📋 Receberá: system.info.*, system.warning.*, system.error.*")
        print(f"{'='*60}")
        print("Pressione CTRL+C para parar\n")
        
        logger.info(f"[{CONSUMER_ID}] 🖥️ Monitorando mensagens de SISTEMA. Para sair pressione Ctrl+C")
        logger.info("🔄 Iniciando consumo de mensagens...")
        
        # Inicia o consumo
        channel.start_consuming()
        
    except KeyboardInterrupt:
        logger.info("⏹️  Parando consumer...")
        if 'channel' in locals():
            channel.stop_consuming()
        logger.info("✅ Consumer parado!")
    except Exception as e:
        logger.error(f"❌ Erro fatal no consumer: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
    finally:
        if 'connection' in locals() and not connection.is_closed:
            connection.close()
            logger.info("🔌 Conexão fechada")

if __name__ == "__main__":
    main()
