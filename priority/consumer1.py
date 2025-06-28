"""
Consumer 1 para Priority Queue - Processador de Alertas Críticos
Processa mensagens de alta prioridade primeiro
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
    setup_logging, get_rabbitmq_connection,
    print_scenario_header, print_config_info
)

def main():
    # Configurações do cenário
    SCENARIO_NAME = "priority"
    COMPONENT_NAME = "consumer1"
    QUEUE_NAME = "priority_queue"
    
    # Setup
    print_scenario_header(
        SCENARIO_NAME, 
        COMPONENT_NAME, 
        "Consumer especializado em alertas críticos e de alta prioridade"
    )
    
    logger = setup_logging(SCENARIO_NAME, COMPONENT_NAME)
    print_config_info(logger)
    
    try:
        # Conecta ao RabbitMQ
        logger.info("Conectando ao RabbitMQ...")
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        # Declara a fila (idempotente)
        logger.info(f"Declarando fila '{QUEUE_NAME}'...")
        channel.queue_declare(
            queue=QUEUE_NAME,
            durable=True,
            arguments={'x-max-priority': 10}
        )
        
        # Configurações do consumer
        channel.basic_qos(prefetch_count=1)  # Processa uma mensagem por vez
        
        # Estatísticas
        stats = {
            'processed': 0,
            'critical': 0,
            'errors': 0,
            'warnings': 0,
            'info': 0,
            'debug': 0,
            'start_time': datetime.now()
        }
        
        logger.info("Iniciando consumer de prioridades...")
        print(f"\n🎯 CONSUMER 1: Processador de Alertas Críticos")
        print(f"🔍 Foco: Mensagens de alta prioridade (7-10)")
        print(f"⚡ Velocidade: Rápida para críticos, normal para outros")
        print(f"🔄 Pressione Ctrl+C para parar\n")
        
        def callback(ch, method, properties, body):
            try:
                # Deserializa mensagem
                message = json.loads(body.decode('utf-8'))
                stats['processed'] += 1
                
                # Extrai informações
                msg_id = message.get('id', 'unknown')
                msg_type = message.get('type', 'unknown')
                priority = message.get('priority', 0)
                description = message.get('description', '')
                severity = message.get('severity', 'UNKNOWN')
                
                # Ícone baseado na prioridade
                priority_icon = get_priority_icon(priority)
                
                # Atualiza estatísticas por severidade
                if severity == 'CRITICAL':
                    stats['critical'] += 1
                elif severity == 'ERROR':
                    stats['errors'] += 1
                elif severity == 'WARNING':
                    stats['warnings'] += 1
                elif severity == 'INFO':
                    stats['info'] += 1
                else:
                    stats['debug'] += 1
                
                # Log de recebimento
                print(f"📥 MSG #{msg_id:03d} | "
                      f"{priority_icon} P{priority} | "
                      f"{severity:8s} | "
                      f"{msg_type:15s} | "
                      f"Processing...")
                
                # Tempo de processamento baseado na prioridade
                processing_time = get_processing_time(priority, severity)
                
                # Simula processamento específico por tipo
                if msg_type == "CRITICAL_ALERT":
                    process_critical_alert(message, logger)
                elif msg_type == "SECURITY_BREACH":
                    process_security_breach(message, logger)
                elif msg_type == "ERROR_LOG":
                    process_error_log(message, logger)
                else:
                    process_regular_message(message, logger)
                
                # Simula tempo de processamento
                time.sleep(processing_time)
                
                # Log de conclusão
                elapsed = datetime.now() - stats['start_time']
                uptime = str(elapsed).split('.')[0]  # Remove microsegundos
                
                print(f"✅ MSG #{msg_id:03d} | "
                      f"Processed in {processing_time:.1f}s | "
                      f"Total: {stats['processed']} | "
                      f"Uptime: {uptime}")
                
                # Confirma processamento
                ch.basic_ack(delivery_tag=method.delivery_tag)
                
                # Log estatísticas a cada 10 mensagens
                if stats['processed'] % 10 == 0:
                    print_stats(stats, logger)
                
            except json.JSONDecodeError as e:
                logger.error(f"Erro ao decodificar JSON: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                
            except Exception as e:
                logger.error(f"Erro no processamento: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        
        # Configura consumer
        channel.basic_consume(
            queue=QUEUE_NAME,
            on_message_callback=callback,
            auto_ack=False
        )
        
        logger.info("Aguardando mensagens. Para sair, pressione CTRL+C")
        channel.start_consuming()
        
    except KeyboardInterrupt:
        logger.info("Interrompido pelo usuário")
        print(f"\n✅ Finalizando consumer1...")
        print_final_stats(stats)
        
    except Exception as e:
        logger.error(f"Erro no consumer: {e}")
        print(f"❌ Erro: {e}")
        
    finally:
        if 'channel' in locals() and channel.is_open:
            channel.stop_consuming()
        if 'connection' in locals() and connection.is_open:
            connection.close()
            logger.info("Conexão fechada")

def get_priority_icon(priority):
    """Retorna ícone baseado na prioridade"""
    if priority >= 9:
        return "🚨"
    elif priority >= 7:
        return "⚠️"
    elif priority >= 5:
        return "🟡"
    elif priority >= 3:
        return "ℹ️"
    else:
        return "🔍"

def get_processing_time(priority, severity):
    """Retorna tempo de processamento baseado na prioridade"""
    if severity == 'CRITICAL':
        return round(random.uniform(0.1, 0.3), 1)  # Muito rápido para críticos
    elif severity == 'ERROR':
        return round(random.uniform(0.3, 0.7), 1)  # Rápido para erros
    elif severity == 'WARNING':
        return round(random.uniform(0.5, 1.0), 1)  # Normal para warnings
    else:
        return round(random.uniform(1.0, 2.0), 1)  # Mais lento para info/debug

def process_critical_alert(message, logger):
    """Processa alertas críticos"""
    alert_code = message.get('alert_code', 'UNKNOWN')
    affected_systems = message.get('affected_systems', [])
    
    logger.warning(f"🚨 ALERTA CRÍTICO: {alert_code}")
    logger.warning(f"Sistemas afetados: {', '.join(affected_systems)}")
    
    # Simula ações críticas
    actions = [
        "Escalando para equipe de plantão",
        "Enviando notificação SMS para gerentes",
        "Ativando protocolo de emergência",
        "Iniciando procedimento de rollback"
    ]
    
    for action in actions:
        logger.info(f"Executando: {action}")

def process_security_breach(message, logger):
    """Processa violações de segurança"""
    source_ip = message.get('source_ip', 'unknown')
    attack_type = message.get('attack_type', 'unknown')
    
    logger.error(f"🔒 VIOLAÇÃO DE SEGURANÇA: {attack_type} de {source_ip}")
    
    # Simula ações de segurança
    logger.info(f"Bloqueando IP: {source_ip}")
    logger.info(f"Registrando tentativa de {attack_type}")
    logger.info("Notificando equipe de segurança")

def process_error_log(message, logger):
    """Processa logs de erro"""
    server = message.get('server', 'unknown')
    logger.error(f"⚠️ ERRO em {server}: {message.get('description', '')}")
    logger.info("Registrando erro para análise posterior")

def process_regular_message(message, logger):
    """Processa mensagens regulares"""
    msg_type = message.get('type', 'unknown')
    logger.info(f"📝 Processando {msg_type}: {message.get('description', '')}")

def print_stats(stats, logger):
    """Imprime estatísticas do consumer"""
    elapsed = datetime.now() - stats['start_time']
    rate = stats['processed'] / elapsed.total_seconds() if elapsed.total_seconds() > 0 else 0
    
    print(f"\n📊 ESTATÍSTICAS CONSUMER1:")
    print(f"   Total processadas: {stats['processed']}")
    print(f"   🚨 Críticas: {stats['critical']}")
    print(f"   ⚠️ Erros: {stats['errors']}")
    print(f"   🟡 Warnings: {stats['warnings']}")
    print(f"   ℹ️ Info: {stats['info']}")
    print(f"   🔍 Debug: {stats['debug']}")
    print(f"   📈 Taxa: {rate:.2f} msg/s")
    print(f"   ⏱️ Uptime: {str(elapsed).split('.')[0]}\n")

def print_final_stats(stats):
    """Imprime estatísticas finais"""
    elapsed = datetime.now() - stats['start_time']
    rate = stats['processed'] / elapsed.total_seconds() if elapsed.total_seconds() > 0 else 0
    
    print(f"\n📈 ESTATÍSTICAS FINAIS - CONSUMER1:")
    print(f"   Total processadas: {stats['processed']}")
    print(f"   Tempo total: {str(elapsed).split('.')[0]}")
    print(f"   Taxa média: {rate:.2f} msg/s")
    print(f"   Distribuição por prioridade:")
    print(f"     🚨 Críticas: {stats['critical']} ({stats['critical']/max(stats['processed'], 1)*100:.1f}%)")
    print(f"     ⚠️ Erros: {stats['errors']} ({stats['errors']/max(stats['processed'], 1)*100:.1f}%)")
    print(f"     🟡 Warnings: {stats['warnings']} ({stats['warnings']/max(stats['processed'], 1)*100:.1f}%)")
    print(f"     ℹ️ Info: {stats['info']} ({stats['info']/max(stats['processed'], 1)*100:.1f}%)")
    print(f"     🔍 Debug: {stats['debug']} ({stats['debug']/max(stats['processed'], 1)*100:.1f}%)")

if __name__ == "__main__":
    main()
