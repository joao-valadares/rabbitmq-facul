"""
Utilitários compartilhados para o projeto RabbitMQ
"""
import os
import pika
import logging
import sys
from datetime import datetime
from typing import Optional, Dict, Any

def setup_logging(scenario_name: str, component_name: str) -> logging.Logger:
    """
    Configura logging padronizado para todos os componentes
    
    Args:
        scenario_name: Nome do cenário (ex: 'direct_exchange')
        component_name: Nome do componente (ex: 'producer', 'consumer1')
    
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(f"{scenario_name}_{component_name}")
    logger.setLevel(logging.INFO)
    
    # Remove handlers existentes para evitar duplicação
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Formato das mensagens
    formatter = logging.Formatter(
        '%(asctime)s - [%(name)s] - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

def get_rabbitmq_connection() -> pika.BlockingConnection:
    """
    Cria conexão com RabbitMQ usando variáveis de ambiente
    
    Returns:
        Conexão ativa com RabbitMQ
        
    Raises:
        ConnectionError: Se não conseguir conectar
    """
    # Carrega configurações do ambiente
    host = os.getenv('RABBITMQ_HOST', 'localhost')
    port = int(os.getenv('RABBITMQ_PORT', '5672'))
    username = os.getenv('RABBITMQ_USER', 'guest')
    password = os.getenv('RABBITMQ_PASSWORD', 'guest')
    vhost = os.getenv('RABBITMQ_VHOST', '/')
    
    # Parâmetros de conexão
    credentials = pika.PlainCredentials(username, password)
    parameters = pika.ConnectionParameters(
        host=host,
        port=port,
        virtual_host=vhost,
        credentials=credentials,
        heartbeat=600,
        blocked_connection_timeout=300
    )
    
    try:
        connection = pika.BlockingConnection(parameters)
        return connection
    except Exception as e:
        raise ConnectionError(f"Falha ao conectar com RabbitMQ em {host}:{port} - {str(e)}")

def create_exchange_and_queue(channel: pika.channel.Channel, 
                            exchange_name: str, 
                            exchange_type: str, 
                            queue_name: str,
                            routing_key: str = '',
                            queue_arguments: Optional[Dict[str, Any]] = None,
                            durable: bool = True) -> None:
    """
    Cria exchange e fila de forma idempotente
    
    Args:
        channel: Canal do RabbitMQ
        exchange_name: Nome do exchange
        exchange_type: Tipo do exchange (direct, fanout, topic, headers)
        queue_name: Nome da fila
        routing_key: Chave de roteamento para binding
        queue_arguments: Argumentos adicionais da fila
        durable: Se exchange e fila devem ser duráveis
    """
    # Cria exchange se não existir
    channel.exchange_declare(
        exchange=exchange_name,
        exchange_type=exchange_type,
        durable=durable
    )
    
    # Cria fila se não existir
    channel.queue_declare(
        queue=queue_name,
        durable=durable,
        arguments=queue_arguments or {}
    )
    
    # Cria binding se routing_key fornecida (não se aplica a fanout)
    if routing_key or exchange_type != 'fanout':
        channel.queue_bind(
            exchange=exchange_name,
            queue=queue_name,
            routing_key=routing_key
        )

def log_message_sent(logger: logging.Logger, 
                    exchange: str, 
                    routing_key: str, 
                    message: str,
                    properties: Optional[pika.BasicProperties] = None) -> None:
    """
    Log padronizado para mensagens enviadas
    """
    props_info = ""
    if properties:
        props_info = f" | delivery_mode={properties.delivery_mode}"
        if properties.priority:
            props_info += f" | priority={properties.priority}"
        if properties.headers:
            props_info += f" | headers={properties.headers}"
    
    logger.info(f"ENVIADO → Exchange: {exchange} | Routing Key: {routing_key} | Mensagem: {message[:50]}...{props_info}")

def log_message_received(logger: logging.Logger,
                        method: pika.spec.Basic.Deliver,
                        properties: pika.BasicProperties,
                        body: bytes,
                        consumer_id: str) -> None:
    """
    Log padronizado para mensagens recebidas
    """
    message = body.decode('utf-8')
    props_info = f"delivery_mode={properties.delivery_mode}"
    if properties.priority:
        props_info += f" | priority={properties.priority}"
    if properties.headers:
        props_info += f" | headers={properties.headers}"
    
    logger.info(f"RECEBIDO [{consumer_id}] ← Exchange: {method.exchange} | "
               f"Routing Key: {method.routing_key} | Mensagem: {message[:50]}... | {props_info}")

def print_scenario_header(scenario_name: str, component_name: str, description: str) -> None:
    """
    Imprime cabeçalho padronizado para cada componente
    """
    print("=" * 80)
    print(f"CENÁRIO: {scenario_name.upper()}")
    print(f"COMPONENTE: {component_name.upper()}")
    print(f"DESCRIÇÃO: {description}")
    print(f"TIMESTAMP: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()

def get_config_summary() -> Dict[str, str]:
    """
    Retorna resumo das configurações atuais
    """
    return {
        'RABBITMQ_HOST': os.getenv('RABBITMQ_HOST', 'localhost'),
        'RABBITMQ_PORT': os.getenv('RABBITMQ_PORT', '5672'),
        'RABBITMQ_USER': os.getenv('RABBITMQ_USER', 'guest'),
        'RABBITMQ_VHOST': os.getenv('RABBITMQ_VHOST', '/')
    }

def print_config_info(logger: logging.Logger) -> None:
    """
    Imprime informações de configuração
    """
    config = get_config_summary()
    logger.info("Configuração RabbitMQ:")
    for key, value in config.items():
        # Não mostra senha por segurança
        if 'PASSWORD' in key:
            value = '*' * len(value)
        logger.info(f"  {key}: {value}")
