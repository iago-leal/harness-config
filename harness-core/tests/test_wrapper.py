import subprocess
import os

def test_wrapper_help():
    # O wrapper está localizado na raiz do projeto (dois níveis acima de tests/)
    wrapper_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../harness"))
    
    # Se o wrapper ainda não existir no momento do pytest (por exemplo, na fase 2 TDD),
    # o teste deve falhar ou ser ignorado. Mas no fluxo do Reversa, criaremos logo em seguida.
    assert os.path.exists(wrapper_path), f"Wrapper {wrapper_path} não encontrado."

    result = subprocess.run(
        [wrapper_path, "--help"],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0
    assert "Harness Core CLI" in result.stdout

def test_wrapper_cmd_clarificar():
    wrapper_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../harness"))
    assert os.path.exists(wrapper_path)

    result = subprocess.run(
        [wrapper_path, "cmd", "clarificar"],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0
    assert "Clarificação de Requisitos" in result.stdout
