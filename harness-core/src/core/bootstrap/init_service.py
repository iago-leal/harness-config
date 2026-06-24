import os
import re
from typing import List, Optional
from src.core.ports.fs import FileSystemPort
from src.core.ports.process import ProcessPort
from src.core.install.antigravity_hooks import materialize_hooks_json
from src.core.install.session_commands import materialize_session_commands


class InitializationService:
    def __init__(self, fs: FileSystemPort, process: ProcessPort):
        self.fs = fs
        self.process = process
        self.current_version = "1.2.43"

    def initialize_project(
        self,
        target_path: str,
        active_harness: str = "claude",
        upstream_path: Optional[str] = None,
    ) -> None:
        """Inicializa um novo repositório de destino com o Harness Core de forma física e isolada."""
        # 1. Valida se o destino é um repositório git válido
        git_dir = os.path.join(target_path, ".git")
        if not self.fs.exists(git_dir):
            raise ValueError(
                f"O diretório de destino '{target_path}' não é um repositório git válido (falta a subpasta .git)."
            )

        # 2. Resolve o upstream original
        if not upstream_path:
            # Sobe 5 níveis a partir deste arquivo: init_service.py -> bootstrap -> core -> src -> harness-core -> raiz
            upstream_path = os.path.dirname(
                os.path.dirname(
                    os.path.dirname(
                        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    )
                )
            )
        upstream_path = os.path.abspath(upstream_path)

        # 3. Copia a pasta harness-core recursivamente (ignora venv, caches, etc.)
        src_core = os.path.join(upstream_path, "harness-core")
        dst_core = os.path.join(target_path, "harness-core")

        excludes = [".venv", ".pytest_cache", ".ruff_cache", "__pycache__", ".DS_Store"]
        self._copy_tree(src_core, dst_core, excludes)

        # 4. Copia o wrapper harness
        src_wrapper = os.path.join(upstream_path, "harness")
        dst_wrapper = os.path.join(target_path, "harness")
        if self.fs.exists(src_wrapper):
            wrapper_content = self.fs.read_file(src_wrapper)
            self.fs.write_file(dst_wrapper, wrapper_content)
            # Garante permissão de execução
            self.process.run_command(["chmod", "+x", dst_wrapper])

        # 5. Inicializa pasta .harness e arquivos padrão
        dot_harness = os.path.join(target_path, ".harness")
        decisions_dir = os.path.join(dot_harness, "decisoes")
        self.fs.makedirs(decisions_dir)

        cabecalho_path = os.path.join(decisions_dir, "_cabecalho.md")
        if not self.fs.exists(cabecalho_path):
            self.fs.write_file(cabecalho_path, "# Microdecisões do Projeto\n")

        index_path = os.path.join(dot_harness, "microdecisoes.md")
        if not self.fs.exists(index_path):
            self.fs.write_file(
                index_path,
                "# Índice de Microdecisões\n\n> Gerado automaticamente. Não edite este arquivo diretamente.\n",
            )

        sessao_path = os.path.join(dot_harness, "estado-da-sessao.md")
        if not self.fs.exists(sessao_path):
            self.fs.write_file(
                sessao_path,
                "---\ncommit: null\nfeature: null\nstart_time: null\nstatus: null\n---\n# Estado de Sessão\n",
            )

        # 6. Grava ou atualiza harness.toml
        toml_path = os.path.join(target_path, "harness.toml")
        if self.fs.exists(toml_path):
            toml_content = self.fs.read_file(toml_path)
            # Atualiza versão e upstream_path
            toml_content = self._update_toml_field(
                toml_content, "upstream_path", upstream_path
            )
            toml_content = self._update_toml_field(
                toml_content, "version", self.current_version
            )
            toml_content = self._update_toml_field(
                toml_content, "active_harness", active_harness
            )
            self.fs.write_file(toml_path, toml_content)
        else:
            self.fs.write_file(
                toml_path,
                f'[harness]\nactive_harness = "{active_harness}"\nupstream_path = "{upstream_path}"\nversion = "{self.current_version}"\n\n[session]\nstate_file = ".harness/estado-da-sessao.md"\n\n[decisions]\ndir = ".harness/decisoes"\nindex_file = ".harness/microdecisoes.md"\nheader_file = ".harness/decisoes/_cabecalho.md"\n',
            )

        # 7. Configura a venv e roda pip install no destino
        self.process.run_command(["python3", "-m", "venv", ".venv"], cwd=dst_core)
        self.process.run_command(
            [".venv/bin/pip", "install", "-r", "requirements.txt"], cwd=dst_core
        )

        # 8. Executa bootstrap de hooks git no destino
        dest_python_bin = os.path.join(dst_core, ".venv", "bin", "python3")
        dest_main_cli = os.path.join(dst_core, "src", "main.py")
        if self.fs.exists(dest_main_cli):
            # Executa bootstrap para criar ganchos git pre-commit e post-merge
            self.process.run_command(
                [dest_python_bin, dest_main_cli, "bootstrap"], cwd=target_path
            )

        # 9. Materializa o .agents/hooks.json quando o harness ativo é o Antigravity.
        # O command_path é o caminho absoluto do projeto-alvo (prefixo de `<ABS>/harness ...`).
        if active_harness == "antigravity":
            command_path = os.path.abspath(target_path)
            materialize_hooks_json(self.fs, target_path, command_path)

        # 10. Materializa os slash commands de sessão de IDE (Claude + Antigravity),
        # SEMPRE — independentemente do active_harness (feature 010, D-03).
        materialize_session_commands(self.fs, target_path, os.path.abspath(target_path))

    def upgrade_project(self, target_path: str) -> None:
        """Atualiza a instalação do Harness Core no projeto de destino a partir do upstream configurado."""
        toml_path = os.path.join(target_path, "harness.toml")
        if not self.fs.exists(toml_path):
            raise ValueError(
                f"O projeto em '{target_path}' não possui um arquivo harness.toml configurado."
            )

        toml_content = self.fs.read_file(toml_path)
        upstream_path = self._parse_toml_field(toml_content, "upstream_path")
        if not upstream_path:
            raise ValueError(
                "O campo 'upstream_path' não foi encontrado no harness.toml do projeto de destino."
            )

        upstream_path = os.path.abspath(upstream_path)
        if not self.fs.exists(upstream_path):
            raise ValueError(
                f"O caminho upstream '{upstream_path}' não está acessível no host local."
            )

        # 1. Compara versões
        upstream_version = self._get_upstream_version(upstream_path)
        local_version = self._parse_toml_field(toml_content, "version") or "0.0.0"

        if upstream_version == local_version:
            # Já está atualizado
            return

        # 2. Executa a cópia do core (ignora dados do usuário e venv)
        src_core = os.path.join(upstream_path, "harness-core")
        dst_core = os.path.join(target_path, "harness-core")

        excludes = [".venv", ".pytest_cache", ".ruff_cache", "__pycache__", ".DS_Store"]
        self._copy_tree(src_core, dst_core, excludes)

        # 3. Atualiza wrapper harness
        src_wrapper = os.path.join(upstream_path, "harness")
        dst_wrapper = os.path.join(target_path, "harness")
        if self.fs.exists(src_wrapper):
            wrapper_content = self.fs.read_file(src_wrapper)
            self.fs.write_file(dst_wrapper, wrapper_content)
            self.process.run_command(["chmod", "+x", dst_wrapper])

        # 4. Atualiza a versão no harness.toml
        toml_content = self._update_toml_field(
            toml_content, "version", upstream_version
        )
        self.fs.write_file(toml_path, toml_content)

        # 5. Roda bootstrap de ganchos git no destino
        dest_python_bin = os.path.join(dst_core, ".venv", "bin", "python3")
        dest_main_cli = os.path.join(dst_core, "src", "main.py")
        if self.fs.exists(dest_main_cli):
            self.process.run_command(
                [dest_python_bin, dest_main_cli, "bootstrap"], cwd=target_path
            )

        # 6. Reescreve o .agents/hooks.json quando o harness ativo é o Antigravity
        # (mantém o `command` com o caminho absoluto correto se o repo foi movido).
        active_harness = self._parse_toml_field(toml_content, "active_harness")
        if active_harness == "antigravity":
            command_path = os.path.abspath(target_path)
            materialize_hooks_json(self.fs, target_path, command_path)

        # 7. (Re)materializa os slash commands de sessão de IDE, sempre — mantém o
        # caminho absoluto do wrapper correto se o repositório foi movido (D-03).
        materialize_session_commands(self.fs, target_path, os.path.abspath(target_path))

    def _copy_tree(self, src: str, dst: str, excludes: List[str]) -> None:
        """Copia a árvore de diretórios e arquivos recursivamente usando FileSystemPort."""
        self.fs.makedirs(dst)
        for item in self.fs.list_dir(src):
            if item in excludes:
                continue
            src_item = os.path.join(src, item)
            dst_item = os.path.join(dst, item)

            if self.fs.is_dir(src_item):
                self._copy_tree(src_item, dst_item, excludes)
            else:
                content = self.fs.read_file(src_item)
                self.fs.write_file(dst_item, content)

    def _get_upstream_version(self, upstream_path: str) -> str:
        """Lê a versão do config.py do upstream."""
        config_path = os.path.join(
            upstream_path, "harness-core", "src", "core", "domain", "config.py"
        )
        if not self.fs.exists(config_path):
            return self.current_version

        content = self.fs.read_file(config_path)
        match = re.search(r'version:\s*str\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            return match.group(1)
        return self.current_version

    @staticmethod
    def _parse_toml_field(toml_content: str, field_name: str) -> Optional[str]:
        """Faz o parsing simples de um campo no toml."""
        match = re.search(rf'{field_name}\s*=\s*["\']([^"\']+)["\']', toml_content)
        if match:
            return match.group(1)
        return None

    @staticmethod
    def _update_toml_field(toml_content: str, field_name: str, new_value: str) -> str:
        """Atualiza ou insere um campo no toml."""
        pattern = rf'({field_name}\s*=\s*["\'])([^"\']+)(["\'])'
        if re.search(pattern, toml_content):
            return re.sub(pattern, rf"\g<1>{new_value}\g<3>", toml_content)
        # Se for na seção [harness], tenta inserir logo após ela
        if "[harness]" in toml_content:
            return toml_content.replace(
                "[harness]", f'[harness]\n{field_name} = "{new_value}"'
            )
        return toml_content + f'\n{field_name} = "{new_value}"\n'
