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
VM_COUNT=3
PROJECT_NAME="rabbitmq-facul"

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

# Cria network security group
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
    
    # SSH
    az network nsg rule create \
        --resource-group "$RESOURCE_GROUP" \
        --nsg-name "$nsg_name" \
        --name "AllowSSH" \
        --protocol tcp \
        --priority 1000 \
        --destination-port-range 22 \
        --access allow \
        --output table
    
    # RabbitMQ AMQP
    az network nsg rule create \
        --resource-group "$RESOURCE_GROUP" \
        --nsg-name "$nsg_name" \
        --name "AllowRabbitMQ" \
        --protocol tcp \
        --priority 1001 \
        --destination-port-range 5672 \
        --access allow \
        --output table
    
    # RabbitMQ Management
    az network nsg rule create \
        --resource-group "$RESOURCE_GROUP" \
        --nsg-name "$nsg_name" \
        --name "AllowRabbitMQMgmt" \
        --protocol tcp \
        --priority 1002 \
        --destination-port-range 15672 \
        --access allow \
        --output table
    
    # HTTP/HTTPS
    az network nsg rule create \
        --resource-group "$RESOURCE_GROUP" \
        --nsg-name "$nsg_name" \
        --name "AllowHTTP" \
        --protocol tcp \
        --priority 1003 \
        --destination-port-range 80 \
        --access allow \
        --output table
    
    az network nsg rule create \
        --resource-group "$RESOURCE_GROUP" \
        --nsg-name "$nsg_name" \
        --name "AllowHTTPS" \
        --protocol tcp \
        --priority 1004 \
        --destination-port-range 443 \
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

# Gera chave SSH
generate_ssh_key() {
    local key_path="$HOME/.ssh/${PROJECT_NAME}-key"
    
    if [ ! -f "$key_path" ]; then
        log "Gerando chave SSH..."
        ssh-keygen -t rsa -b 4096 -f "$key_path" -N "" -C "${PROJECT_NAME}@azure"
        log "Chave SSH gerada: $key_path"
    else
        log "Chave SSH já existe: $key_path"
    fi
    
    echo "$key_path"
}

# Cria VMs
create_vms() {
    local ssh_key_path=$(generate_ssh_key)
    local vnet_name="${PROJECT_NAME}-vnet"
    local subnet_name="${PROJECT_NAME}-subnet"
    
    log "Criando $VM_COUNT VMs..."
    
    for i in $(seq 1 $VM_COUNT); do
        local vm_name="${PROJECT_NAME}-vm${i}"
        local pip_name="${vm_name}-pip"
        
        log "Criando VM $i de $VM_COUNT: $vm_name"
        
        # Cria IP público
        az network public-ip create \
            --resource-group "$RESOURCE_GROUP" \
            --name "$pip_name" \
            --allocation-method Dynamic \
            --location "$LOCATION" \
            --output table
        
        # Cria VM
        az vm create \
            --resource-group "$RESOURCE_GROUP" \
            --name "$vm_name" \
            --image "Ubuntu2204" \
            --size "$VM_SIZE" \
            --admin-username "$ADMIN_USERNAME" \
            --ssh-key-values "${ssh_key_path}.pub" \
            --public-ip-address "$pip_name" \
            --vnet-name "$vnet_name" \
            --subnet "$subnet_name" \
            --nsg "${PROJECT_NAME}-nsg" \
            --location "$LOCATION" \
            --tags role="rabbitmq-node" project="$PROJECT_NAME" \
            --output table
        
        log "VM $vm_name criada"
    done
    
    log "Todas as VMs foram criadas"
}

# Lista informações das VMs
list_vm_info() {
    log "Coletando informações das VMs..."
    
    echo -e "\n${BLUE}=== INFORMAÇÕES DAS VMs ===${NC}"
    
    for i in $(seq 1 $VM_COUNT); do
        local vm_name="${PROJECT_NAME}-vm${i}"
        local pip_name="${vm_name}-pip"
        
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
        
        echo -e "${GREEN}VM $i - $vm_name:${NC}"
        echo -e "  IP Público:  $public_ip"
        echo -e "  IP Privado:  $private_ip"
        echo -e "  SSH:         ssh -i ~/.ssh/${PROJECT_NAME}-key ${ADMIN_USERNAME}@${public_ip}"
        echo -e "  RabbitMQ UI: http://${public_ip}:15672"
        echo
    done
}

# Configura VMs remotamente
configure_vms() {
    local ssh_key_path="$HOME/.ssh/${PROJECT_NAME}-key"
    
    log "Configurando VMs remotamente..."
    
    for i in $(seq 1 $VM_COUNT); do
        local vm_name="${PROJECT_NAME}-vm${i}"
        local pip_name="${vm_name}-pip"
        
        # Pega IP público
        local public_ip=$(az network public-ip show \
            --resource-group "$RESOURCE_GROUP" \
            --name "$pip_name" \
            --query "ipAddress" \
            --output tsv)
        
        if [ -n "$public_ip" ] && [ "$public_ip" != "null" ]; then
            log "Configurando VM $vm_name ($public_ip)..."
            
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
            
            # Executa setup
            ssh -i "$ssh_key_path" -o StrictHostKeyChecking=no \
                "$ADMIN_USERNAME@$public_ip" \
                "sudo chmod +x /tmp/azure-setup.sh && sudo /tmp/azure-setup.sh"
            
            log "VM $vm_name configurada"
        else
            warn "Não foi possível obter IP público para VM $vm_name"
        fi
    done
    
    log "Configuração das VMs concluída"
}

# Cria arquivo de inventário
create_inventory() {
    local inventory_file="azure-inventory.txt"
    
    log "Criando arquivo de inventário..."
    
    cat > "$inventory_file" << EOF
# Inventário de VMs Azure - Projeto RabbitMQ Faculdade
# Gerado em: $(date)

Resource Group: $RESOURCE_GROUP
Location: $LOCATION
Project: $PROJECT_NAME
SSH Key: ~/.ssh/${PROJECT_NAME}-key

VMs:
EOF
    
    for i in $(seq 1 $VM_COUNT); do
        local vm_name="${PROJECT_NAME}-vm${i}"
        local pip_name="${vm_name}-pip"
        
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
        
        cat >> "$inventory_file" << EOF

VM $i - $vm_name:
  IP Público:  $public_ip
  IP Privado:  $private_ip
  SSH:         ssh -i ~/.ssh/${PROJECT_NAME}-key ${ADMIN_USERNAME}@${public_ip}
  RabbitMQ UI: http://${public_ip}:15672
  RabbitMQ:    amqp://admin:admin123@${public_ip}:5672
EOF
    done
    
    cat >> "$inventory_file" << EOF

Comandos úteis:
  # Conectar via SSH
  ssh -i ~/.ssh/${PROJECT_NAME}-key ${ADMIN_USERNAME}@<IP_PUBLICO>
  
  # Verificar status RabbitMQ
  docker ps | grep rabbitmq
  
  # Ver logs RabbitMQ
  docker logs rabbitmq-server
  
  # Executar cenários
  cd /home/rabbitmq-app
  sudo su - rabbitmq-app
  # Clone do repositório e execução dos cenários

EOF
    
    log "Arquivo de inventário criado: $inventory_file"
}

# Cleanup - remove recursos
cleanup() {
    warn "Esta operação irá remover TODOS os recursos do projeto!"
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
    echo "Script de deployment para Azure VMs - Projeto RabbitMQ"
    echo
    echo "Uso: $0 [COMANDO]"
    echo
    echo "Comandos:"
    echo "  deploy     - Cria toda a infraestrutura (padrão)"
    echo "  info       - Lista informações das VMs existentes"
    echo "  inventory  - Cria arquivo de inventário"
    echo "  cleanup    - Remove todos os recursos"
    echo "  help       - Mostra esta ajuda"
    echo
    echo "Variáveis de ambiente (opcionais):"
    echo "  RESOURCE_GROUP  - Nome do resource group (padrão: $RESOURCE_GROUP)"
    echo "  LOCATION        - Região Azure (padrão: $LOCATION)"
    echo "  VM_SIZE         - Tamanho das VMs (padrão: $VM_SIZE)"
    echo "  VM_COUNT        - Número de VMs (padrão: $VM_COUNT)"
    echo
    echo "Exemplo:"
    echo "  VM_COUNT=5 LOCATION=eastus $0 deploy"
}

# Função principal de deploy
deploy() {
    log "=== INICIANDO DEPLOYMENT AZURE ==="
    
    check_azure_cli
    create_resource_group
    create_nsg
    create_vnet
    create_vms
    list_vm_info
    configure_vms
    create_inventory
    
    log "=== DEPLOYMENT CONCLUÍDO ==="
    echo
    echo -e "${BLUE}Próximos passos:${NC}"
    echo "1. Aguarde alguns minutos para a configuração das VMs terminar"
    echo "2. Conecte-se às VMs usando as informações exibidas acima"
    echo "3. Faça login como usuário 'rabbitmq-app': sudo su - rabbitmq-app"
    echo "4. Clone o repositório do projeto"
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
