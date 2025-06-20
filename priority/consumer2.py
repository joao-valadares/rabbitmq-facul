"""
Consumer 2 para Priority Queue - Processador de Operações Gerais
Processa todas as mensagens mas foca em operações de médio prazo
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
    COMPONENT_NAME = "consumer2"
    QUEUE_NAME = "priority_queue"
    
    # Setup
    print_scenario_header(
        SCENARIO_NAME, 
        COMPONENT_NAME, 
        "Consumer para operações gerais e processamento balanceado"
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
        channel.basic_qos(prefetch_count=2)  # Processa até 2 mensagens simultaneamente
        
        # Estatísticas
        stats = {
            'processed': 0,
            'by_priority': {i: 0 for i in range(11)},  # 0-10
            'processing_times': [],
            'start_time': datetime.now()
        }
        
        logger.info("Iniciando consumer de operações gerais...")
        print(f"\n🎯 CONSUMER 2: Processador de Operações Gerais")
        print(f"⚖️ Estratégia: Balanceado entre velocidade e qualidade")
        print(f"🔢 Capacidade: Até 2 mensagens simultâneas")
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
                
                # Atualiza estatísticas de prioridade
                stats['by_priority'][priority] += 1
                
                # Ícone baseado na prioridade
                priority_icon = get_priority_icon(priority)
                
                # Log de recebimento
                print(f"📥 MSG #{msg_id:03s} | "
                      f"{priority_icon} P{priority} | "
                      f"{severity:8s} | "
                      f"{msg_type:15s} | "
                      f"Processing...")
                
                start_time = time.time()
                
                # Processamento baseado no tipo de mensagem
                if msg_type == "CRITICAL_ALERT":
                    process_critical_operations(message, logger)
                elif msg_type == "SECURITY_BREACH":
                    process_security_operations(message, logger)
                elif msg_type == "ERROR_LOG":
                    process_error_analysis(message, logger)
                elif msg_type == "WARNING":
                    process_warning_analysis(message, logger)
                elif msg_type == "BATCH_PROCESS":
                    process_batch_coordination(message, logger)
                else:
                    process_general_operations(message, logger)
                
                # Tempo de processamento consistente mas eficiente
                processing_time = get_balanced_processing_time(priority, msg_type)
                time.sleep(processing_time)
                
                end_time = time.time()
                actual_time = end_time - start_time
                stats['processing_times'].append(actual_time)
                
                # Log de conclusão
                elapsed = datetime.now() - stats['start_time']
                uptime = str(elapsed).split('.')[0]
                
                print(f"✅ MSG #{msg_id:03s} | "
                      f"Processed in {actual_time:.1f}s | "
                      f"Total: {stats['processed']} | "
                      f"Uptime: {uptime}")
                
                # Confirma processamento
                ch.basic_ack(delivery_tag=method.delivery_tag)
                
                # Log estatísticas a cada 15 mensagens
                if stats['processed'] % 15 == 0:
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
        print(f"\n✅ Finalizando consumer2...")
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

def get_balanced_processing_time(priority, msg_type):
    """Retorna tempo de processamento balanceado"""
    base_time = 0.5
    
    # Ajuste por prioridade (menos tempo para maior prioridade)
    priority_factor = (10 - priority) * 0.1
    
    # Ajuste por tipo de mensagem
    type_factors = {
        "CRITICAL_ALERT": 0.2,
        "SECURITY_BREACH": 0.4,
        "ERROR_LOG": 0.6,
        "WARNING": 0.8,
        "INFO_LOG": 1.0,
        "DEBUG_LOG": 1.2,
        "BATCH_PROCESS": 1.5
    }
    
    type_factor = type_factors.get(msg_type, 1.0)
    
    # Calcula tempo final com variação aleatória
    final_time = base_time + priority_factor + type_factor
    variation = random.uniform(0.8, 1.2)  # ±20% de variação
    
    return round(final_time * variation, 1)

def process_critical_operations(message, logger):
    """Processa operações críticas"""
    alert_code = message.get('alert_code', 'UNKNOWN')
    logger.warning(f"🚨 Operação crítica: {alert_code}")
    
    # Operações de suporte
    logger.info("Coletando logs do sistema")
    logger.info("Preparando relatório de incidente")
    logger.info("Atualizando dashboard de status")

def process_security_operations(message, logger):
    """Processa operações de segurança"""
    source_ip = message.get('source_ip', 'unknown')
    attack_type = message.get('attack_type', 'unknown')
    
    logger.error(f"🔒 Operação de segurança: {attack_type}")
    
    # Análise complementar
    logger.info(f"Analisando padrões de ataque de {source_ip}")
    logger.info("Atualizando regras de firewall")
    logger.info("Gerando relatório de segurança")

def process_error_analysis(message, logger):
    """Processa análise de erros"""
    server = message.get('server', 'unknown')
    logger.warning(f"⚠️ Análise de erro em {server}")
    
    # Análise detalhada
    logger.info("Coletando stack trace")
    logger.info("Verificando recursos do sistema")
    logger.info("Atualizando métricas de erro")

def process_warning_analysis(message, logger):
    """Processa análise de warnings"""
    logger.info(f"🟡 Análise de warning: {message.get('description', '')}")
    
    # Monitoramento preventivo
    logger.info("Verificando tendências")
    logger.info("Atualizando alertas preventivos")

def process_batch_coordination(message, logger):
    """Processa coordenação de lotes"""
    records_count = message.get('records_count', 0)
    estimated_time = message.get('estimated_time', 'unknown')
    
    logger.info(f"📦 Coordenação de lote: {records_count} registros")
    logger.info(f"Tempo estimado: {estimated_time}")
    
    # Preparação do ambiente
    logger.info("Reservando recursos computacionais")
    logger.info("Configurando pipeline de processamento")

def process_general_operations(message, logger):
    """Processa operações gerais"""
    msg_type = message.get('type', 'unknown')
    logger.info(f"📝 Operação geral: {msg_type}")
    logger.info("Processamento padrão executado")

def print_stats(stats, logger):
    """Imprime estatísticas do consumer"""
    elapsed = datetime.now() - stats['start_time']
    rate = stats['processed'] / elapsed.total_seconds() if elapsed.total_seconds() > 0 else 0
    
    avg_time = sum(stats['processing_times']) / len(stats['processing_times']) if stats['processing_times'] else 0
    
    print(f"\n📊 ESTATÍSTICAS CONSUMER2:")
    print(f"   Total processadas: {stats['processed']}")
    print(f"   📈 Taxa: {rate:.2f} msg/s")
    print(f"   ⏱️ Tempo médio: {avg_time:.2f}s")
    print(f"   🎯 Distribuição por prioridade:")
    
    for priority in range(10, -1, -1):
        count = stats['by_priority'][priority]
        if count > 0:
            percentage = (count / stats['processed']) * 100
            icon = get_priority_icon(priority)
            print(f"      {icon} P{priority}: {count} ({percentage:.1f}%)")
    
    print(f"   ⏱️ Uptime: {str(elapsed).split('.')[0]}\n")

def print_final_stats(stats):
    """Imprime estatísticas finais"""
    elapsed = datetime.now() - stats['start_time']
    rate = stats['processed'] / elapsed.total_seconds() if elapsed.total_seconds() > 0 else 0
    
    avg_time = sum(stats['processing_times']) / len(stats['processing_times']) if stats['processing_times'] else 0
    min_time = min(stats['processing_times']) if stats['processing_times'] else 0
    max_time = max(stats['processing_times']) if stats['processing_times'] else 0
    
    print(f"\n📈 ESTATÍSTICAS FINAIS - CONSUMER2:")
    print(f"   Total processadas: {stats['processed']}")
    print(f"   Tempo total: {str(elapsed).split('.')[0]}")
    print(f"   Taxa média: {rate:.2f} msg/s")
    print(f"   Tempos de processamento:")
    print(f"     Médio: {avg_time:.2f}s")
    print(f"     Mínimo: {min_time:.2f}s")
    print(f"     Máximo: {max_time:.2f}s")
    print(f"\n   🎯 Eficiência por prioridade:")
    
    # Mostra distribuição detalhada
    total_high_priority = sum(stats['by_priority'][i] for i in range(7, 11))
    total_medium_priority = sum(stats['by_priority'][i] for i in range(3, 7))
    total_low_priority = sum(stats['by_priority'][i] for i in range(0, 3))
    
    if stats['processed'] > 0:
        print(f"     🚨 Alta (7-10): {total_high_priority} ({total_high_priority/stats['processed']*100:.1f}%)")
        print(f"     🟡 Média (3-6): {total_medium_priority} ({total_medium_priority/stats['processed']*100:.1f}%)")
        print(f"     🔍 Baixa (0-2): {total_low_priority} ({total_low_priority/stats['processed']*100:.1f}%)")

if __name__ == "__main__":
    main()
