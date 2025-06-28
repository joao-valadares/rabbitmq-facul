"""
Consumer 3 para Priority Queue - Processador de Tarefas em Lote
Foca em processamento de baixa prioridade e tarefas de longo prazo
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
    COMPONENT_NAME = "consumer3"
    QUEUE_NAME = "priority_queue"
    
    # Setup
    print_scenario_header(
        SCENARIO_NAME, 
        COMPONENT_NAME, 
        "Consumer especializado em processamento em lote e tarefas de longo prazo"
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
        channel.basic_qos(prefetch_count=3)  # Processa até 3 mensagens simultaneamente
        
        # Estatísticas avançadas
        stats = {
            'processed': 0,
            'by_severity': {'CRITICAL': 0, 'ERROR': 0, 'WARNING': 0, 'INFO': 0, 'DEBUG': 0},
            'batch_jobs': 0,
            'quick_jobs': 0,
            'total_processing_time': 0,
            'start_time': datetime.now(),
            'priority_wait_times': {}  # Rastrea tempo de espera por prioridade
        }
        
        logger.info("Iniciando consumer de tarefas em lote...")
        print(f"\n🎯 CONSUMER 3: Processador de Tarefas em Lote")
        print(f"🐌 Estratégia: Otimizado para eficiência e throughput")
        print(f"📦 Especialidade: Processamento em lote e tarefas longas")
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
                timestamp = message.get('timestamp', '')
                
                # Calcula tempo de espera na fila
                if timestamp:
                    try:
                        msg_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00').replace('+00:00', ''))
                        wait_time = (datetime.now() - msg_time).total_seconds()
                        if priority not in stats['priority_wait_times']:
                            stats['priority_wait_times'][priority] = []
                        stats['priority_wait_times'][priority].append(wait_time)
                    except:
                        wait_time = 0
                else:
                    wait_time = 0
                
                # Atualiza estatísticas por severidade
                if severity in stats['by_severity']:
                    stats['by_severity'][severity] += 1
                
                # Ícone baseado na prioridade
                priority_icon = get_priority_icon(priority)
                
                # Log de recebimento com tempo de espera
                print(f"📥 MSG #{msg_id:03d} | "
                      f"{priority_icon} P{priority} | "
                      f"{severity:8s} | "
                      f"Wait: {wait_time:.1f}s | "
                      f"Processing...")
                
                start_time = time.time()
                
                # Processamento especializado
                if msg_type == "BATCH_PROCESS":
                    process_batch_job(message, logger)
                    stats['batch_jobs'] += 1
                elif msg_type == "DEBUG_LOG":
                    process_debug_analysis(message, logger)
                elif msg_type == "INFO_LOG":
                    process_info_aggregation(message, logger)
                elif priority <= 3:  # Baixa prioridade
                    process_low_priority_task(message, logger)
                else:
                    process_opportunistic_task(message, logger)
                    stats['quick_jobs'] += 1
                
                # Tempo de processamento otimizado para eficiência
                processing_time = get_efficient_processing_time(priority, msg_type)
                time.sleep(processing_time)
                
                end_time = time.time()
                actual_time = end_time - start_time
                stats['total_processing_time'] += actual_time
                
                # Log de conclusão
                elapsed = datetime.now() - stats['start_time']
                uptime = str(elapsed).split('.')[0]
                
                efficiency = "🔋" if actual_time <= 1.0 else "⚡" if actual_time <= 2.0 else "🕐"
                
                print(f"✅ MSG #{msg_id:03d} | "
                      f"{efficiency} {actual_time:.1f}s | "
                      f"Total: {stats['processed']} | "
                      f"Uptime: {uptime}")
                
                # Confirma processamento
                ch.basic_ack(delivery_tag=method.delivery_tag)
                
                # Log estatísticas a cada 20 mensagens
                if stats['processed'] % 20 == 0:
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
        print(f"\n✅ Finalizando consumer3...")
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

def get_efficient_processing_time(priority, msg_type):
    """Retorna tempo de processamento otimizado para eficiência"""
    # Consumer 3 é otimizado para throughput, não velocidade individual
    base_times = {
        "BATCH_PROCESS": 2.0,
        "DEBUG_LOG": 0.8,
        "INFO_LOG": 0.6,
        "WARNING": 0.4,
        "ERROR_LOG": 0.3,
        "SECURITY_BREACH": 0.2,
        "CRITICAL_ALERT": 0.1
    }
    
    base_time = base_times.get(msg_type, 1.0)
    
    # Menos variação para melhor previsibilidade
    variation = random.uniform(0.9, 1.1)  # ±10% de variação
    
    return round(base_time * variation, 1)

def process_batch_job(message, logger):
    """Processa trabalhos em lote"""
    records_count = message.get('records_count', 0)
    estimated_time = message.get('estimated_time', 'unknown')
    
    logger.info(f"📦 PROCESSAMENTO EM LOTE: {records_count} registros")
    logger.info(f"Tempo estimado: {estimated_time}")
    
    # Simula processamento em lote otimizado
    steps = [
        "Validando integridade dos dados",
        "Configurando pipeline de processamento",
        "Iniciando processamento em chunks",
        "Aplicando transformações",
        "Validando resultados",
        "Persistindo dados processados",
        "Atualizando índices",
        "Gerando relatório de conclusão"
    ]
    
    for i, step in enumerate(steps, 1):
        logger.info(f"[{i}/{len(steps)}] {step}")

def process_debug_analysis(message, logger):
    """Processa análise de debug"""
    logger.debug(f"🔍 ANÁLISE DE DEBUG: {message.get('description', '')}")
    
    # Análise detalhada para desenvolvimento
    logger.debug("Coletando contexto de execução")
    logger.debug("Analisando call stack")
    logger.debug("Verificando estado das variáveis")
    logger.debug("Gerando relatório de debug")

def process_info_aggregation(message, logger):
    """Processa agregação de informações"""
    logger.info(f"ℹ️ AGREGAÇÃO DE INFO: {message.get('description', '')}")
    
    # Agregação para relatórios
    logger.info("Coletando métricas relacionadas")
    logger.info("Atualizando dashboards")
    logger.info("Consolidando estatísticas")

def process_low_priority_task(message, logger):
    """Processa tarefas de baixa prioridade"""
    msg_type = message.get('type', 'unknown')
    logger.info(f"🔽 BAIXA PRIORIDADE: {msg_type}")
    
    # Processamento otimizado para eficiência
    logger.info("Executando com recursos otimizados")
    logger.info("Processamento em background")

def process_opportunistic_task(message, logger):
    """Processa tarefas oportunísticas (quando há capacidade)"""
    msg_type = message.get('type', 'unknown')
    logger.info(f"⚡ OPORTUNÍSTICO: {msg_type}")
    
    # Aproveita capacidade ociosa
    logger.info("Aproveitando capacidade disponível")

def print_stats(stats, logger):
    """Imprime estatísticas do consumer"""
    elapsed = datetime.now() - stats['start_time']
    rate = stats['processed'] / elapsed.total_seconds() if elapsed.total_seconds() > 0 else 0
    
    avg_processing = stats['total_processing_time'] / stats['processed'] if stats['processed'] > 0 else 0
    
    # Calcula tempos médios de espera por prioridade
    avg_wait_times = {}
    for priority, times in stats['priority_wait_times'].items():
        if times:
            avg_wait_times[priority] = sum(times) / len(times)
    
    print(f"\n📊 ESTATÍSTICAS CONSUMER3:")
    print(f"   Total processadas: {stats['processed']}")
    print(f"   📦 Trabalhos em lote: {stats['batch_jobs']}")
    print(f"   ⚡ Trabalhos rápidos: {stats['quick_jobs']}")
    print(f"   📈 Taxa: {rate:.2f} msg/s")
    print(f"   ⏱️ Proc. médio: {avg_processing:.2f}s")
    
    if avg_wait_times:
        print(f"   ⏳ Tempos de espera médios:")
        for priority in sorted(avg_wait_times.keys(), reverse=True):
            icon = get_priority_icon(priority)
            print(f"      {icon} P{priority}: {avg_wait_times[priority]:.1f}s")
    
    print(f"   ⏱️ Uptime: {str(elapsed).split('.')[0]}\n")

def print_final_stats(stats):
    """Imprime estatísticas finais"""
    elapsed = datetime.now() - stats['start_time']
    rate = stats['processed'] / elapsed.total_seconds() if elapsed.total_seconds() > 0 else 0
    
    avg_processing = stats['total_processing_time'] / stats['processed'] if stats['processed'] > 0 else 0
    
    print(f"\n📈 ESTATÍSTICAS FINAIS - CONSUMER3:")
    print(f"   Total processadas: {stats['processed']}")
    print(f"   Tempo total: {str(elapsed).split('.')[0]}")
    print(f"   Taxa média: {rate:.2f} msg/s")
    print(f"   Tempo proc. médio: {avg_processing:.2f}s")
    print(f"   Eficiência geral: {(stats['processed'] / elapsed.total_seconds() * avg_processing):.2f}")
    
    print(f"\n   🎯 Especialização:")
    print(f"     📦 Trabalhos em lote: {stats['batch_jobs']} ({stats['batch_jobs']/max(stats['processed'], 1)*100:.1f}%)")
    print(f"     ⚡ Trabalhos rápidos: {stats['quick_jobs']} ({stats['quick_jobs']/max(stats['processed'], 1)*100:.1f}%)")
    
    print(f"\n   🔍 Distribuição por severidade:")
    for severity, count in stats['by_severity'].items():
        if count > 0:
            percentage = (count / stats['processed']) * 100
            print(f"     {severity}: {count} ({percentage:.1f}%)")
    
    # Análise de eficiência da priorização
    if stats['priority_wait_times']:
        print(f"\n   ⏳ Eficiência da priorização:")
        all_wait_times = []
        for priority, times in stats['priority_wait_times'].items():
            if times:
                avg_wait = sum(times) / len(times)
                all_wait_times.extend(times)
                icon = get_priority_icon(priority)
                print(f"     {icon} P{priority}: {avg_wait:.1f}s médio ({len(times)} msgs)")
        
        if all_wait_times:
            overall_avg = sum(all_wait_times) / len(all_wait_times)
            print(f"     📊 Tempo médio geral: {overall_avg:.1f}s")

if __name__ == "__main__":
    main()
