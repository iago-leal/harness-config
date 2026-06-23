import os
import re
from datetime import datetime, timezone
from typing import Optional, List
from src.core.ports.fs import FileSystemPort
from src.core.ports.git import GitPort
from src.core.domain.models import SessionState

class CommandService:
    def __init__(self, fs: FileSystemPort, git: GitPort):
        self.fs = fs
        self.git = git

    def load_session(self, filepath: str) -> Optional[SessionState]:
        """
        Carrega o estado da sessão a partir de um arquivo Markdown de sessão.
        """
        if not self.fs.exists(filepath):
            return None

        content = self.fs.read_file(filepath)
        
        feature_match = re.search(r"-\s+\*\*Active Feature:\*\* (.*)", content, re.IGNORECASE)
        commit_match = re.search(r"-\s+\*\*Commit Hash:\*\* (.*)", content, re.IGNORECASE)
        time_match = re.search(r"-\s+\*\*Start Time:\*\* (.*)", content, re.IGNORECASE)
        status_match = re.search(r"-\s+\*\*Status:\*\* (.*)", content, re.IGNORECASE)

        if not (feature_match and commit_match):
            return None

        active_feature = feature_match.group(1).strip()
        commit_hash = commit_match.group(1).strip()
        
        is_active = True
        if status_match:
            is_active = status_match.group(1).strip().lower() == "active"

        start_time = datetime.now(timezone.utc)
        if time_match:
            try:
                start_time = datetime.fromisoformat(time_match.group(1).strip())
                if start_time.tzinfo is None:
                    start_time = start_time.replace(tzinfo=timezone.utc)
            except Exception:
                pass

        return SessionState(
            commit_hash=commit_hash,
            active_feature=active_feature,
            start_time=start_time,
            is_active=is_active
        )

    def save_session(self, filepath: str, state: SessionState) -> None:
        """
        Salva o SessionState de forma atômica em um arquivo Markdown de sessão.
        """
        status_str = "active" if state.is_active else "inactive"
        content = (
            "# Estado da Sessão\n\n"
            f"- **Active Feature:** {state.active_feature}\n"
            f"- **Commit Hash:** {state.commit_hash}\n"
            f"- **Start Time:** {state.start_time.isoformat()}\n"
            f"- **Status:** {status_str}\n"
        )
        self.fs.write_file_atomic(filepath, content)

    def execute_command(self, command: str, args: List[str], repo_path: str, session_filepath: str) -> str:
        """
        Executa um slash command de forma agnóstica à IDE.
        """
        cmd_normalized = command.strip().lower().lstrip("/")

        if cmd_normalized == "encerrar-sessao":
            session = self.load_session(session_filepath)
            if not session or not session.is_active:
                return "Erro: Nenhuma sessão ativa encontrada para encerrar."

            # Valida âncora Git e isolamento (BR-MIGRAR-014 / BR-MIGRAR-015)
            current_commit = self.git.get_head_commit(repo_path)
            session.close_session(current_commit)
            self.save_session(session_filepath, session)
            return f"Sessão encerra com sucesso na feature '{session.active_feature}' com commit âncora {current_commit}."

        elif cmd_normalized == "resume":
            session = self.load_session(session_filepath)
            if not session:
                # Se não existir sessão anterior, cria uma padrão
                current_commit = self.git.get_head_commit(repo_path)
                feature_name = args[0] if args else "default_feature"
                session = SessionState(commit_hash=current_commit, active_feature=feature_name)
                self.save_session(session_filepath, session)
                return f"Nova sessão iniciada para a feature '{feature_name}'."

            current_commit = self.git.get_head_commit(repo_path)
            
            # Validação da Âncora de Integridade Git
            warning_msg = ""
            if session.commit_hash != current_commit:
                warning_msg = f"⚠️ ALERTA: O commit HEAD atual ({current_commit}) diverge do commit âncora da sessão anterior ({session.commit_hash})!\n"

            session.start_session(session.active_feature, current_commit)
            self.save_session(session_filepath, session)
            return f"{warning_msg}Sessão retomada com sucesso para a feature '{session.active_feature}' no commit {current_commit}."

        elif cmd_normalized == "clarificar":
            return (
                "## Clarificação de Requisitos\n"
                "Para evitar loops de IA, o diálogo de clarificação é limitado a no máximo **2 rodadas**.\n"
                "Por favor, responda de forma clara e concisa."
            )

        elif cmd_normalized == "handoff":
            current_commit = self.git.get_head_commit(repo_path)
            session = self.load_session(session_filepath)
            feature_name = session.active_feature if session else "N/A"
            return (
                "# Handoff Bastão\n\n"
                f"- **Feature:** {feature_name}\n"
                f"- **Commit HEAD:** {current_commit}\n"
                "- **Status:** Pronto para o próximo agente.\n"
            )

        else:
            return f"Comando desconhecido: {command}"
