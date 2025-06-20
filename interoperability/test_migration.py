#!/usr/bin/env python3
"""
Test script para verificar a migração de Java para JavaScript
"""
import subprocess
import time
import sys
import os

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")

def test_javascript_consumer():
    """Testa se o consumer JavaScript funciona corretamente"""
    print_header("TESTE DO CONSUMER JAVASCRIPT")
    
    try:
        # Verifica se o arquivo existe
        js_consumer = "consumer3.js"
        if not os.path.exists(js_consumer):
            print(f"❌ Arquivo {js_consumer} não encontrado")
            return False
        
        print(f"✅ Arquivo {js_consumer} encontrado")
        
        # Verifica sintaxe básica
        result = subprocess.run([
            "node", "-c", js_consumer
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Sintaxe JavaScript válida")
        else:
            print(f"❌ Erro de sintaxe: {result.stderr}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def test_package_json():
    """Verifica se package.json está configurado corretamente"""
    print_header("TESTE DO PACKAGE.JSON")
    
    try:
        import json
        
        with open("package.json", "r") as f:
            package_data = json.load(f)
        
        # Verifica dependências necessárias
        deps = package_data.get("dependencies", {})
        
        if "amqplib" in deps:
            print("✅ Dependência amqplib encontrada")
        else:
            print("❌ Dependência amqplib não encontrada")
            return False
        
        print(f"📦 Versão amqplib: {deps['amqplib']}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar package.json: {e}")
        return False

def test_node_modules():
    """Verifica se node_modules está instalado"""
    print_header("TESTE DOS NODE_MODULES")
    
    if os.path.exists("node_modules"):
        print("✅ node_modules encontrado")
        
        # Verifica amqplib especificamente
        if os.path.exists("node_modules/amqplib"):
            print("✅ amqplib instalado corretamente")
            return True
        else:
            print("❌ amqplib não encontrado em node_modules")
            return False
    else:
        print("❌ node_modules não encontrado")
        print("💡 Execute: npm install")
        return False

def test_producer_updates():
    """Verifica se o producer foi atualizado para JavaScript"""
    print_header("TESTE DAS ATUALIZAÇÕES DO PRODUCER")
    
    try:
        with open("producer.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Verifica se mudanças foram feitas
        if "javascript_queue" in content:
            print("✅ Producer atualizado para javascript_queue")
        else:
            print("❌ Producer ainda referencia java_queue")
            return False
        
        if '"javascript"' in content:
            print("✅ Routing key 'javascript' encontrada")
        else:
            print("❌ Routing key 'javascript' não encontrada")
            return False
        
        if "🟡" in content:
            print("✅ Emoji JavaScript (🟡) encontrado")
        else:
            print("❌ Emoji JavaScript não encontrado")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar producer: {e}")
        return False

def test_readme_updates():
    """Verifica se o README foi atualizado"""
    print_header("TESTE DAS ATUALIZAÇÕES DO README")
    
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Verifica atualizações
        if "consumer3.js" in content:
            print("✅ README atualizado para consumer3.js")
        else:
            print("❌ README ainda referencia Consumer3.java")
            return False
        
        if "JavaScript" in content or "javascript" in content:
            print("✅ Referências ao JavaScript encontradas")
        else:
            print("❌ Referências ao JavaScript não encontradas")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar README: {e}")
        return False

def check_removed_files():
    """Verifica se arquivos Java foram removidos"""
    print_header("VERIFICAÇÃO DE ARQUIVOS REMOVIDOS")
    
    java_files = [
        "Consumer3.java",
        "pom.xml"
    ]
    
    all_removed = True
    
    for file in java_files:
        if os.path.exists(file):
            print(f"⚠️ Arquivo {file} ainda existe (deveria ter sido removido)")
            all_removed = False
        else:
            print(f"✅ Arquivo {file} removido corretamente")
    
    return all_removed

def main():
    print_header("TESTE DE MIGRAÇÃO JAVA → JAVASCRIPT")
    print("Verificando se a migração foi realizada corretamente...")
    
    # Lista de testes
    tests = [
        ("Node.js Dependencies", test_node_modules),
        ("Package.json", test_package_json),
        ("JavaScript Consumer", test_javascript_consumer),
        ("Producer Updates", test_producer_updates),
        ("README Updates", test_readme_updates),
        ("Removed Files", check_removed_files)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 Executando: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro no teste {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumo dos resultados
    print_header("RESUMO DOS TESTES")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 RESULTADO FINAL: {passed}/{total} testes passaram")
    
    if passed == total:
        print("\n🎉 MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("✅ Java consumer foi substituído por JavaScript consumer")
        print("✅ Todas as configurações foram atualizadas")
        print("✅ Documentação foi atualizada")
        print("\n💡 Próximos passos:")
        print("   1. Testar com RabbitMQ rodando")
        print("   2. Executar producer e consumers")
        print("   3. Verificar logs de funcionamento")
    else:
        print(f"\n⚠️ MIGRAÇÃO INCOMPLETA ({total-passed} problemas encontrados)")
        print("🔧 Verifique os itens que falharam acima")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
