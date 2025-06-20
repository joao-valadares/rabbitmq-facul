# filepath: c:\Users\joaog\Documents\Projetos Pessoais\rabbitmq-facul\interoperability\consumer2.js
/**
 * Consumer Node.js para Interoperabilidade
 * Demonstra consumo de mensagens enviadas pelo producer Python usando Node.js
 */

const amqp = require('amqplib');
const os = require('os');

// Configurações
const SCENARIO_NAME = "interoperability";
const COMPONENT_NAME = "consumer2-nodejs";
const QUEUE_NAME = "nodejs_queue";

// Configurações do RabbitMQ via env vars
const RABBITMQ_HOST = process.env.RABBITMQ_HOST || 'localhost';
const RABBITMQ_PORT = process.env.RABBITMQ_PORT || 5672;
const RABBITMQ_USER = process.env.RABBITMQ_USER || 'guest';
const RABBITMQ_PASS = process.env.RABBITMQ_PASS || 'guest';

// Estatísticas globais
const stats = {
    processed: 0,
    byType: {},
    errors: 0,
    processingTimes: [],
    startTime: new Date()
};

/**
 * Função principal
 */
async function main() {
    console.log('\n' + '='.repeat(80));
    console.log(`🌐 CENÁRIO: ${SCENARIO_NAME} | COMPONENTE: ${COMPONENT_NAME}`);
    console.log('Consumer Node.js para demonstração de interoperabilidade');
    console.log('='.repeat(80));
    
    printConfigInfo();
    
    try {
        // Conecta ao RabbitMQ
        console.log('\n📡 Conectando ao RabbitMQ...');
        const connection = await amqp.connect({
            hostname: RABBITMQ_HOST,
            port: RABBITMQ_PORT,
            username: RABBITMQ_USER,
            password: RABBITMQ_PASS
        });
        
        const channel = await connection.createChannel();
        
        // Declara a fila (idempotente)
        console.log(`📦 Declarando fila '${QUEUE_NAME}'...`);
        await channel.assertQueue(QUEUE_NAME, { durable: true });
        
        // Configurações do consumer
        await channel.prefetch(1);
        
        console.log('\n🟢 CONSUMER NODE.JS: Processador JavaScript');
        console.log(`📋 Fila: ${QUEUE_NAME}`);
        console.log('🔧 Runtime: Node.js');
        console.log('📦 Biblioteca: amqplib');
        console.log('🔄 Pressione Ctrl+C para parar\n');
        
        // Processa mensagens
        await channel.consume(QUEUE_NAME, async (msg) => {
            if (msg !== null) {
                await processMessage(channel, msg);
            }
        }, { noAck: false });
        
        console.log('⏳ Aguardando mensagens. Para sair, pressione CTRL+C');
        
        // Graceful shutdown
        process.on('SIGINT', () => {
            console.log('\n✅ Finalizando consumer Node.js...');
            printFinalStats();
            connection.close();
            process.exit(0);
        });
        
    } catch (error) {
        console.error('❌ Erro no consumer:', error.message);
        process.exit(1);
    }
}

/**
 * Processa uma mensagem
 */
async function processMessage(channel, msg) {
    const startTime = Date.now();
    
    try {
        // Decodifica mensagem JSON
        const messageText = msg.content.toString();
        const message = JSON.parse(messageText);
        
        stats.processed++;
        
        // Extrai metadados
        const msgType = message.type || 'UNKNOWN';
        const meta = message._meta || {};
        
        const producerLang = meta.producer || 'unknown';
        const messageId = meta.message_id || 'unknown';
        const correlationId = meta.correlation_id || 'unknown';
        
        // Atualiza estatísticas por tipo
        if (!stats.byType[msgType]) {
            stats.byType[msgType] = 0;
        }
        stats.byType[msgType]++;
        
        // Log de recebimento
        console.log(`📥 MSG #${stats.processed.toString().padStart(3, '0')} | ` +
                   `🐍→🟢 | ` +
                   `${msgType.padEnd(20)} | ` +
                   `Processing...`);
        
        // Processamento específico por tipo em Node.js
        switch (msgType) {
            case 'USER_REGISTRATION':
                await processUserRegistrationNodejs(message);
                break;
            case 'ORDER_CREATED':
                await processOrderCreatedNodejs(message);
                break;
            case 'PAYMENT_PROCESSED':
                await processPaymentProcessedNodejs(message);
                break;
            case 'INVENTORY_UPDATE':
                await processInventoryUpdateNodejs(message);
                break;
            case 'NOTIFICATION_SEND':
                await processNotificationSendNodejs(message);
                break;
            default:
                await processGenericMessageNodejs(message);
        }
        
        // Simula tempo de processamento
        const processingTime = Math.random() * 500 + 200; // 200-700ms
        await sleep(processingTime);
        
        const endTime = Date.now();
        const actualTime = (endTime - startTime) / 1000;
        stats.processingTimes.push(actualTime);
        
        // Log de conclusão
        const elapsed = new Date() - stats.startTime;
        const uptime = formatDuration(elapsed);
        
        console.log(`✅ MSG #${stats.processed.toString().padStart(3, '0')} | ` +
                   `🟢 Node.js | ` +
                   `${actualTime.toFixed(2)}s | ` +
                   `ID: ${correlationId} | ` +
                   `Uptime: ${uptime}`);
        
        // Confirma processamento
        channel.ack(msg);
        
        // Log estatísticas a cada 10 mensagens
        if (stats.processed % 10 === 0) {
            printStats();
        }
        
    } catch (error) {
        stats.errors++;
        console.error('❌ Erro no processamento:', error.message);
        
        // Rejeita mensagem (não requeue se for erro de JSON)
        const requeue = !(error instanceof SyntaxError);
        channel.nack(msg, false, requeue);
    }
}

/**
 * Processa registro de usuário usando recursos Node.js
 */
async function processUserRegistrationNodejs(message) {
    const { user_id, email, name, metadata = {} } = message;
    
    console.log(`🆕 Novo usuário registrado: ${name} (${email})`);
    
    // Demonstra recursos específicos do Node.js
    // Destructuring e template literals
    const domain = email ? email.split('@')[1] : 'unknown';
    console.log(`Domínio de email: ${domain}`);
    
    // Object methods
    const userInfo = Object.fromEntries(
        Object.entries(message).filter(([key]) => !key.startsWith('_') && key !== 'type')
    );
    
    console.log(`Dados processados: ${Object.keys(userInfo).length} campos`);
    
    // Set operations
    const requiredFields = new Set(['user_id', 'email', 'name']);
    const presentFields = new Set(Object.keys(message));
    const missingFields = [...requiredFields].filter(field => !presentFields.has(field));
    
    if (missingFields.length > 0) {
        console.log(`⚠️ Campos obrigatórios ausentes: ${missingFields.join(', ')}`);
    } else {
        console.log('✅ Todos os campos obrigatórios presentes');
    }
    
    // Async simulation
    console.log('Executando validações Node.js...');
    await sleep(50);
    console.log('Salvando no banco de dados...');
    await sleep(100);
    console.log('Enviando email de boas-vindas...');
}

/**
 * Processa criação de pedido usando recursos Node.js
 */
async function processOrderCreatedNodejs(message) {
    const { order_id, items = [], total = 0 } = message;
    
    console.log(`📦 Novo pedido: ${order_id} - Total: $${total.toFixed(2)}`);
    
    // Array methods modernos
    const totalItems = items.reduce((sum, item) => sum + (item.quantity || 0), 0);
    const avgPrice = totalItems > 0 ? total / totalItems : 0;
    
    // Map e filter
    const productIds = items.map(item => item.product_id);
    const expensiveItems = items.filter(item => (item.price || 0) > 50);
    
    console.log(`Itens totais: ${totalItems}`);
    console.log(`Preço médio: $${avgPrice.toFixed(2)}`);
    console.log(`Itens caros (>$50): ${expensiveItems.length}`);
    console.log(`Produtos: ${productIds.join(', ')}`);
    
    // Promise.all para processamento paralelo
    console.log('Processamento paralelo...');
    await Promise.all([
        simulateAsync('Validando estoque', 100),
        simulateAsync('Calculando frete', 150),
        simulateAsync('Gerando nota fiscal', 200)
    ]);
}

/**
 * Processa pagamento usando recursos Node.js
 */
async function processPaymentProcessedNodejs(message) {
    const { payment_id, amount = 0, status, gateway } = message;
    
    console.log(`💳 Pagamento ${payment_id}: ${status} - $${amount.toFixed(2)} via ${gateway}`);
    
    // Switch moderno com break implícito
    switch (status) {
        case 'success':
            console.log('✅ Pagamento aprovado - Liberando pedido');
            break;
        case 'failed':
            console.log('❌ Pagamento rejeitado - Notificando cliente');
            break;
        case 'pending':
            console.log('⏳ Pagamento pendente - Aguardando confirmação');
            break;
        default:
            console.log(`⚠️ Status desconhecido: ${status}`);
    }
    
    // Formatação usando Intl
    try {
        const formatter = new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'USD'
        });
        const formattedAmount = formatter.format(amount);
        console.log(`Valor formatado: ${formattedAmount}`);
    } catch (error) {
        console.log(`Valor: $${amount.toFixed(2)}`);
    }
    
    // Async/await chain
    console.log('Atualizando status do pedido...');
    await sleep(80);
    console.log('Registrando transação...');
}

/**
 * Processa atualização de estoque usando recursos Node.js
 */
async function processInventoryUpdateNodejs(message) {
    const { product_id, quantity = 0, operation, warehouse } = message;
    
    console.log(`📦 Estoque ${product_id}: ${operation} ${quantity} unidades em ${warehouse}`);
    
    // Map com operações
    const OPERATIONS = new Map([
        ['add', 'Adicionando ao estoque'],
        ['remove', 'Removendo do estoque'],
        ['set', 'Definindo estoque'],
        ['reserve', 'Reservando itens']
    ]);
    
    const operationDesc = OPERATIONS.get(operation) || `Operação desconhecida: ${operation}`;
    console.log(operationDesc);
    
    // Array.from com função geradora
    if (operation === 'add' && quantity > 100) {
        const batches = Array.from({ length: 10 }, (_, i) => Math.floor(quantity / 10));
        console.log(`Processando em lotes: ${batches.slice(0, 3).join(', ')}... (total: ${batches.length} lotes)`);
    }
    
    // Sequential async operations
    for (const step of ['Validando produto', 'Atualizando banco', 'Notificando compras']) {
        console.log(step + '...');
        await sleep(30);
    }
}

/**
 * Processa notificação usando recursos Node.js
 */
async function processNotificationSendNodejs(message) {
    const { notification_id, recipient, channel, message: msgText, priority = 1 } = message;
    
    console.log(`📱 Notificação ${notification_id}: ${channel} para ${recipient}`);
    
    // Conditional (ternary) operators encadeados
    const priorityEmoji = priority >= 4 ? '🔴' : priority >= 2 ? '🟡' : '🟢';
    console.log(`Prioridade: ${priorityEmoji} ${priority}/5`);
    
    // Buffer para demonstrar encoding
    const msgBuffer = Buffer.from(msgText, 'utf8');
    console.log(`Tamanho da mensagem: ${msgBuffer.length} bytes`);
    
    // Try/catch com diferentes tipos de erro
    try {
        const channelHandlers = {
            email: () => console.log('📧 Preparando envio por email...'),
            sms: () => console.log('📱 Preparando envio por SMS...'),
            push: () => console.log('🔔 Preparando push notification...')
        };
        
        const handler = channelHandlers[channel];
        if (!handler) {
            throw new Error(`Canal não suportado: ${channel}`);
        }
        
        handler();
        console.log('✅ Notificação enviada com sucesso');
        
    } catch (error) {
        console.error(`Erro de configuração: ${error.message}`);
    }
}

/**
 * Processa mensagem genérica mostrando recursos Node.js
 */
async function processGenericMessageNodejs(message) {
    const msgType = message.type || 'UNKNOWN';
    
    console.log(`🔧 Processamento genérico Node.js: ${msgType}`);
    
    // Object methods e reflection
    const fields = Object.keys(message).filter(key => !key.startsWith('_'));
    console.log(`Campos disponíveis: ${fields.join(', ')}`);
    
    // Array methods para verificação
    const hasStringFields = Object.values(message).some(value => typeof value === 'string');
    const allFieldsPresent = ['type'].every(field => message[field]);
    
    console.log(`Tem campos string: ${hasStringFields}`);
    console.log(`Campos obrigatórios: ${allFieldsPresent}`);
}

/**
 * Utilitário para sleep async
 */
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Simula operação assíncrona com nome
 */
async function simulateAsync(operation, ms) {
    console.log(`${operation}...`);
    await sleep(ms);
}

/**
 * Formata duração em formato legível
 */
function formatDuration(ms) {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    
    if (hours > 0) {
        return `${hours}:${(minutes % 60).toString().padStart(2, '0')}:${(seconds % 60).toString().padStart(2, '0')}`;
    } else {
        return `${minutes}:${(seconds % 60).toString().padStart(2, '0')}`;
    }
}

/**
 * Imprime informações de configuração
 */
function printConfigInfo() {
    console.log('\n🔧 CONFIGURAÇÕES:');
    console.log(`   Host: ${RABBITMQ_HOST}:${RABBITMQ_PORT}`);
    console.log(`   User: ${RABBITMQ_USER}`);
    console.log(`   Node: ${process.version}`);
    console.log(`   Platform: ${os.platform()} ${os.arch()}`);
    console.log(`   Memory: ${Math.round(process.memoryUsage().heapUsed / 1024 / 1024)} MB`);
}

/**
 * Imprime estatísticas periódicas
 */
function printStats() {
    const elapsed = new Date() - stats.startTime;
    const rate = stats.processed / (elapsed / 1000);
    const avgTime = stats.processingTimes.reduce((sum, time) => sum + time, 0) / stats.processingTimes.length;
    
    console.log('\n📊 ESTATÍSTICAS NODE.JS CONSUMER:');
    console.log(`   🟢 Total processadas: ${stats.processed}`);
    console.log(`   ❌ Erros: ${stats.errors}`);
    console.log(`   📈 Taxa: ${rate.toFixed(2)} msg/s`);
    console.log(`   ⏱️ Tempo médio: ${avgTime.toFixed(2)}s`);
    console.log('   📋 Distribuição por tipo:');
    
    Object.entries(stats.byType)
        .sort(([,a], [,b]) => b - a)
        .forEach(([type, count]) => {
            const percentage = (count / stats.processed) * 100;
            console.log(`      ${type}: ${count} (${percentage.toFixed(1)}%)`);
        });
    
    console.log(`   ⏱️ Uptime: ${formatDuration(elapsed)}\n`);
}

/**
 * Imprime estatísticas finais
 */
function printFinalStats() {
    const elapsed = new Date() - stats.startTime;
    const rate = stats.processed / (elapsed / 1000);
    
    const avgTime = stats.processingTimes.reduce((sum, time) => sum + time, 0) / stats.processingTimes.length || 0;
    const minTime = Math.min(...stats.processingTimes) || 0;
    const maxTime = Math.max(...stats.processingTimes) || 0;
    
    console.log('\n📈 ESTATÍSTICAS FINAIS - NODE.JS CONSUMER:');
    console.log(`   🟢 Linguagem: Node.js ${process.version}`);
    console.log(`   📦 Biblioteca: amqplib`);
    console.log(`   📊 Total processadas: ${stats.processed}`);
    console.log(`   ❌ Erros: ${stats.errors}`);
    console.log(`   ⏱️ Tempo total: ${formatDuration(elapsed)}`);
    console.log(`   📈 Taxa média: ${rate.toFixed(2)} msg/s`);
    console.log('   ⏱️ Tempos de processamento:');
    console.log(`      Médio: ${avgTime.toFixed(2)}s`);
    console.log(`      Mínimo: ${minTime.toFixed(2)}s`);
    console.log(`      Máximo: ${maxTime.toFixed(2)}s`);
    
    if (stats.processed > 0) {
        const successRate = ((stats.processed - stats.errors) / stats.processed) * 100;
        console.log(`   ✅ Taxa de sucesso: ${successRate.toFixed(1)}%`);
    }
    
    console.log('\n   🔧 Recursos Node.js demonstrados:');
    console.log('      • Async/await e Promises');
    console.log('      • Destructuring assignment');
    console.log('      • Template literals');
    console.log('      • Array methods (map, filter, reduce)');
    console.log('      • Object methods e Map/Set');
    console.log('      • Buffer para encoding');
    console.log('      • Intl para formatação');
}

// Executa se for arquivo principal
if (require.main === module) {
    main().catch(console.error);
}

module.exports = { processMessage, sleep };
