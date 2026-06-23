import sys
import os

# Adiciona o caminho do harness-core para podermos importar
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.decisions.importer import LegacyDecisionImporter

def test_migration():
    source_dir = "/Users/iagoleal/dev/harness/harness-config/decisoes"
    target_dir = "/Users/iagoleal/dev/harness/harness-core/decisoes_test"
    
    print(f"Executando migração de teste de: {source_dir}")
    print(f"Para pasta temporária: {target_dir}")
    
    try:
        count = LegacyDecisionImporter.import_directory(source_dir, target_dir)
        print(f"Sucesso! Importados {count} arquivos de microdecisões.")
        
        # Validação de contagem
        assert count == 17, f"Esperava 17 arquivos, importou {count}"
        
        # Validar um dos arquivos importados
        test_file = os.path.join(target_dir, "MD-0001.md")
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        print("Conteúdo do MD-0001.md importado:")
        print("-" * 40)
        print("\n".join(content.splitlines()[:15]))
        print("-" * 40)
        
        # Limpar diretório de teste
        for f in os.listdir(target_dir):
            os.remove(os.path.join(target_dir, f))
        os.rmdir(target_dir)
        print("Limpeza do diretório de teste concluída.")
        
    except Exception as e:
        print(f"Erro na migração: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_migration()
