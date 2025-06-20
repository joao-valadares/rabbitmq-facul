"""
Consumer 2 para Headers Exchange
Consome mensagens da região US OU formato XML
Binding: region=us OR format=xml (x-match=any)
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
    COMPONENT_NAME = "consumer2"
    CONSUMER_ID = "US_OR_XML_PROCESSOR"
    EXCHANGE_NAME = "headers_exchange_demo"
    EXCHANGE_TYPE = "headers"
    QUEUE_NAME = "headers_queue_us_or_xml"
    
    # Headers para binding - PODE ter region=us OU format=xml
    BINDING_HEADERS = {
        "x-match": "any",  # Qualquer header que corresponder
        "region": "us",
        "format": "xml"
    }
    
    # Setup
    print_scenario_header(
        SCENARIO_NAME, 
        COMPONENT_NAME, 
        "Consumer que processa mensagens dos EUA OU formato XML (x-match=any)"
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
            
            # Identifica qual critério foi atendido
            region = headers.get('region')
            format_type = headers.get('format')
            matched_criteria = []
            
            if region == 'us':
                matched_criteria.append("REGIÃO=US")
            if format_type == 'xml':
                matched_criteria.append("FORMAT=XML")
            
            logger.info(f"[{CONSUMER_ID}] 🎯 CRITÉRIO ATENDIDO: {' + '.join(matched_criteria)}")
            logger.info(f"[{CONSUMER_ID}] ID: {message_data.get('id')}")
            logger.info(f"[{CONSUMER_ID}] Format: {format_type}")
            logger.info(f"[{CONSUMER_ID}] Region: {region}")
            logger.info(f"[{CONSUMER_ID}] Priority: {headers.get('priority', 'N/A')}")
            logger.info(f"[{CONSUMER_ID}] Conteúdo: {message_data.get('content')}")
            
            # Processamento específico baseado no critério
            if region == 'us' and format_type == 'xml':
                logger.info(f"[{CONSUMER_ID}] 🇺🇸 + 📄 Processamento US+XML (critérios duplos)...")
                time.sleep(1.5)
            elif region == 'us':
                logger.info(f"[{CONSUMER_ID}] 🇺🇸 Processamento específico para região US...")
                time.sleep(1.2)
            elif format_type == 'xml':
                logger.info(f"[{CONSUMER_ID}] 📄 Processamento específico para formato XML...")
                time.sleep(1.0)
            
            # Confirma o processamento
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info(f"[{CONSUMER_ID}] ✅ Processamento regionalizado/XML concluído")
            
        except Exception as e:
            logger.error(f"[{CONSUMER_ID}] ❌ Erro no processamento: {str(e)}")
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
        logger.info("Receberá: region=us OU format=xml (qualquer um)")
        
        # Configura o consumer
        channel.basic_consume(
            queue=QUEUE_NAME,
            on_message_callback=callback,
            auto_ack=False  # Confirmação manual
        )
        
        logger.info(f"[{CONSUMER_ID}] 🌎 Aguardando mensagens dos EUA ou XML...")
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
