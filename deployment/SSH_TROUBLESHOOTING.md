# Guia de Resolução de Problemas SSH no Windows

## Problema: "Arquivo de chave pública SSH não encontrado"

Este erro é comum ao usar Azure CLI em ambientes Windows com Git Bash/WSL/MinGW. 

### Soluções Implementadas no Script

1. **Conversão automática de paths**: O script agora converte automaticamente paths Unix para Windows
2. **Regeneração forçada**: Use `--regen-ssh` para forçar uma nova chave
3. **Métodos de backup**: Múltiplos métodos de geração SSH caso o padrão falhe
4. **Validação aprimorada**: Verifica formato e existência da chave antes de usar

### Como Usar

```bash
# Executar com regeneração forçada da chave SSH
./azure-deploy.sh --regen-ssh

# Testar geração de chave SSH antes do deploy
./test-ssh-key.sh
```

### Solução Manual se o Script Falhar

Se ainda assim houver problemas, gere a chave manualmente:

#### No Git Bash:
```bash
# Criar diretório SSH
mkdir -p ~/.ssh

# Gerar chave SSH
ssh-keygen -t rsa -b 4096 -f ~/.ssh/rabbitmq-facul-key -N "" -C "rabbitmq-facul@azure" -m PEM

# Verificar arquivos criados
ls -la ~/.ssh/rabbitmq-facul-key*

# Verificar formato
ssh-keygen -l -f ~/.ssh/rabbitmq-facul-key.pub
```

#### No PowerShell:
```powershell
# Navegar para diretório SSH
cd $env:USERPROFILE\.ssh

# Gerar chave SSH
ssh-keygen -t rsa -b 4096 -f rabbitmq-facul-key -N '""' -C "rabbitmq-facul@azure" -m PEM

# Verificar arquivos
dir rabbitmq-facul-key*
```

### Paths de Chave SSH por Ambiente

- **Git Bash**: `~/.ssh/rabbitmq-facul-key.pub`
- **WSL**: `~/.ssh/rabbitmq-facul-key.pub`  
- **PowerShell**: `$env:USERPROFILE\.ssh\rabbitmq-facul-key.pub`
- **Cmd**: `%USERPROFILE%\.ssh\rabbitmq-facul-key.pub`

### Verificações Importantes

1. **Arquivo existe**:
   ```bash
   [ -f ~/.ssh/rabbitmq-facul-key.pub ] && echo "Existe" || echo "Não existe"
   ```

2. **Formato válido**:
   ```bash
   ssh-keygen -l -f ~/.ssh/rabbitmq-facul-key.pub
   ```

3. **Conteúdo da chave**:
   ```bash
   head -c 50 ~/.ssh/rabbitmq-facul-key.pub
   ```

### Problemas Comuns e Soluções

#### 1. Erro "Incorrect padding"
- **Causa**: Formato de chave incompatível
- **Solução**: Use `-m PEM` ao gerar a chave

#### 2. Erro "Permission denied"
- **Causa**: Permissões incorretas
- **Solução**: 
  ```bash
  chmod 600 ~/.ssh/rabbitmq-facul-key
  chmod 644 ~/.ssh/rabbitmq-facul-key.pub
  ```

#### 3. Path não encontrado no Azure CLI
- **Causa**: Diferença entre paths Unix e Windows
- **Solução**: O script agora converte automaticamente

#### 4. Chave corrompida
- **Causa**: Interrupção durante geração
- **Solução**: Delete e regenere:
  ```bash
  rm ~/.ssh/rabbitmq-facul-key*
  ./azure-deploy.sh --regen-ssh
  ```

### Teste Antes do Deploy

Execute sempre o teste antes do deploy principal:

```bash
# Testar ambiente e geração SSH
./test-ssh-key.sh

# Se teste passou, executar deploy
./azure-deploy.sh
```

### Suporte a Diferentes Ambientes Windows

O script foi testado e funciona em:
- ✅ Git Bash (recomendado)
- ✅ WSL (Windows Subsystem for Linux)
- ✅ MinGW/MSYS2
- ⚠️ PowerShell (pode precisar de ajustes de path)
- ⚠️ Command Prompt (limitações de comandos Unix)

### Em Caso de Falha Total

Se nada funcionar, use a abordagem manual completa:

1. Gere a chave manualmente no ambiente que preferir
2. Edite o script para usar o path absoluto da sua chave
3. Execute o deploy

Exemplo de edição manual no script:
```bash
# Substitua a linha que define ssh_key_path por:
ssh_key_path="/c/Users/SEU_USUARIO/.ssh/rabbitmq-facul-key"
```
