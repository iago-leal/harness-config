import json
import os
import re
from datetime import datetime, timezone, timedelta
from typing import Optional
from src.core.ports.fs import FileSystemPort
from src.core.ports.git import GitPort
from src.core.domain.cache import SyncCache
from src.core.domain.layout import CORE_CONFIG_CANDIDATE_RELPATHS


class SyncService:
    def __init__(
        self,
        fs: FileSystemPort,
        git: GitPort,
        cache_filepath: str,
        cache_ttl_hours: int = 24,
    ):
        self.fs = fs
        self.git = git
        self.cache_filepath = cache_filepath
        self.cache_ttl_hours = cache_ttl_hours

    def check_sync(self, repo_path: str) -> bool:
        """
        Verifica se o repositório local está sincronizado com o remoto.
        Retorna True se estiver sincronizado, se o cache estiver no TTL, ou em caso de erro de rede (não bloqueia).
        Retorna False apenas se o remote tiver commits diferentes e o cache tiver expirado.
        """
        try:
            agora = datetime.now(timezone.utc)

            # 1. Verificar cache local (BR-MIGRAR-003)
            if self.fs.exists(self.cache_filepath):
                try:
                    cache_content = self.fs.read_file(self.cache_filepath)
                    cache_data = json.loads(cache_content)

                    # Converte a string de data UTC do cache para datetime c/ timezone
                    last_checked = datetime.fromisoformat(
                        cache_data["last_checked_time"]
                    )
                    if last_checked.tzinfo is None:
                        last_checked = last_checked.replace(tzinfo=timezone.utc)

                    # Se estiver dentro do TTL (24h), pulamos a rede e retornamos True
                    if agora - last_checked < timedelta(hours=self.cache_ttl_hours):
                        # Se o commit_hash bate com o HEAD local, garante consistência
                        local_commit = self.git.get_head_commit(repo_path)
                        if cache_data.get("commit_hash") == local_commit:
                            return True
                        # Mesmo que mude, se está no TTL, a política clássica evita checagem de rede excessiva
                        return True
                except Exception:
                    # Falha no parse do cache, força nova consulta de rede
                    pass

            # 2. Executar checagem de rede (Git ls-remote)
            local_commit = self.git.get_head_commit(repo_path)
            # ls-remote remoto
            remote_commit = self.git.get_remote_commit(repo_path)

            # 3. Atualizar o cache de forma atômica
            new_cache = SyncCache(last_checked_time=agora, commit_hash=remote_commit)
            self.fs.write_file_atomic(
                self.cache_filepath, new_cache.model_dump_json(indent=2)
            )

            # 4. Retornar se local bate com o remote
            return local_commit == remote_commit

        except Exception as e:
            # Não-bloqueio em falha de rede/git (BR-MIGRAR-005)
            # Exibe o erro no stdout/stderr mas retorna True
            print(
                f"Aviso de Sincronia: Falha ao checar rede Git ({e}). Prosseguindo de forma resiliente."
            )
            return True

    def check_version_update(
        self, local_version: str, upstream_path: Optional[str]
    ) -> Optional[str]:
        """Compara a versão local com a do upstream. Retorna a versão mais recente se houver update."""
        if not upstream_path:
            return None

        try:
            # Varre os caminhos-candidato (canônico + legado) para sobreviver a
            # relocações do core no upstream — espelha _get_upstream_version do
            # init_service (feature 012). Mantém-se passiva e não-bloqueante.
            for rel in CORE_CONFIG_CANDIDATE_RELPATHS:
                config_path = os.path.join(upstream_path, rel)
                if not self.fs.exists(config_path):
                    continue
                content = self.fs.read_file(config_path)
                match = re.search(r'version:\s*str\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    upstream_version = match.group(1)
                    if upstream_version != local_version:
                        return upstream_version
                    return None
        except Exception:
            pass
        return None
