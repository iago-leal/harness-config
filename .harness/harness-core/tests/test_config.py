"""Configuração tipada — seção [regen] (feature 016)."""

from src.core.domain.config import load_config, HarnessConfig, RegenSection
from tests.helpers import MockFileSystem


def test_regen_section_default_is_none():
    # Sem harness.toml, defaults: regen.command é None (no-op).
    cfg = HarnessConfig()
    assert isinstance(cfg.regen, RegenSection)
    assert cfg.regen.command is None


def test_load_config_parses_regen_command():
    fs = MockFileSystem()
    fs.write_file(
        "harness.toml",
        '[harness]\nactive_harness = "claude"\n\n'
        '[regen]\ncommand = "python gerar_site.py && python empacotar.py"\n',
    )
    cfg = load_config(fs, "harness.toml")
    assert cfg.regen.command == "python gerar_site.py && python empacotar.py"


def test_load_config_absent_regen_is_none():
    fs = MockFileSystem()
    fs.write_file("harness.toml", '[harness]\nactive_harness = "claude"\n')
    cfg = load_config(fs, "harness.toml")
    assert cfg.regen.command is None


def test_load_config_tolerates_toml_without_version():
    # Feature 020: o init deixa de gravar `version`; um harness.toml sem esse
    # campo deve carregar normalmente (default), sem quebrar o parse.
    fs = MockFileSystem()
    fs.write_file(
        "harness.toml",
        '[harness]\nactive_harness = "claude"\nupstream_path = "/abs/up"\n',
    )
    cfg = load_config(fs, "harness.toml")
    assert cfg.harness.upstream_path == "/abs/up"
    assert isinstance(cfg.harness.version, str)  # default aplicado, sem erro


def test_load_config_tolerates_toml_with_version():
    # Compat retroativa: um harness.toml herdado (com `version`) segue parseável.
    fs = MockFileSystem()
    fs.write_file(
        "harness.toml",
        '[harness]\nactive_harness = "claude"\n'
        'upstream_path = "/abs/up"\nversion = "1.2.56"\n',
    )
    cfg = load_config(fs, "harness.toml")
    assert cfg.harness.version == "1.2.56"
    assert cfg.harness.upstream_path == "/abs/up"


def test_session_inject_decisions_index_default_true():
    # Feature 021: sem harness.toml, o flag nasce True (habilitado por padrão).
    cfg = HarnessConfig()
    assert cfg.session.inject_decisions_index is True


def test_load_config_parses_inject_decisions_index_false():
    # [session].inject_decisions_index = false → desliga o anexo de decisões.
    fs = MockFileSystem()
    fs.write_file(
        "harness.toml",
        '[harness]\nactive_harness = "claude"\n\n'
        "[session]\ninject_decisions_index = false\n",
    )
    cfg = load_config(fs, "harness.toml")
    assert cfg.session.inject_decisions_index is False


def test_load_config_absent_session_flag_defaults_true():
    # Retrocompatível: [session] ausente inteiro → default True.
    fs = MockFileSystem()
    fs.write_file("harness.toml", '[harness]\nactive_harness = "claude"\n')
    cfg = load_config(fs, "harness.toml")
    assert cfg.session.inject_decisions_index is True
