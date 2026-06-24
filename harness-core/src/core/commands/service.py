from typing import Optional, List
from src.core.ports.fs import FileSystemPort
from src.core.ports.git import GitPort
from src.core.domain.models import SessionState, SessionNarrative
from src.core.session import serializer


class CommandService:
    def __init__(self, fs: FileSystemPort, git: GitPort):
        self.fs = fs
        self.git = git

    def load_session(self, filepath: str) -> Optional[SessionState]:
        """Carrega o estado de sessão do arquivo canônico.

        Arquivo ausente, ou presente no estado inicial do ``init`` (campos
        obrigatórios todos ``null``) → ``None`` (sessão nova, normal). Arquivo
        presente mas malformado → ``MalformedSessionStateError`` (RN-N4: erro
        barulhento, nunca degrada em silêncio para "sem sessão").
        """
        if not self.fs.exists(filepath):
            return None
        return serializer.parse(self.fs.read_file(filepath))

    def save_session(self, filepath: str, state: SessionState) -> None:
        """Salva o SessionState de forma atômica no formato canônico (round-trip)."""
        self.fs.write_file_atomic(filepath, serializer.render(state))

    def execute_command(
        self, command: str, args: List[str], repo_path: str, session_filepath: str
    ) -> str:
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
                session = SessionState(
                    commit_hash=current_commit, active_feature=feature_name
                )
                self.save_session(session_filepath, session)
                return f"Nova sessão iniciada para a feature '{feature_name}'."

            current_commit = self.git.get_head_commit(repo_path)

            # Validação da Âncora de Integridade Git
            warning_msg = ""
            if session.commit_hash != current_commit:
                warning_msg = f"⚠️ ALERTA: O commit HEAD atual ({current_commit}) diverge do commit âncora da sessão anterior ({session.commit_hash})!\n"

            # start_session reativa preservando a narrativa escrita pelo agente
            session.start_session(session.active_feature, current_commit)
            self.save_session(session_filepath, session)
            body = serializer.render_narrative(session.narrative or SessionNarrative())
            footer = f"Sessão retomada com sucesso para a feature '{session.active_feature}' no commit {current_commit}."
            return f"{warning_msg}{body}\n{footer}"

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
