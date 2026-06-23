import argparse
import json
import pytest
from tests.helpers import MockFileSystem
from src.core.documentation.service import DocumentationService
from src.main import build_parser

def test_extract_commands():
    parser = argparse.ArgumentParser(description="Test Parser")
    subparsers = parser.add_subparsers(dest="command")
    
    sub = subparsers.add_parser("testcmd", description="Help do comando de teste")
    sub.add_argument("--foo", help="Help do argumento foo", default="bar")
    
    fs = MockFileSystem()
    service = DocumentationService(fs)
    commands = service.extract_commands(parser)
    
    assert len(commands) == 1
    assert commands[0]["name"] == "testcmd"
    assert commands[0]["help"] == "Help do comando de teste"
    assert len(commands[0]["arguments"]) == 1
    assert "--foo" in commands[0]["arguments"][0]["flags"]
    assert commands[0]["arguments"][0]["default"] == "bar"

def test_parse_markdown_rules():
    domain_content = """
# Regras
**RN-01: Regra Unitária** Detalhes da regra 01 🟢
**RN-02: Outra Regra** Alguma outra regra 🟡
    """
    fs = MockFileSystem(existing_files={"domain.md"})
    fs.write_file("domain.md", domain_content)
    
    service = DocumentationService(fs)
    rules = service.parse_markdown_rules("domain.md")
    
    assert len(rules) == 2
    assert rules[0]["id"] == "RN-01"
    assert rules[0]["title"] == "Regra Unitária"
    assert rules[0]["details"] == "Detalhes da regra 01"
    assert rules[0]["confidence"] == "🟢"

def test_load_checkpoints():
    state_content = '{"completed": ["scout", "architect"], "checkpoints": {}}'
    fs = MockFileSystem(existing_files={"state.json"})
    fs.write_file("state.json", state_content)
    
    service = DocumentationService(fs)
    state = service.load_checkpoints("state.json")
    
    assert "completed" in state
    assert state["completed"] == ["scout", "architect"]

def test_generate_html():
    parser = argparse.ArgumentParser()
    fs = MockFileSystem(existing_files={"template.html", "domain.md", "state.json"})
    fs.write_file("template.html", "<html>/* INJECTED_DATA_PLACEHOLDER */</html>")
    fs.write_file("domain.md", "**RN-01: Teste** Detalhe 🟢")
    fs.write_file("state.json", '{"completed": []}')
    
    service = DocumentationService(fs)
    service.generate_html(
        parser=parser,
        template_path="template.html",
        domain_path="domain.md",
        state_path="state.json",
        output_path="harness-docs.html"
    )
    
    assert fs.exists("harness-docs.html")
    generated_content = fs.read_file("harness-docs.html")
    assert 'const HARNESS_DOC_DATA =' in generated_content
    assert '"commands"' in generated_content

def test_parser_integration():
    """Valida se o parser global do main.py registra os subcomandos doc-gen e doc-serve."""
    parser = build_parser()
    
    # Testa parsing de 'doc-gen'
    parsed_gen = parser.parse_args(["doc-gen"])
    assert parsed_gen.command == "doc-gen"
    
    # Testa parsing de 'doc-serve'
    parsed_serve = parser.parse_args(["doc-serve", "--port", "9000"])
    assert parsed_serve.command == "doc-serve"
    assert parsed_serve.port == 9000
