"""
Consumer 3 para Topic Exchange
Consome mensagens da aplicação relacionadas a usuários (app.user.*)
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
    COMPONENT_NAME = "consumer3"
    CONSUMER_ID = "USER_ACTIVITY_TRACKER"
    EXCHANGE_NAME = "topic_exchange_demo"
    EXCHANGE_TYPE = "topic"
    QUEUE_NAME = "topic_queue_user_activity"
    ROUTING_PATTERN = "app.user.*"  # Apenas atividades de usuário
    
    # Setup
    print_scenario_header(
        SCENARIO_NAME, 
        COMPONENT_NAME, 
        f"Consumer que rastreia atividade de USUÁRIOS (padrão: {ROUTING_PATTERN})"
    )
    
    logger = setup_logging(SCENARIO_NAME, COMPONENT_NAME)
    print_config_info(logger)
    
    # Contador de atividades
    activity_count = {"login": 0, "logout": 0, "other": 0}
    
    def callback(ch, method, properties, body):
        """Callback para processar mensagens recebidas"""
        nonlocal activity_count
        try:
            # Log da mensagem recebida
            log_message_received(logger, method, properties, body, CONSUMER_ID)
            
            # Processa a mensagem
            message_data = json.loads(body.decode('utf-8'))
            
            activity_type = message_data.get('detail', 'other')
            activity_count[activity_type] = activity_count.get(activity_type, 0) + 1
            
            logger.info(f"[{CONSUMER_ID}] 👤 ATIVIDADE DE USUÁRIO: {activity_type.upper()}")
            logger.info(f"[{CONSUMER_ID}] ID: {message_data.get('id')}")
            logger.info(f"[{CONSUMER_ID}] Routing Key: {message_data.get('routing_key')}")
            logger.info(f"[{CONSUMER_ID}] Conteúdo: {message_data.get('content')}")
            
            # Estatísticas
            total_activities = sum(activity_count.values())
            logger.info(f"[{CONSUMER_ID}] Estatísticas: Login={activity_count.get('login', 0)}, "
                       f"Logout={activity_count.get('logout', 0)}, "
                       f"Outros={activity_count.get('other', 0)}, "
                       f"Total={total_activities}")
            
            # Processamento específico por tipo de atividade
            if activity_type == 'login':
                logger.info(f"[{CONSUMER_ID}] 🟢 Registrando login de usuário...")
                time.sleep(0.8)
            elif activity_type == 'logout':
                logger.info(f"[{CONSUMER_ID}] 🔴 Registrando logout de usuário...")
                time.sleep(0.6)
            else:
                logger.info(f"[{CONSUMER_ID}] 📝 Registrando atividade geral...")
                time.sleep(0.4)
            
            # Confirma o processamento
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info(f"[{CONSUMER_ID}] ✅ Atividade de usuário registrada")
            
        except Exception as e:
            logger.error(f"[{CONSUMER_ID}] ❌ Erro ao processar atividade: {str(e)}")
            # Rejeita a mensagem e não recoloca na fila
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    
    try:
        # Conecta ao RabbitMQ
        logger.info("Conectando ao RabbitMQ...")
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        # Configura QoS
        channel.basic_qos(prefetch_count=1)
        
        # Cria exchange, fila e binding (idempotente)
        create_exchange_and_queue(
            channel=channel,
            exchange_name=EXCHANGE_NAME,
            exchange_type=EXCHANGE_TYPE,
            queue_name=QUEUE_NAME,
            routing_key=ROUTING_PATTERN,
            durable=True
        )
        
        logger.info(f"Exchange '{EXCHANGE_NAME}' declarado")
        logger.info(f"Fila '{QUEUE_NAME}' declarada e vinculada com padrão '{ROUTING_PATTERN}'")
        logger.info(f"Receberá: app.user.login, app.user.logout, etc.")
        
        # Configura o consumer
        channel.basic_consume(
            queue=QUEUE_NAME,
            on_message_callback=callback,
            auto_ack=False  # Confirmação manual
        )
        
        logger.info(f"[{CONSUMER_ID}] 👥 Rastreando atividades de USUÁRIO. Para sair pressione Ctrl+C")
        
        # Inicia o consumo
        channel.start_consuming()
        
    except KeyboardInterrupt:
        logger.info(f"Parando consumer... Estatísticas finais: {activity_count}")
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
