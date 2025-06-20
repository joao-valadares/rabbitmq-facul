"""
Producer para Priority Queue
Demonstra filas com prioridade onde mensagens importantes são processadas primeiro
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
    SCENARIO_NAME = "priority"
    COMPONENT_NAME = "producer"
    EXCHANGE_NAME = ""  # Exchange padrão
    QUEUE_NAME = "priority_queue"
    
    # Setup
    print_scenario_header(
        SCENARIO_NAME, 
        COMPONENT_NAME, 
        "Producer que envia mensagens com diferentes prioridades"
    )
    
    logger = setup_logging(SCENARIO_NAME, COMPONENT_NAME)
    print_config_info(logger)
    
    try:
        # Conecta ao RabbitMQ
        logger.info("Conectando ao RabbitMQ...")
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        # Declara a fila com prioridade máxima 10
        logger.info(f"Declarando fila '{QUEUE_NAME}' com prioridade máxima 10...")
        channel.queue_declare(
            queue=QUEUE_NAME,
            durable=True,
            arguments={'x-max-priority': 10}  # Prioridade máxima 10
        )
        
        # Tipos de mensagens com diferentes prioridades
        message_types = [
            {"type": "CRITICAL_ALERT", "priority": 10, "description": "Sistema em falha crítica"},
            {"type": "SECURITY_BREACH", "priority": 9, "description": "Tentativa de invasão detectada"},
            {"type": "ERROR_LOG", "priority": 7, "description": "Erro no processamento"},
            {"type": "WARNING", "priority": 5, "description": "Aviso de capacidade"},
            {"type": "INFO_LOG", "priority": 3, "description": "Log informativo"},
            {"type": "DEBUG_LOG", "priority": 1, "description": "Debug de desenvolvimento"},
            {"type": "BATCH_PROCESS", "priority": 0, "description": "Processamento em lote"}
        ]
        
        logger.info("Iniciando envio de mensagens com prioridades...")
        print(f"\n🎯 CENÁRIO: Enviando mensagens com diferentes prioridades")
        print(f"📊 Prioridades: 0 (menor) → 10 (maior)")
        print(f"⏰ Intervalo: 0.5s entre mensagens")
        print(f"🔄 Pressione Ctrl+C para parar\n")
        
        message_count = 0
        
        # Loop principal de envio
        while True:
            # Escolhe tipo de mensagem aleatoriamente
            msg_type = random.choice(message_types)
            
            message_count += 1
            timestamp = datetime.now().isoformat()
            
            # Cria payload da mensagem
            message = {
                "id": message_count,
                "type": msg_type["type"],
                "priority": msg_type["priority"],
                "description": msg_type["description"],
                "timestamp": timestamp,
                "server": f"server-{random.randint(1, 5)}",
                "severity": get_severity_level(msg_type["priority"])
            }
            
            # Adiciona contexto específico por tipo
            if msg_type["type"] == "CRITICAL_ALERT":
                message["alert_code"] = f"CRIT-{random.randint(1000, 9999)}"
                message["affected_systems"] = ["database", "api", "frontend"]
            elif msg_type["type"] == "SECURITY_BREACH":
                message["source_ip"] = f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}"
                message["attack_type"] = random.choice(["SQL_INJECTION", "BRUTE_FORCE", "XSS"])
            elif msg_type["type"] == "BATCH_PROCESS":
                message["records_count"] = random.randint(1000, 50000)
                message["estimated_time"] = f"{random.randint(5, 120)} minutes"
            
            # Serializa mensagem
            message_body = json.dumps(message, indent=2)
            
            # Publica mensagem com prioridade
            channel.basic_publish(
                exchange=EXCHANGE_NAME,
                routing_key=QUEUE_NAME,
                body=message_body,
                properties=pika.BasicProperties(
                    priority=msg_type["priority"],  # Define prioridade da mensagem
                    delivery_mode=2,  # Mensagem persistente
                    message_id=str(message_count),
                    timestamp=int(time.time()),
                    headers={
                        'message_type': msg_type["type"],
                        'severity': get_severity_level(msg_type["priority"]),
                        'component': 'priority_producer'
                    }
                )
            )
            
            # Log detalhado
            priority_icon = get_priority_icon(msg_type["priority"])
            severity = get_severity_level(msg_type["priority"])
            
            log_message_sent(
                logger, 
                message_count, 
                f"[{priority_icon} P{msg_type['priority']}] {msg_type['type']}: {msg_type['description']}"
            )
            
            print(f"📤 MSG #{message_count:03d} | "
                  f"{priority_icon} P{msg_type['priority']} | "
                  f"{severity:8s} | "
                  f"{msg_type['type']:15s} | "
                  f"{msg_type['description']}")
            
            # Aguarda antes da próxima mensagem
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        logger.info(f"Interrompido pelo usuário. Total de mensagens enviadas: {message_count}")
        print(f"\n✅ Finalizando producer. Total: {message_count} mensagens enviadas")
        
    except Exception as e:
        logger.error(f"Erro no producer: {e}")
        print(f"❌ Erro: {e}")
        
    finally:
        if 'connection' in locals() and connection.is_open:
            connection.close()
            logger.info("Conexão fechada")

def get_priority_icon(priority):
    """Retorna ícone baseado na prioridade"""
    if priority >= 9:
        return "🚨"  # Crítico
    elif priority >= 7:
        return "⚠️"   # Erro
    elif priority >= 5:
        return "🟡"  # Warning
    elif priority >= 3:
        return "ℹ️"   # Info
    else:
        return "🔍"  # Debug/Baixa

def get_severity_level(priority):
    """Retorna nível de severidade baseado na prioridade"""
    if priority >= 9:
        return "CRITICAL"
    elif priority >= 7:
        return "ERROR"
    elif priority >= 5:
        return "WARNING"
    elif priority >= 3:
        return "INFO"
    else:
        return "DEBUG"

if __name__ == "__main__":
    main()
