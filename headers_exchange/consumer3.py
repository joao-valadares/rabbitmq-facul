"""
Consumer 3 para Headers Exchange
Consome mensagens com qualquer header 'encrypted' presente
Binding: encrypted=true (x-match=any)
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
    SCENARIO_NAME = "headers_exchange"
    COMPONENT_NAME = "consumer3"
    CONSUMER_ID = "ENCRYPTED_DATA_PROCESSOR"
    EXCHANGE_NAME = "headers_exchange_demo"
    EXCHANGE_TYPE = "headers"
    QUEUE_NAME = "headers_queue_encrypted"
    
    # Headers para binding - mensagens criptografadas
    BINDING_HEADERS = {
        "x-match": "any",  # Qualquer header que corresponder
        "encrypted": "true"
    }
    
    # Setup
    print_scenario_header(
        SCENARIO_NAME, 
        COMPONENT_NAME, 
        "Consumer que processa mensagens CRIPTOGRAFADAS (encrypted=true)"
    )
    
    logger = setup_logging(SCENARIO_NAME, COMPONENT_NAME)
    print_config_info(logger)
    
    def callback(ch, method, properties, body):
        """Callback para processar mensagens recebidas"""
        try:
            # Log da mensagem recebida
            log_message_received(logger, method, properties, body, CONSUMER_ID)
            
            # Processa a mensagem
            message_data = json.loads(body.decode('utf-8'))
            headers = properties.headers or {}
            
            logger.info(f"[{CONSUMER_ID}] 🔐 DADOS CRIPTOGRAFADOS DETECTADOS!")
            logger.info(f"[{CONSUMER_ID}] ID: {message_data.get('id')}")
            logger.info(f"[{CONSUMER_ID}] Encrypted: {headers.get('encrypted')}")
            logger.info(f"[{CONSUMER_ID}] Format: {headers.get('format', 'N/A')}")
            logger.info(f"[{CONSUMER_ID}] Region: {headers.get('region', 'N/A')}")
            logger.info(f"[{CONSUMER_ID}] Priority: {headers.get('priority', 'N/A')}")
            
            # Processamento especial para dados criptografados
            logger.info(f"[{CONSUMER_ID}] 🔑 Iniciando processo de descriptografia...")
            time.sleep(0.8)  # Simula descriptografia
            
            logger.info(f"[{CONSUMER_ID}] 🔓 Dados descriptografados com sucesso")
            logger.info(f"[{CONSUMER_ID}] Conteúdo: {message_data.get('content')}")
            
            # Processamento dos dados descriptografados
            logger.info(f"[{CONSUMER_ID}] 📊 Processando dados sensíveis...")
            time.sleep(1.0)
            
            # Log de auditoria para dados criptografados
            logger.info(f"[{CONSUMER_ID}] 📝 Registrando acesso a dados criptografados na auditoria...")
            
            # Confirma o processamento
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info(f"[{CONSUMER_ID}] ✅ Processamento seguro concluído")
            
        except Exception as e:
            logger.error(f"[{CONSUMER_ID}] ❌ Erro no processamento seguro: {str(e)}")
            # Rejeita a mensagem e não recoloca na fila
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    
    try:
        # Conecta ao RabbitMQ
        logger.info("Conectando ao RabbitMQ...")
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        # Configura QoS
        channel.basic_qos(prefetch_count=1)
        
        # Declara exchange (idempotente)
        channel.exchange_declare(
            exchange=EXCHANGE_NAME,
            exchange_type=EXCHANGE_TYPE,
            durable=True
        )
        
        # Declara fila (idempotente)
        channel.queue_declare(
            queue=QUEUE_NAME,
            durable=True
        )
        
        # Cria binding com headers
        channel.queue_bind(
            exchange=EXCHANGE_NAME,
            queue=QUEUE_NAME,
            routing_key='',  # Ignorada em headers exchange
            arguments=BINDING_HEADERS
        )
        
        logger.info(f"Exchange '{EXCHANGE_NAME}' declarado")
        logger.info(f"Fila '{QUEUE_NAME}' declarada")
        logger.info(f"Binding criado com headers: {BINDING_HEADERS}")
        logger.info("Receberá apenas: mensagens com encrypted=true")
        
        # Configura o consumer
        channel.basic_consume(
            queue=QUEUE_NAME,
            on_message_callback=callback,
            auto_ack=False  # Confirmação manual
        )
        
        logger.info(f"[{CONSUMER_ID}] 🛡️ Aguardando mensagens CRIPTOGRAFADAS...")
        logger.info("Para sair pressione Ctrl+C")
        
        # Inicia o consumo
        channel.start_consuming()
        
    except KeyboardInterrupt:
        logger.info("Parando consumer...")
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
