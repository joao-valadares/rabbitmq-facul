#!/bin/bash
# Script de deployment para Azure VMs
# Automatiza criação de VMs e configuração do ambiente distribuído

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configurações padrão
RESOURCE_GROUP="rabbitmq-facul-rg"
LOCATION="brazilsouth"
VM_SIZE="Standard_B2s"
ADMIN_USERNAME="azureuser"
VM_COUNT=5  # ✅ Alterado de 3 para 5
PROJECT_NAME="rabbitmq-facul"
FORCE_REGEN_SSH=false  # ✅ Inicialização da variável SSH

# ✅ NOVA: Definição dos papéis das VMs
VM_ROLES=(
    "broker"      # VM1 - RabbitMQ Broker
    "producer"    # VM2 - Producer
    "consumer"    # VM3 - Consumer 1
    "consumer"    # VM4 - Consumer 2
    "consumer"    # VM5 - Consumer 3
)

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --regen-ssh)
            FORCE_REGEN_SSH=true
            shift
            ;;
        --help|-h)
            echo "Uso: $0 [opções]"
            echo "Opções:"
            echo "  --regen-ssh    Força regeneração da chave SSH"
            echo "  --help, -h     Mostra esta ajuda"
            exit 0
            ;;
        *)
            echo "Opção desconhecida: $1"
            echo "Use --help para ver as opções disponíveis"
            exit 1
            ;;
    esac
done

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

# Verifica se Azure CLI está instalado
check_azure_cli() {
    if ! command -v az &> /dev/null; then
        error "Azure CLI não está instalado. Instale: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    fi
    
    # Verifica se está logado
    if ! az account show &> /dev/null; then
        error "Não está logado no Azure. Execute: az login"
    fi
    
    log "Azure CLI configurado corretamente"
}

# ✅ NOVA: Cria ou verifica chave SSH
setup_ssh_key() {
    local ssh_dir="$HOME/.ssh"
    local key_name="${PROJECT_NAME}-key"
    local private_key_path="${ssh_dir}/${key_name}"
    local public_key_path="${private_key_path}.pub"
    
    # Converte o HOME para formato Windows se necessário
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]] && [[ "$ssh_dir" =~ ^/[a-z]/ ]]; then
        local drive=$(echo "$ssh_dir" | sed 's|^/\([a-z]\)/.*|\1|')
        local rest=$(echo "$ssh_dir" | sed 's|^/[a-z]/||')
        ssh_dir="${drive^^}:/${rest}"
        private_key_path="${ssh_dir}/${key_name}"
        public_key_path="${private_key_path}.pub"
    fi
    
    log "Configurando chave SSH para o projeto..."
    
    # Cria diretório .ssh se não existir
    if [ ! -d "$ssh_dir" ]; then
        log "Criando diretório $ssh_dir..."
        mkdir -p "$ssh_dir"
        chmod 700 "$ssh_dir"
    fi
    
    # Verifica se deve regenerar a chave
    if [ "$FORCE_REGEN_SSH" = "true" ] || [ ! -f "$private_key_path" ] || [ ! -f "$public_key_path" ]; then
        if [ -f "$private_key_path" ] || [ -f "$public_key_path" ]; then
            if [ "$FORCE_REGEN_SSH" = "true" ]; then
                log "Regenerando chave SSH existente..."
            else
                log "Chave SSH incompleta, criando nova..."
            fi
            rm -f "$private_key_path" "$public_key_path"
        else
            log "Criando nova chave SSH..."
        fi
        
        # Gera nova chave SSH
        ssh-keygen -t rsa -b 4096 \
            -f "$private_key_path" \
            -N "" \
            -C "${ADMIN_USERNAME}@${PROJECT_NAME}-azure" \
            > /dev/null
        
        if [ $? -eq 0 ]; then
            log "Chave SSH criada: $private_key_path"
        else
            error "Falha ao criar chave SSH"
        fi
        
        # Define permissões corretas
        chmod 600 "$private_key_path"
        chmod 644 "$public_key_path"
    else
        log "Usando chave SSH existente: $private_key_path"
    fi
    
    # Verifica se as chaves existem e são válidas
    if [ ! -f "$private_key_path" ] || [ ! -f "$public_key_path" ]; then
        error "Chaves SSH não encontradas após criação"
    fi
    
    # Exporta o caminho da chave pública para uso nas VMs
    export pub_key_path="$public_key_path"
    
    log "Chave SSH configurada: $public_key_path"
    
    # Mostra fingerprint da chave para verificação
    local fingerprint=$(ssh-keygen -lf "$public_key_path" 2>/dev/null | awk '{print $2}')
    if [ -n "$fingerprint" ]; then
        log "Fingerprint da chave: $fingerprint"
    fi
}

# Cria resource group
create_resource_group() {
    log "Criando resource group '$RESOURCE_GROUP'..."
    
    az group create \
        --name "$RESOURCE_GROUP" \
        --location "$LOCATION" \
        --tags project="$PROJECT_NAME" environment="academic" \
        --output table
    
    log "Resource group criado"
}

# ✅ ATUALIZADA: NSG específico por papel
create_nsg() {
    local nsg_name="${PROJECT_NAME}-nsg"
    
    log "Criando network security group '$nsg_name'..."
    
    # Cria NSG
    az network nsg create \
        --resource-group "$RESOURCE_GROUP" \
        --name "$nsg_name" \
        --location "$LOCATION" \
        --output table
    
    # Regras de segurança
    log "Configurando regras de segurança..."
    
    # SSH (todas as VMs)
    az network nsg rule create \
        --resource-group "$RESOURCE_GROUP" \
        --nsg-name "$nsg_name" \
        --name "AllowSSH" \
        --protocol tcp \
        --priority 1000 \
        --destination-port-range 22 \
        --access allow \
        --output table
    
    # RabbitMQ AMQP (apenas para broker, mas liberamos para todas por simplicidade)
    az network nsg rule create \
        --resource-group "$RESOURCE_GROUP" \
        --nsg-name "$nsg_name" \
        --name "AllowRabbitMQ" \
        --protocol tcp \
        --priority 1001 \
        --destination-port-range 5672 \
        --access allow \
        --output table
    
    # RabbitMQ Management (apenas broker)
    az network nsg rule create \
        --resource-group "$RESOURCE_GROUP" \
        --nsg-name "$nsg_name" \
        --name "AllowRabbitMQMgmt" \
        --protocol tcp \
        --priority 1002 \
        --destination-port-range 15672 \
        --access allow \
        --output table
    
    log "Network security group configurado"
}

# Cria virtual network
create_vnet() {
    local vnet_name="${PROJECT_NAME}-vnet"
    local subnet_name="${PROJECT_NAME}-subnet"
    
    log "Criando virtual network '$vnet_name'..."
    
    # Cria VNet
    az network vnet create \
        --resource-group "$RESOURCE_GROUP" \
        --name "$vnet_name" \
        --address-prefix 10.0.0.0/16 \
        --subnet-name "$subnet_name" \
        --subnet-prefix 10.0.1.0/24 \
        --location "$LOCATION" \
        --output table
    
    # Associa NSG à subnet
    az network vnet subnet update \
        --resource-group "$RESOURCE_GROUP" \
        --vnet-name "$vnet_name" \
        --name "$subnet_name" \
        --network-security-group "${PROJECT_NAME}-nsg" \
        --output table
    
    log "Virtual network criada"
}



# ✅ ATUALIZADA: Cria VMs com papéis específicos
create_vms() {
    local vnet_name="${PROJECT_NAME}-vnet"
    local subnet_name="${PROJECT_NAME}-subnet"
    
    log "Criando $VM_COUNT VMs com papéis específicos..."
    
    for i in $(seq 1 $VM_COUNT); do
        local vm_name="${PROJECT_NAME}-vm${i}"
        local pip_name="${vm_name}-pip"
        local role="${VM_ROLES[$((i-1))]}"  # ✅ Pega o papel da VM
        
        log "Criando VM $i de $VM_COUNT: $vm_name (Papel: $role)"
        
        # Create Public IP with Static allocation
        log "Criando IP público estático para $vm_name..."
        az network public-ip create \
            --resource-group "$RESOURCE_GROUP" \
            --name "$pip_name" \
            --allocation-method Static \
            --sku Standard \
            --location "$LOCATION" \
            --output table
        
        if [ $? -ne 0 ]; then
            error "Falha ao criar IP público para $vm_name"
        fi
        
        # Create VM with error handling
        log "Criando VM $vm_name..."
        if az vm create \
            --resource-group "$RESOURCE_GROUP" \
            --name "$vm_name" \
            --image "Ubuntu2204" \
            --size "$VM_SIZE" \
            --admin-username "$ADMIN_USERNAME" \
            --ssh-key-values "$pub_key_path" \
            --public-ip-address "$pip_name" \
            --vnet-name "$vnet_name" \
            --subnet "$subnet_name" \
            --nsg "${PROJECT_NAME}-nsg" \
            --location "$LOCATION" \
            --tags role="$role" project="$PROJECT_NAME" vm_number="$i" \
            --output table; then
            
            log "VM $vm_name criada com sucesso (papel: $role)"
        else
            error "Falha ao criar VM $vm_name"
        fi
        
        # Small delay between VM creations to avoid resource conflicts
        sleep 10
    done
    
    log "Todas as $VM_COUNT VMs foram criadas com sucesso"
}

# ✅ ATUALIZADA: Lista com papéis das VMs
list_vm_info() {
    log "Coletando informações das VMs..."
    
    echo -e "\n${BLUE}=== INFORMAÇÕES DAS VMs (Arquitetura 5 VMs) ===${NC}"
    
    for i in $(seq 1 $VM_COUNT); do
        local vm_name="${PROJECT_NAME}-vm${i}"
        local pip_name="${vm_name}-pip"
        local role="${VM_ROLES[$((i-1))]}"
        
        # Pega IP público
        local public_ip=$(az network public-ip show \
            --resource-group "$RESOURCE_GROUP" \
            --name "$pip_name" \
            --query "ipAddress" \
            --output tsv)
        
        # Pega IP privado
        local private_ip=$(az vm show \
            --resource-group "$RESOURCE_GROUP" \
            --name "$vm_name" \
            --show-details \
            --query "privateIps" \
            --output tsv)
        
        # ✅ Ícones por papel
        local icon=""
        case $role in
            "broker") icon="🏭" ;;
            "producer") icon="📤" ;;
            "consumer") icon="📥" ;;
        esac
        
        echo -e "${GREEN}VM $i - $vm_name ($icon $role):${NC}"
        echo -e "  IP Público:  $public_ip"
        echo -e "  IP Privado:  $private_ip"
        echo -e "  SSH:         ssh -i ~/.ssh/${PROJECT_NAME}-key ${ADMIN_USERNAME}@${public_ip}"
        if [ "$role" == "broker" ]; then
            echo -e "  RabbitMQ UI: http://${public_ip}:15672"
            echo -e "  Usuário:     admin / admin123"
        fi
        echo
    done
}

# ✅ ATUALIZADA: Configuração específica por papel
configure_vms() {
    # Converte o HOME para formato Windows se necessário
    local home_dir="$HOME"
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]] && [[ "$home_dir" =~ ^/[a-z]/ ]]; then
        local drive=$(echo "$home_dir" | sed 's|^/\([a-z]\)/.*|\1|')
        local rest=$(echo "$home_dir" | sed 's|^/[a-z]/||')
        home_dir="${drive^^}:/${rest}"
    fi
    
    local ssh_key_path="${home_dir}/.ssh/${PROJECT_NAME}-key"
    local broker_private_ip=""
    
    log "Configurando VMs remotamente com papéis específicos..."
    
    # Primeiro, pega o IP privado do broker
    local broker_private_ip=$(az vm show \
        --resource-group "$RESOURCE_GROUP" \
        --name "${PROJECT_NAME}-vm1" \
        --show-details \
        --query "privateIps" \
        --output tsv)
    
    log "IP privado do broker: $broker_private_ip"
    
    for i in $(seq 1 $VM_COUNT); do
        local vm_name="${PROJECT_NAME}-vm${i}"
        local pip_name="${vm_name}-pip"
        local role="${VM_ROLES[$((i-1))]}"
        
        # Pega IP público
        local public_ip=$(az network public-ip show \
            --resource-group "$RESOURCE_GROUP" \
            --name "$pip_name" \
            --query "ipAddress" \
            --output tsv)
        
        if [ -n "$public_ip" ] && [ "$public_ip" != "null" ]; then
            log "Configurando VM $vm_name ($role) - IP: $public_ip..."
            
            # Aguarda VM estar pronta
            log "Aguardando VM estar acessível..."
            for attempt in {1..30}; do
                if ssh -i "$ssh_key_path" -o ConnectTimeout=10 -o StrictHostKeyChecking=no \
                   "$ADMIN_USERNAME@$public_ip" "echo 'VM ready'" &>/dev/null; then
                    break
                fi
                
                if [ $attempt -eq 30 ]; then
                    warn "VM $vm_name não respondeu após 5 minutos"
                    continue 2
                fi
                
                sleep 10
            done
            
            # Copia script de setup
            scp -i "$ssh_key_path" -o StrictHostKeyChecking=no \
                "$(dirname $0)/azure-setup.sh" \
                "$ADMIN_USERNAME@$public_ip:/tmp/"
            
            # ✅ Executa setup com papel específico
            ssh -i "$ssh_key_path" -o StrictHostKeyChecking=no \
                "$ADMIN_USERNAME@$public_ip" \
                "sudo chmod +x /tmp/azure-setup.sh && sudo /tmp/azure-setup.sh --role $role --broker-ip $broker_private_ip"
            
            log "VM $vm_name ($role) configurada"
        else
            warn "Não foi possível obter IP público para VM $vm_name"
        fi
    done
    
    log "Configuração das VMs concluída"
}

# ✅ ATUALIZADA: Inventário com arquitetura das 5 VMs
create_inventory() {
    local inventory_file="azure-inventory.txt"
    local broker_private_ip=$(az vm show \
        --resource-group "$RESOURCE_GROUP" \
        --name "${PROJECT_NAME}-vm1" \
        --show-details \
        --query "privateIps" \
        --output tsv)
    
    log "Criando arquivo de inventário..."
    
    cat > "$inventory_file" << EOF
# 🌐 Inventário de VMs Azure - Projeto RabbitMQ Faculdade
# Arquitetura: 1 Broker + 1 Producer + 3 Consumers
# Gerado em: $(date)

Resource Group: $RESOURCE_GROUP
Location: $LOCATION
Project: $PROJECT_NAME
SSH Key: ~/.ssh/${PROJECT_NAME}-key

ARQUITETURA - 5 VMs:
═══════════════════

🏭 VM1 (Broker):     RabbitMQ Server + Management UI
📤 VM2 (Producer):   Python Producer Applications
📥 VM3 (Consumer1):  Python Consumer Applications
📥 VM4 (Consumer2):  Python Consumer Applications  
📥 VM5 (Consumer3):  Python/Node.js Consumer Applications

DETALHES DAS VMs:
═══════════════════
EOF
    
    for i in $(seq 1 $VM_COUNT); do
        local vm_name="${PROJECT_NAME}-vm${i}"
        local pip_name="${vm_name}-pip"
        local role="${VM_ROLES[$((i-1))]}"
        
        local public_ip=$(az network public-ip show \
            --resource-group "$RESOURCE_GROUP" \
            --name "$pip_name" \
            --query "ipAddress" \
            --output tsv 2>/dev/null || echo "N/A")
        
        local private_ip=$(az vm show \
            --resource-group "$RESOURCE_GROUP" \
            --name "$vm_name" \
            --show-details \
            --query "privateIps" \
            --output tsv 2>/dev/null || echo "N/A")
        
        local icon=""
        case $role in
            "broker") icon="🏭" ;;
            "producer") icon="📤" ;;
            "consumer") icon="📥" ;;
        esac
        
        cat >> "$inventory_file" << EOF

$icon VM $i - $vm_name ($role):
  IP Público:  $public_ip
  IP Privado:  $private_ip
  SSH:         ssh -i ~/.ssh/${PROJECT_NAME}-key ${ADMIN_USERNAME}@${public_ip}
EOF
        
        if [ "$role" == "broker" ]; then
            cat >> "$inventory_file" << EOF
  RabbitMQ UI: http://${public_ip}:15672
  Usuário:     admin / admin123
  AMQP URL:    amqp://admin:admin123@${private_ip}:5672
EOF
        fi
    done
    
    cat >> "$inventory_file" << EOF

CONFIGURAÇÃO DOS CONSUMERS:
═════════════════════════

Em cada VM de aplicação (VM2-VM5), configure o .env:
RABBITMQ_HOST=$broker_private_ip
RABBITMQ_PORT=5672
RABBITMQ_USER=admin
RABBITMQ_PASS=admin123

EXECUÇÃO DOS CENÁRIOS:
═══════════════════════

1. Clone o repositório em cada VM:
   git clone <seu-repo-url>
   cd rabbitmq-facul

2. Execute cenários (exemplo - Direct Exchange):
   
   📤 VM2 (Producer):
   cd direct_exchange/
   python3 producer.py
   
   📥 VM3 (Consumer1):
   cd direct_exchange/
   python3 consumer1.py
   
   📥 VM4 (Consumer2):
   cd direct_exchange/
   python3 consumer2.py
   
   📥 VM5 (Consumer3):
   cd direct_exchange/
   python3 consumer3.py

COMANDOS ÚTEIS:
═════════════════

# Verificar status RabbitMQ (VM1)
docker ps | grep rabbitmq
docker logs rabbitmq-server

# Monitorar filas
curl -u admin:admin123 http://localhost:15672/api/queues

# Conectar em todas as VMs
for i in {1..5}; do
  ssh -i ~/.ssh/${PROJECT_NAME}-key ${ADMIN_USERNAME}@<IP_VM\$i>
done

EOF
    
    log "Arquivo de inventário criado: $inventory_file"
}

# Cleanup - remove recursos
cleanup() {
    warn "Esta operação irá remover TODOS os recursos do projeto (5 VMs)!"
    read -p "Tem certeza? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log "Removendo resource group e todos os recursos..."
        az group delete --name "$RESOURCE_GROUP" --yes --no-wait
        log "Comando de remoção enviado. Recursos serão removidos em background."
    else
        log "Operação cancelada"
    fi
}

# Função de ajuda
show_help() {
    echo "Script de deployment para Azure VMs - Projeto RabbitMQ (5 VMs)"
    echo
    echo "Arquitetura:"
    echo "  🏭 VM1: Broker (RabbitMQ)"
    echo "  📤 VM2: Producer"  
    echo "  📥 VM3: Consumer 1"
    echo "  📥 VM4: Consumer 2"
    echo "  📥 VM5: Consumer 3"
    echo
    echo "Uso: $0 [COMANDO] [OPÇÕES]"
    echo
    echo "Comandos:"
    echo "  deploy     - Cria toda a infraestrutura (padrão)"
    echo "  info       - Lista informações das VMs existentes"
    echo "  inventory  - Cria arquivo de inventário"
    echo "  cleanup    - Remove todos os recursos"
    echo "  help       - Mostra esta ajuda"
    echo
    echo "Opções:"
    echo "  --regen-ssh    Força regeneração da chave SSH"
    echo "  --help, -h     Mostra esta ajuda"
    echo
    echo "Variáveis de ambiente (opcionais):"
    echo "  RESOURCE_GROUP  - Nome do resource group (padrão: $RESOURCE_GROUP)"
    echo "  LOCATION        - Região Azure (padrão: $LOCATION)"
    echo "  VM_SIZE         - Tamanho das VMs (padrão: $VM_SIZE)"
    echo
    echo "Exemplo:"
    echo "  LOCATION=eastus VM_SIZE=Standard_B4ms $0 deploy"
    echo "  $0 deploy --regen-ssh"
    echo "  $0 cleanup"
}

# Função principal de deploy
deploy() {
    log "=== INICIANDO DEPLOYMENT AZURE (5 VMs) ==="
    
    check_azure_cli
    setup_ssh_key
    create_resource_group
    create_nsg
    create_vnet
    create_vms
    list_vm_info
    configure_vms
    create_inventory
    
    log "=== DEPLOYMENT CONCLUÍDO ==="
    echo
    echo -e "${BLUE}🎯 Arquitetura implantada:${NC}"
    echo -e "🏭 1 VM Broker (RabbitMQ)"
    echo -e "📤 1 VM Producer"
    echo -e "📥 3 VMs Consumers"
    echo
    echo -e "${GREEN}Próximos passos:${NC}"
    echo "1. Aguarde alguns minutos para a configuração das VMs terminar"
    echo "2. Acesse RabbitMQ Management UI: http://<IP_VM1>:15672"
    echo "3. Clone o repositório em cada VM de aplicação (VM2-VM5)"
    echo "4. Configure o arquivo .env com o IP do broker"
    echo "5. Execute os cenários de teste"
    echo
    echo -e "${GREEN}Arquivo de inventário gerado:${NC} azure-inventory.txt"
}

# Main
case "${1:-deploy}" in
    deploy)
        deploy
        ;;
    info)
        check_azure_cli
        list_vm_info
        ;;
    inventory)
        check_azure_cli
        create_inventory
        ;;
    cleanup)
        check_azure_cli
        cleanup
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        error "Comando inválido: $1. Use '$0 help' para ver comandos disponíveis."
        ;;
esac