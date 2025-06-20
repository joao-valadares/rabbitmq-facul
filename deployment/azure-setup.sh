#!/bin/bash
# Setup script para Azure VMs - RabbitMQ Distributed Messaging

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para logging
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

# Verifica se é executado como root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        error "Este script deve ser executado como root (sudo)"
    fi
}

# Detecta distribuição Linux
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        VERSION=$VERSION_ID
    else
        error "Não foi possível detectar o sistema operacional"
    fi
    
    log "Sistema detectado: $OS $VERSION"
}

# Atualiza sistema
update_system() {
    log "Atualizando sistema..."
    
    case $OS in
        ubuntu|debian)
            apt-get update && apt-get upgrade -y
            apt-get install -y curl wget gnupg lsb-release software-properties-common
            ;;
        centos|rhel|fedora)
            yum update -y
            yum install -y curl wget gnupg which
            ;;
        *)
            error "Sistema operacional não suportado: $OS"
            ;;
    esac
}

# Instala Docker
install_docker() {
    log "Instalando Docker..."
    
    case $OS in
        ubuntu|debian)
            # Remove versões antigas
            apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true
            
            # Adiciona repositório Docker
            curl -fsSL https://download.docker.com/linux/$OS/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
            echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/$OS $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list
            
            # Instala Docker
            apt-get update
            apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
            ;;
        centos|rhel)
            # Remove versões antigas
            yum remove -y docker docker-client docker-client-latest docker-common docker-latest docker-latest-logrotate docker-logrotate docker-engine
            
            # Instala Docker
            yum install -y yum-utils
            yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
            yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
            ;;
        fedora)
            dnf remove -y docker docker-client docker-client-latest docker-common docker-latest docker-latest-logrotate docker-logrotate docker-selinux docker-engine-selinux docker-engine
            dnf install -y dnf-plugins-core
            dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo
            dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
            ;;
    esac
    
    # Inicia e habilita Docker
    systemctl start docker
    systemctl enable docker
    
    # Adiciona usuário ao grupo docker
    usermod -aG docker $SUDO_USER 2>/dev/null || true
    
    log "Docker instalado com sucesso"
}

# Instala Docker Compose (standalone)
install_docker_compose() {
    log "Instalando Docker Compose standalone..."
    
    # Download da versão mais recente
    DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep tag_name | cut -d'"' -f4)
    curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    
    # Cria link simbólico
    ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
    
    log "Docker Compose $DOCKER_COMPOSE_VERSION instalado"
}

# Instala RabbitMQ via Docker
install_rabbitmq() {
    log "Configurando RabbitMQ..."
    
    # Cria diretório para dados
    mkdir -p /opt/rabbitmq/data
    mkdir -p /opt/rabbitmq/logs
    
    # Configura permissões
    chown -R 999:999 /opt/rabbitmq
    
    # Para o container se estiver rodando
    docker stop rabbitmq-server 2>/dev/null || true
    docker rm rabbitmq-server 2>/dev/null || true
    
    # Executa RabbitMQ
    docker run -d \
        --name rabbitmq-server \
        --restart unless-stopped \
        -p 5672:5672 \
        -p 15672:15672 \
        -v /opt/rabbitmq/data:/var/lib/rabbitmq \
        -v /opt/rabbitmq/logs:/var/log/rabbitmq \
        -e RABBITMQ_DEFAULT_USER=admin \
        -e RABBITMQ_DEFAULT_PASS=admin123 \
        rabbitmq:3-management
    
    log "RabbitMQ iniciado. Management UI: http://$(curl -s ifconfig.me):15672"
    log "Usuário: admin | Senha: admin123"
}

# Instala Python e dependências
install_python() {
    log "Instalando Python e dependências..."
    
    case $OS in
        ubuntu|debian)
            apt-get install -y python3 python3-pip python3-venv
            ;;
        centos|rhel|fedora)
            if command -v dnf &> /dev/null; then
                dnf install -y python3 python3-pip
            else
                yum install -y python3 python3-pip
            fi
            ;;
    esac
    
    # Instala pika globalmente
    pip3 install pika python-dotenv
    
    log "Python configurado"
}

# Instala Node.js
install_nodejs() {
    log "Instalando Node.js..."
    
    # Instala Node.js via NodeSource
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - 2>/dev/null || {
        curl -fsSL https://rpm.nodesource.com/setup_18.x | bash - 2>/dev/null || {
            error "Falha ao configurar repositório Node.js"
        }
    }
    
    case $OS in
        ubuntu|debian)
            apt-get install -y nodejs
            ;;
        centos|rhel|fedora)
            if command -v dnf &> /dev/null; then
                dnf install -y nodejs npm
            else
                yum install -y nodejs npm
            fi
            ;;
    esac
    
    # Verifica instalação
    node --version
    npm --version
    
    log "Node.js instalado"
}

# Instala Java
install_java() {
    log "Instalando Java..."
    
    case $OS in
        ubuntu|debian)
            apt-get install -y openjdk-11-jdk maven
            ;;
        centos|rhel|fedora)
            if command -v dnf &> /dev/null; then
                dnf install -y java-11-openjdk-devel maven
            else
                yum install -y java-11-openjdk-devel maven
            fi
            ;;
    esac
    
    # Configura JAVA_HOME
    JAVA_HOME=$(readlink -f /usr/bin/java | sed "s:bin/java::")
    echo "export JAVA_HOME=$JAVA_HOME" >> /etc/environment
    
    log "Java instalado"
}

# Configura firewall
configure_firewall() {
    log "Configurando firewall..."
    
    # Detecta serviço de firewall
    if command -v ufw &> /dev/null; then
        # Ubuntu/Debian - UFW
        ufw allow 22/tcp      # SSH
        ufw allow 5672/tcp    # RabbitMQ AMQP
        ufw allow 15672/tcp   # RabbitMQ Management
        ufw allow 80/tcp      # HTTP
        ufw allow 443/tcp     # HTTPS
        ufw --force enable
        log "UFW configurado"
        
    elif command -v firewall-cmd &> /dev/null; then
        # CentOS/RHEL/Fedora - firewalld
        systemctl start firewalld
        systemctl enable firewalld
        
        firewall-cmd --permanent --add-port=22/tcp
        firewall-cmd --permanent --add-port=5672/tcp
        firewall-cmd --permanent --add-port=15672/tcp
        firewall-cmd --permanent --add-port=80/tcp
        firewall-cmd --permanent --add-port=443/tcp
        firewall-cmd --reload
        log "firewalld configurado"
        
    else
        warn "Nenhum serviço de firewall conhecido encontrado"
    fi
}

# Cria usuário para aplicação
create_app_user() {
    log "Criando usuário para aplicação..."
    
    # Cria usuário rabbitmq-app se não existir
    if ! id "rabbitmq-app" &>/dev/null; then
        useradd -m -s /bin/bash rabbitmq-app
        usermod -aG docker rabbitmq-app
        
        # Cria estrutura de diretórios
        mkdir -p /home/rabbitmq-app/{logs,configs,scripts}
        chown -R rabbitmq-app:rabbitmq-app /home/rabbitmq-app
        
        log "Usuário rabbitmq-app criado"
    else
        log "Usuário rabbitmq-app já existe"
    fi
}

# Configura monitoramento básico
setup_monitoring() {
    log "Configurando monitoramento básico..."
    
    # Script de health check
    cat > /opt/rabbitmq-healthcheck.sh << 'EOF'
#!/bin/bash
# Health check script para RabbitMQ

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Verifica se RabbitMQ está rodando
if docker ps | grep -q rabbitmq-server; then
    echo "[$TIMESTAMP] RabbitMQ: RUNNING"
    
    # Verifica se está respondendo
    if curl -s -u admin:admin123 http://localhost:15672/api/overview > /dev/null; then
        echo "[$TIMESTAMP] RabbitMQ API: OK"
    else
        echo "[$TIMESTAMP] RabbitMQ API: ERROR"
    fi
else
    echo "[$TIMESTAMP] RabbitMQ: NOT RUNNING"
    echo "[$TIMESTAMP] Tentando reiniciar..."
    docker start rabbitmq-server
fi
EOF
    
    chmod +x /opt/rabbitmq-healthcheck.sh
    
    # Adiciona ao crontab para executar a cada 5 minutos
    (crontab -l 2>/dev/null; echo "*/5 * * * * /opt/rabbitmq-healthcheck.sh >> /var/log/rabbitmq-health.log 2>&1") | crontab -
    
    log "Monitoramento configurado"
}

# Cria arquivo de configuração
create_config_file() {
    log "Criando arquivo de configuração..."
    
    # IP público da instância
    PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || echo "localhost")
    
    cat > /home/rabbitmq-app/.env << EOF
# Configurações RabbitMQ para Azure VM
RABBITMQ_HOST=$PUBLIC_IP
RABBITMQ_PORT=5672
RABBITMQ_USER=admin
RABBITMQ_PASS=admin123

# Configurações de log
LOG_LEVEL=INFO

# Configurações da aplicação
APP_ENV=production
APP_VERSION=1.0.0

# Azure metadata (se disponível)
AZURE_REGION=$(curl -s -H Metadata:true "http://169.254.169.254/metadata/instance/compute/location?api-version=2021-02-01&format=text" 2>/dev/null || echo "unknown")
AZURE_VM_SIZE=$(curl -s -H Metadata:true "http://169.254.169.254/metadata/instance/compute/vmSize?api-version=2021-02-01&format=text" 2>/dev/null || echo "unknown")
EOF
    
    chown rabbitmq-app:rabbitmq-app /home/rabbitmq-app/.env
    
    log "Arquivo de configuração criado em /home/rabbitmq-app/.env"
}

# Instala utilitários adicionais
install_utilities() {
    log "Instalando utilitários adicionais..."
    
    case $OS in
        ubuntu|debian)
            apt-get install -y htop iotop git vim nano unzip tree jq
            ;;
        centos|rhel|fedora)
            if command -v dnf &> /dev/null; then
                dnf install -y htop iotop git vim nano unzip tree jq
            else
                yum install -y htop iotop git vim nano unzip tree jq
            fi
            ;;
    esac
    
    log "Utilitários instalados"
}

# Função principal
main() {
    log "=== INICIANDO SETUP DE VM AZURE PARA RABBITMQ ==="
    
    check_root
    detect_os
    update_system
    install_docker
    install_docker_compose
    install_python
    install_nodejs
    install_java
    create_app_user
    install_rabbitmq
    configure_firewall
    setup_monitoring
    create_config_file
    install_utilities
    
    log "=== SETUP CONCLUÍDO COM SUCESSO ==="
    echo
    echo -e "${BLUE}=== INFORMAÇÕES DA INSTALAÇÃO ===${NC}"
    echo -e "${GREEN}RabbitMQ Management UI:${NC} http://$(curl -s ifconfig.me):15672"
    echo -e "${GREEN}Usuário:${NC} admin"
    echo -e "${GREEN}Senha:${NC} admin123"
    echo -e "${GREEN}AMQP Port:${NC} 5672"
    echo
    echo -e "${YELLOW}Próximos passos:${NC}"
    echo "1. Faça login como usuário 'rabbitmq-app': sudo su - rabbitmq-app"
    echo "2. Clone o repositório do projeto"
    echo "3. Configure as variáveis de ambiente conforme necessário"
    echo "4. Execute os cenários de teste"
    echo
    echo -e "${BLUE}Logs de health check:${NC} /var/log/rabbitmq-health.log"
    echo -e "${BLUE}Configurações:${NC} /home/rabbitmq-app/.env"
    echo
}

# Executa função principal
main "$@"
