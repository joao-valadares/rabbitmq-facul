/**
 * Consumer JavaScript para Interoperabilidade
 * Demonstra consumo de mensagens enviadas pelo producer Python usando JavaScript
 */

const amqp = require('amqplib');
const os = require('os');

// Configurações
const SCENARIO_NAME = "interoperability";
const COMPONENT_NAME = "consumer3-javascript";
const QUEUE_NAME = "javascript_queue";

// Configurações do RabbitMQ via env vars
const RABBITMQ_HOST = process.env.RABBITMQ_HOST || 'localhost';
const RABBITMQ_PORT = process.env.RABBITMQ_PORT || 5672;
const RABBITMQ_USER = process.env.RABBITMQ_USER || 'guest';
const RABBITMQ_PASSWORD = process.env.RABBITMQ_PASSWORD || 'guest';

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
    console.log('Consumer JavaScript para demonstração de interoperabilidade');
    console.log('='.repeat(80));
    
    printConfigInfo();
    
    try {
        // Conecta ao RabbitMQ
        console.log('\n📡 Conectando ao RabbitMQ...');
        const connection = await amqp.connect({
            hostname: RABBITMQ_HOST,
            port: RABBITMQ_PORT,
            username: RABBITMQ_USER,
            password: RABBITMQ_PASSWORD
        });
        
        const channel = await connection.createChannel();
        
        // Declara a fila (idempotente)
        console.log(`📦 Declarando fila '${QUEUE_NAME}'...`);
        await channel.assertQueue(QUEUE_NAME, { durable: true });
        
        // Configurações do consumer
        await channel.prefetch(1);
        
        console.log('\n🟡 CONSUMER JAVASCRIPT: Processador Moderno');
        console.log(`📋 Fila: ${QUEUE_NAME}`);
        console.log(`🔧 Runtime: Node.js ${process.version}`);
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
            console.log('\n✅ Finalizando consumer JavaScript...');
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
        stats.byType[msgType] = (stats.byType[msgType] || 0) + 1;
        
        // Log de recebimento
        console.log(`📥 MSG #${stats.processed.toString().padStart(3, '0')} | 🐍→🟡 | ${msgType.padEnd(20)} | Processing...`);
        
        // Processamento específico por tipo em JavaScript
        switch (msgType) {
            case 'USER_REGISTRATION':
                await processUserRegistrationJS(message);
                break;
            case 'ORDER_CREATED':
                await processOrderCreatedJS(message);
                break;
            case 'PAYMENT_PROCESSED':
                await processPaymentProcessedJS(message);
                break;
            case 'INVENTORY_UPDATE':
                await processInventoryUpdateJS(message);
                break;
            case 'NOTIFICATION_SEND':
                await processNotificationSendJS(message);
                break;
            default:
                await processGenericMessageJS(message);
        }
        
        // Simula tempo de processamento
        await sleep(Math.random() * 300 + 200); // 200-500ms
        
        const endTime = Date.now();
        const actualTime = (endTime - startTime) / 1000;
        stats.processingTimes.push(actualTime);
        
        // Log de conclusão
        const elapsed = Date.now() - stats.startTime.getTime();
        const uptime = formatDuration(elapsed);
        
        console.log(`✅ MSG #${stats.processed.toString().padStart(3, '0')} | 🟡 JavaScript | ${actualTime.toFixed(2)}s | ID: ${correlationId} | Uptime: ${uptime}`);
        
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
 * Processa registro de usuário usando recursos JavaScript/ES6+
 */
async function processUserRegistrationJS(message) {
    const { user_id, email, name } = message;
    
    console.log(`🆕 Novo usuário registrado: ${name} (${email})`);
    
    // Demonstra recursos específicos do JavaScript
    // Destructuring e Optional chaining
    const domain = email?.split('@')?.[1] || 'unknown';
    console.log(`Domínio de email: ${domain}`);
    
    // Array methods e filter
    const userFields = Object.keys(message)
        .filter(field => !field.startsWith('_') && field !== 'type');
    
    console.log(`Dados processados: ${userFields.length} campos`);
    
    // Set operations com ES6
    const requiredFields = new Set(['user_id', 'email', 'name']);
    const presentFields = new Set(Object.keys(message));
    
    const missingFields = [...requiredFields]
        .filter(field => !presentFields.has(field));
    
    if (missingFields.length > 0) {
        console.log(`⚠️ Campos obrigatórios ausentes: ${missingFields.join(', ')}`);
    } else {
        console.log('✅ Todos os campos obrigatórios presentes');
    }
    
    // Promises com async/await
    console.log('Executando validações JavaScript...');
    await sleep(50);
    console.log('Salvando no banco de dados...');
    await sleep(100);
    console.log('Enviando email de boas-vindas...');
}

/**
 * Processa criação de pedido usando recursos JavaScript/ES6+
 */
async function processOrderCreatedJS(message) {
    const { order_id, items = [], total = 0 } = message;
    
    console.log(`📦 Novo pedido: ${order_id} - Total: $${total.toFixed(2)}`);
    
    // Array methods avançados
    const totalItems = items.reduce((sum, item) => sum + (item.quantity || 0), 0);
    const avgPrice = totalItems > 0 ? total / totalItems : 0;
    
    // Map e filter chains
    const productIds = items
        .filter(item => item.product_id)
        .map(item => item.product_id);
    
    const expensiveItemsCount = items
        .filter(item => item.price > 50)
        .length;
    
    console.log(`Itens totais: ${totalItems}`);
    console.log(`Preço médio: $${avgPrice.toFixed(2)}`);
    console.log(`Itens caros (>$50): ${expensiveItemsCount}`);
    console.log(`Produtos: ${productIds.join(', ')}`);
    
    // Promise.all para processamento paralelo
    console.log('Processamento paralelo...');
    const tasks = [
        { name: 'Validando estoque', delay: Math.random() * 100 + 50 },
        { name: 'Calculando frete', delay: Math.random() * 100 + 50 },
        { name: 'Gerando nota fiscal', delay: Math.random() * 100 + 50 }
    ];
    
    await Promise.all(tasks.map(async task => {
        console.log(`${task.name}...`);
        await sleep(task.delay);
    }));
}

/**
 * Processa pagamento usando recursos JavaScript/ES6+
 */
async function processPaymentProcessedJS(message) {
    const { payment_id, amount = 0, status, gateway } = message;
    
    console.log(`💳 Pagamento ${payment_id}: ${status} - $${amount.toFixed(2)} via ${gateway}`);
    
    // Switch com objeto literal (JavaScript pattern)
    const statusActions = {
        'success': () => console.log('✅ Pagamento aprovado - Liberando pedido'),
        'failed': () => console.log('❌ Pagamento rejeitado - Notificando cliente'),
        'pending': () => console.log('⏳ Pagamento pendente - Aguardando confirmação'),
        'default': () => console.log(`⚠️ Status desconhecido: ${status}`)
    };
    
    const action = statusActions[status] || statusActions.default;
    action();
    
    // Intl API para formatação de moeda
    try {
        const formatter = new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        });
        const formattedAmount = formatter.format(amount);
        console.log(`Valor formatado: ${formattedAmount}`);
    } catch (error) {
        console.log(`Valor: $${amount.toFixed(2)}`);
    }
    
    console.log('Atualizando status do pedido...');
    await sleep(80);
    console.log('Registrando transação...');
}

/**
 * Processa atualização de estoque usando recursos JavaScript/ES6+
 */
async function processInventoryUpdateJS(message) {
    const { product_id, quantity = 0, operation, warehouse } = message;
    
    console.log(`📦 Estoque ${product_id}: ${operation} ${quantity} unidades em ${warehouse}`);
    
    // Map com operações
    const operations = new Map([
        ['add', 'Adicionando ao estoque'],
        ['remove', 'Removendo do estoque'],
        ['set', 'Definindo estoque'],
        ['reserve', 'Reservando itens']
    ]);
    
    const operationDesc = operations.get(operation) || `Operação desconhecida: ${operation}`;
    console.log(operationDesc);
    
    // Array.from com generator function
    if (operation === 'add' && quantity > 100) {
        const batches = Array.from({ length: 10 }, (_, i) => Math.floor(quantity / 10));
        const batchPreview = batches.slice(0, 3).join(', ');
        
        console.log(`Processando em lotes: ${batchPreview}... (total: ${batches.length} lotes)`);
    }
    
    // Sequential async operations
    const steps = ['Validando produto', 'Atualizando banco', 'Notificando compras'];
    for (const step of steps) {
        console.log(`${step}...`);
        await sleep(30);
    }
}

/**
 * Processa notificação usando recursos JavaScript/ES6+
 */
async function processNotificationSendJS(message) {
    const { notification_id, recipient, channel, message: msgText, priority = 1 } = message;
    
    console.log(`📱 Notificação ${notification_id}: ${channel} para ${recipient}`);
    
    // Ternary operator com template literals
    const priorityEmoji = priority >= 4 ? '🔴' : priority >= 2 ? '🟡' : '🟢';
    console.log(`Prioridade: ${priorityEmoji} ${priority}/5`);
    
    // TextEncoder para bytes
    const encoder = new TextEncoder();
    const msgBytes = encoder.encode(msgText || '');
    console.log(`Tamanho da mensagem: ${msgBytes.length} bytes`);
    
    // Try-catch com object handlers
    try {
        const channelHandlers = {
            'email': () => console.log('📧 Preparando envio por email...'),
            'sms': () => console.log('📱 Preparando envio por SMS...'),
            'push': () => console.log('🔔 Preparando push notification...')
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
 * Processa mensagem genérica mostrando recursos JavaScript/ES6+
 */
async function processGenericMessageJS(message) {
    const msgType = message.type || 'UNKNOWN';
    
    console.log(`🔧 Processamento genérico JavaScript: ${msgType}`);
    
    // Object.keys com filter
    const fields = Object.keys(message)
        .filter(field => !field.startsWith('_'));
    
    console.log(`Campos disponíveis: ${fields.join(', ')}`);
    
    // Array predicates
    const hasStringFields = Object.values(message)
        .some(value => typeof value === 'string');
    
    const allFieldsPresent = ['type']
        .every(field => message.hasOwnProperty(field));
    
    console.log(`Tem campos string: ${hasStringFields}`);
    console.log(`Campos obrigatórios: ${allFieldsPresent}`);
}

/**
 * Utilitário para sleep usando Promise
 */
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
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
    console.log(`   Node.js: ${process.version}`);
    console.log(`   OS: ${os.type()} ${os.arch()}`);
    
    const memoryMB = Math.round(process.memoryUsage().heapUsed / 1024 / 1024);
    console.log(`   Memory: ${memoryMB} MB`);
}

/**
 * Imprime estatísticas periódicas
 */
function printStats() {
    const elapsed = Date.now() - stats.startTime.getTime();
    const rate = stats.processed / (elapsed / 1000 + 0.001);
    const avgTime = stats.processingTimes.length > 0 
        ? stats.processingTimes.reduce((a, b) => a + b, 0) / stats.processingTimes.length 
        : 0;
    
    console.log('\n📊 ESTATÍSTICAS JAVASCRIPT CONSUMER:');
    console.log(`   🟡 Total processadas: ${stats.processed}`);
    console.log(`   ❌ Erros: ${stats.errors}`);
    console.log(`   📈 Taxa: ${rate.toFixed(2)} msg/s`);
    console.log(`   ⏱️ Tempo médio: ${avgTime.toFixed(2)}s`);
    console.log('   📋 Distribuição por tipo:');
    
    // Sort by count descending
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
    const elapsed = Date.now() - stats.startTime.getTime();
    const rate = stats.processed / (elapsed / 1000 + 0.001);
    
    const avgTime = stats.processingTimes.length > 0 
        ? stats.processingTimes.reduce((a, b) => a + b, 0) / stats.processingTimes.length 
        : 0;
    const minTime = stats.processingTimes.length > 0 ? Math.min(...stats.processingTimes) : 0;
    const maxTime = stats.processingTimes.length > 0 ? Math.max(...stats.processingTimes) : 0;
    
    console.log('\n📈 ESTATÍSTICAS FINAIS - JAVASCRIPT CONSUMER:');
    console.log(`   🟡 Linguagem: JavaScript (Node.js ${process.version})`);
    console.log('   📦 Biblioteca: amqplib');
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
    
    console.log('\n   🔧 Recursos JavaScript demonstrados:');
    console.log('      • ES6+ Destructuring e Spread');
    console.log('      • Array methods (map, filter, reduce)');
    console.log('      • Async/await e Promises');
    console.log('      • Set e Map collections');
    console.log('      • Template literals');
    console.log('      • Optional chaining (?.)');
    console.log('      • Intl API para formatação');
    console.log('      • Promise.all para paralelismo');
}

// Executa se chamado diretamente
if (require.main === module) {
    main().catch(console.error);
}

module.exports = { main };
