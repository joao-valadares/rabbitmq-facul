"""
Producer para Headers Exchange
Demonstra roteamento baseado em headers das mensagens
"""
import sys
import os
import time
import json
from datetime import datetime
import random

# Adiciona o diretório pai ao path para importar utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pika
from utils.common import (
    setup_logging, get_rabbitmq_connection, create_exchange_and_queue,
    log_message_sent, print_scenario_header, print_config_info
)

def main():
    # Configurações do cenário
    SCENARIO_NAME = "headers_exchange"
    COMPONENT_NAME = "producer"
    EXCHANGE_NAME = "headers_exchange_demo"
    EXCHANGE_TYPE = "headers"
    
    # Diferentes combinações de headers para demonstrar roteamento
    MESSAGE_TYPES = [
        {
            "headers": {"format": "json", "priority": "high", "region": "us"},
            "content": "Dados JSON de alta prioridade dos EUA"
        },
        {
            "headers": {"format": "xml", "priority": "low", "region": "eu"},
            "content": "Dados XML de baixa prioridade da Europa"
        },
        {
            "headers": {"format": "json", "priority": "medium", "region": "br"},
            "content": "Dados JSON de prioridade média do Brasil"
        },
        {
            "headers": {"format": "csv", "priority": "high", "source": "api"},
            "content": "Dados CSV de alta prioridade da API"
        },
        {
            "headers": {"format": "json", "encrypted": "true", "region": "us"},
            "content": "Dados JSON criptografados dos EUA"
        },
        {
            "headers": {"format": "xml", "priority": "medium", "source": "batch"},
            "content": "Dados XML de prioridade média do processamento batch"
        }
    ]
    
    # Setup
    print_scenario_header(
        SCENARIO_NAME, 
        COMPONENT_NAME, 
        "Producer que envia mensagens com headers variados para Headers Exchange"
    )
    
    logger = setup_logging(SCENARIO_NAME, COMPONENT_NAME)
    print_config_info(logger)
    
    try:
        # Conecta ao RabbitMQ
        logger.info("Conectando ao RabbitMQ...")
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        # Declara o exchange (idempotente)
        logger.info(f"Declarando exchange '{EXCHANGE_NAME}' do tipo '{EXCHANGE_TYPE}'")
        channel.exchange_declare(
            exchange=EXCHANGE_NAME,
            exchange_type=EXCHANGE_TYPE,
            durable=True
        )
        
        logger.info("Producer iniciado. Enviando mensagens com headers variados...")
        logger.info("Tipos de headers que serão enviados:")
        for i, msg_type in enumerate(MESSAGE_TYPES, 1):
            headers_str = ", ".join([f"{k}={v}" for k, v in msg_type["headers"].items()])
            logger.info(f"  {i}. {headers_str}")
        logger.info("Pressione Ctrl+C para parar")
        
        message_count = 1
        
        while True:
            # Escolhe um tipo de mensagem aleatório
            message_type = random.choice(MESSAGE_TYPES)
            headers = message_type["headers"]
            base_content = message_type["content"]
            
            # Prepara a mensagem
            message_data = {
                "id": message_count,
                "content": f"{base_content} #{message_count}",
                "timestamp": datetime.now().isoformat(),
                "scenario": SCENARIO_NAME,
                "headers_info": headers
            }
            
            message_body = json.dumps(message_data, ensure_ascii=False)
            
            # Propriedades da mensagem com headers customizados
            properties = pika.BasicProperties(
                delivery_mode=2,  # Mensagem persistente
                content_type='application/json',
                timestamp=int(time.time()),
                headers=headers  # Headers usados para roteamento
            )
            
            # Publica a mensagem (routing_key é ignorada em headers exchange)
            channel.basic_publish(
                exchange=EXCHANGE_NAME,
                routing_key='',  # Ignorada em headers exchange
                body=message_body,
                properties=properties
            )
            
            # Log customizado para headers
            headers_str = ", ".join([f"{k}={v}" for k, v in headers.items()])
            log_message_sent(logger, EXCHANGE_NAME, f"headers({headers_str})", message_body, properties)
            
            message_count += 1
            time.sleep(3)  # Pausa entre mensagens
            
    except KeyboardInterrupt:
        logger.info("Parando producer...")
    except Exception as e:
        logger.error(f"Erro no producer: {str(e)}")
    finally:
        if 'connection' in locals() and not connection.is_closed:
            connection.close()
            logger.info("Conexão fechada")

if __name__ == "__main__":
    main()
