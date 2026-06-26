import os
import re
from typing import List, Optional
from src.core.ports.fs import FileSystemPort
from src.core.ports.process import ProcessPort
from src.core.domain.layout import (
    CORE_REL_PATH,
    CORE_GITIGNORE_ENTRY,
    CORE_CONFIG_CANDIDATE_RELPATHS,
)
from src.core.install.local_apply import apply_local_materializers


class UpstreamVersionUndeterminedError(Exception):
    """Levantada quando a versão do core no upstream não pode ser lida.

    Ocorre, por exemplo, quando o upstream relocou o core para um caminho fora
    dos candidatos conhecidos (``CORE_CONFIG_CANDIDATE_RELPATHS``). Em vez de
    cair num fallback que igualaria a versão local — gerando um upgrade fantasma
    que imprime "Sucesso" sem copiar nada —, o ``upgrade`` aborta barulhento e
    instrui a reidratação completa via ``init`` (feature 012, RN-04).
    """

    def __init__(self, upstream_path: str):
        self.upstream_path = upstream_path
        super().__init__(
            "Não foi possível determinar a versão do Harness Core no upstream "
            f"'{upstream_path}' (config.py não encontrado nos caminhos-candidato). "
            "O layout do upstream pode ter mudado. Reidrate esta instalação com: "
            f"'{upstream_path}/harness init <caminho-absoluto-deste-projeto>'."
        )


class InitializationService:
    def __init__(self, fs: FileSystemPort, process: ProcessPort):
        self.fs = fs
        self.process = process
        self.current_version = "1.2.49"

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
            # Sobe 6 níveis a partir deste arquivo: init_service.py -> bootstrap -> core -> src -> harness-core -> .harness -> raiz
            upstream_path = os.path.dirname(
                os.path.dirname(
                    os.path.dirname(
                        os.path.dirname(
                            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                        )
                    )
                )
            )
        upstream_path = os.path.abspath(upstream_path)

        # 3. Copia a pasta harness-core recursivamente (ignora venv, caches, etc.)
        src_core = os.path.join(upstream_path, CORE_REL_PATH)
        dst_core = os.path.join(target_path, CORE_REL_PATH)

        # `.harness/` é estado de runtime por-instalação (sessão, microdecisões);
        # nunca deve viajar do upstream para o alvo no init/upgrade.
        excludes = [
            ".venv",
            ".pytest_cache",
            ".ruff_cache",
            "__pycache__",
            ".DS_Store",
            ".harness",
        ]
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

        # 9. Materializa os artefatos de IDE (slash commands sempre; hooks.json do
        # Antigravity quando aplicável) pela função única compartilhada com o
        # upgrade. No init a chamada é in-process: o código em execução já é o do
        # upstream (fresco), então não há risco de staleness (feature 012).
        apply_local_materializers(
            self.fs, target_path, os.path.abspath(target_path), active_harness
        )

        # 11. Registra a cópia vendored do core no .gitignore do alvo: ela é
        # regenerável via upgrade/init, então não deve poluir o histórico do
        # projeto-alvo. Só no alvo; o repo-fonte versiona o core (D-04).
        self._ensure_gitignore_entry(target_path, CORE_GITIGNORE_ENTRY)

    def upgrade_project(self, target_path: str, force: bool = False) -> None:
        """Atualiza a instalação do Harness Core no projeto de destino a partir do upstream configurado.

        Com ``force=True``, ignora a comparação de versão e tolera uma versão de
        upstream indeterminada (vira aviso), sempre recopiando e rematerializando.
        """
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

        # 1. Determina a versão do upstream. Sob --force, uma versão indeterminada
        # vira aviso (segue mesmo assim); sem --force, propaga o erro (abort
        # barulhento, RN-04) em vez de cair num fallback silencioso.
        upstream_version = None
        try:
            upstream_version = self._get_upstream_version(upstream_path)
        except UpstreamVersionUndeterminedError as exc:
            if not force:
                raise
            print(f"Aviso: {exc} Prosseguindo mesmo assim por causa de --force.")

        # 2. Sem --force, encerra cedo quando já está atualizado.
        if not force:
            local_version = self._parse_toml_field(toml_content, "version") or "0.0.0"
            if upstream_version == local_version:
                # Já está atualizado
                return

        # 2. Executa a cópia do core (ignora dados do usuário e venv)
        src_core = os.path.join(upstream_path, CORE_REL_PATH)
        dst_core = os.path.join(target_path, CORE_REL_PATH)

        # `.harness/` é estado de runtime por-instalação (sessão, microdecisões);
        # nunca deve viajar do upstream para o alvo no init/upgrade.
        excludes = [
            ".venv",
            ".pytest_cache",
            ".ruff_cache",
            "__pycache__",
            ".DS_Store",
            ".harness",
        ]
        self._copy_tree(src_core, dst_core, excludes)

        # 3. Atualiza wrapper harness
        src_wrapper = os.path.join(upstream_path, "harness")
        dst_wrapper = os.path.join(target_path, "harness")
        if self.fs.exists(src_wrapper):
            wrapper_content = self.fs.read_file(src_wrapper)
            self.fs.write_file(dst_wrapper, wrapper_content)
            self.process.run_command(["chmod", "+x", dst_wrapper])

        # 5. Atualiza a versão no harness.toml, quando determinada. Sob --force
        # com versão indeterminada, preserva o version existente (não grava None).
        if upstream_version is not None:
            toml_content = self._update_toml_field(
                toml_content, "version", upstream_version
            )
            self.fs.write_file(toml_path, toml_content)

        # 6. Roda bootstrap de ganchos Git e rematerializa os artefatos de IDE no
        # destino, ambos via subprocesso do python de destino — executam com o
        # CÓDIGO RECÉM-COPIADO, não com os módulos antigos carregados em memória
        # (Modo 1 stale, RN-01/RN-02). O bootstrap já seguia este molde; a
        # materialização passa a segui-lo também (feature 012).
        dest_python_bin = os.path.join(dst_core, ".venv", "bin", "python3")
        dest_main_cli = os.path.join(dst_core, "src", "main.py")
        if not self.fs.exists(dest_python_bin) or not self.fs.exists(dest_main_cli):
            raise ValueError(
                f"O core de destino em '{dst_core}' está incompleto após a cópia "
                "(falta a venv ou o main.py). Reidrate a instalação com: "
                f"'{upstream_path}/harness init <caminho-absoluto-deste-projeto>'."
            )
        self.process.run_command(
            [dest_python_bin, dest_main_cli, "bootstrap"], cwd=target_path
        )
        self.process.run_command(
            [dest_python_bin, dest_main_cli, "materialize"], cwd=target_path
        )

        # 7. Garante (idempotente) a entrada do core no .gitignore do alvo — útil
        # também na migração de instalações antigas para o novo layout (D-04).
        self._ensure_gitignore_entry(target_path, CORE_GITIGNORE_ENTRY)

    def _ensure_gitignore_entry(self, target_path: str, entry: str) -> None:
        """Garante, de forma idempotente, que `entry` consta no .gitignore do alvo.

        Lê o .gitignore existente (vazio se ausente), acrescenta a linha apenas
        se ela ainda não estiver presente e grava de forma atômica. Toda escrita
        ocorre sob `target_path` — footprint global zero preservado (RN-N17).
        """
        gitignore_path = os.path.join(target_path, ".gitignore")
        content = (
            self.fs.read_file(gitignore_path) if self.fs.exists(gitignore_path) else ""
        )
        if entry in [line.strip() for line in content.splitlines()]:
            return
        new_content = content
        if new_content and not new_content.endswith("\n"):
            new_content += "\n"
        new_content += entry + "\n"
        self.fs.write_file_atomic(gitignore_path, new_content)

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
        """Lê a versão do config.py do upstream, resiliente ao layout.

        Varre os caminhos-candidato (canônico + legado da raiz) e devolve a
        primeira versão encontrada. Quando nenhum candidato existe ou nenhum
        expõe a versão, levanta ``UpstreamVersionUndeterminedError`` em vez de
        cair num fallback silencioso — caso contrário um relayout do upstream
        faria a versão "indeterminada" coincidir com a local e o upgrade viraria
        um no-op silencioso (feature 012, RN-03/RN-04).
        """
        for rel in CORE_CONFIG_CANDIDATE_RELPATHS:
            config_path = os.path.join(upstream_path, rel)
            if not self.fs.exists(config_path):
                continue
            content = self.fs.read_file(config_path)
            match = re.search(r'version:\s*str\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                return match.group(1)
        raise UpstreamVersionUndeterminedError(upstream_path)

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
