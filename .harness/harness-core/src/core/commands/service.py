from typing import Optional, List
from src.core.ports.fs import FileSystemPort
from src.core.ports.git import GitPort
from src.core.commands.errors import SessionCommitError
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
        self,
        command: str,
        args: List[str],
        repo_path: str,
        session_filepath: str,
        *,
        versionar_estado: bool = True,
        caminhos_extras: Optional[List[str]] = None,
    ) -> str:
        """
        Executa um slash command de forma agnóstica à IDE.

        ``versionar_estado`` (feature 024/D-03): quando ``True`` (default, que
        preserva todos os chamadores atuais — inclusive a borda MCP), o
        encerramento grava o commit de encerramento por cima do trabalho, como
        antes. Quando ``False``, o estado é fechado no arquivo mas NÃO versionado
        (o ``commit_paths`` é pulado); o desfecho fica registrado na narrativa
        (D-05) e o arquivo permanece como mudança pendente no working tree. A
        decisão chega pronta da borda (``SessionCloseFlow``), que sabe se há
        terminal e autorização; o serviço permanece livre de IO de pergunta.

        ``caminhos_extras`` (MD-0026): artefatos do próprio harness que a borda
        regravou nesta passada (as visões de decisões, no MCP) e que entram no
        commit de encerramento junto do estado — sempre por caminho explícito,
        nunca ``git add -A``. Ignorado quando ``versionar_estado=False`` ou em
        comandos que não commitam.
        """
        cmd_normalized = command.strip().lower().lstrip("/")

        if cmd_normalized == "encerrar-sessao":
            session = self.load_session(session_filepath)
            if session is None:
                # D1 (016): sessão AUSENTE não é erro — não há nada a encerrar.
                # No-op ruidoso (a borda imprime e sai com 0), sem commit. O
                # malformado segue barulhento (load_session levanta antes daqui,
                # RN-N4): ausente ≠ malformado.
                return (
                    "Nenhuma sessão para encerrar (estado de sessão ausente). "
                    "Nada foi encerrado; a sessão reabre no próximo boot/resume."
                )

            # Âncora = último commit de TRABALHO, capturada ANTES de qualquer
            # escrita. O commit de encerramento fica por cima; a âncora nunca
            # aponta para ele (BR-MIGRAR-014 / BR-MIGRAR-015, RN-07). Sem
            # versionamento, o HEAD nem se move, e a âncora coincide com ele.
            ancora = self.git.get_head_commit(repo_path)
            feature = session.active_feature

            reativada = not session.is_active
            if reativada:
                # D1/D3 (016): sessão INATIVA reativa preservando a narrativa
                # (RN-N3) e fecha no mesmo passo. O espírito ruidoso da 015 é
                # mantido pelo anúncio na mensagem de saída, não por um erro.
                session.start_session(feature, ancora)
            session.close_session(ancora)

            if not versionar_estado:
                # Desfecho não versionado (024/RN-04/RN-08): fecha no arquivo, não
                # commita. Registra o ato na narrativa (D-05, RN-N3: o core não
                # inventa narrativa, apenas registra ato deliberado); o motivo
                # detalhado vive no marker da borda.
                session.narrative.feito.append(
                    "Encerramento não versionado: o estado de sessão ficou como "
                    "mudança pendente no working tree."
                )
                self.save_session(session_filepath, session)
                msg = (
                    f"Sessão encerrada (sem versionar o estado) na feature "
                    f"'{feature}' com âncora {ancora}; o estado de sessão ficou "
                    "como mudança pendente no working tree."
                )
                if reativada:
                    msg += (
                        "\n(Sessão estava inativa; reativada automaticamente antes "
                        "de encerrar.)"
                    )
                return msg

            self.save_session(session_filepath, session)

            # Versiona o arquivo de estado e, quando a borda os regravou, os
            # artefatos derivados do próprio harness (caminhos_extras) — sempre
            # por caminho explícito, jamais git add -A: o registro de
            # encerramento entra no histórico sem arrastar mudanças alheias do
            # working tree. Falha de commit é barulhenta e preserva o estado salvo.
            try:
                commit_encerramento = self.git.commit_paths(
                    repo_path,
                    [session_filepath, *(caminhos_extras or [])],
                    f"chore(sessao): encerrar sessão {feature}; âncora {ancora}",
                )
            except Exception as exc:
                raise SessionCommitError(
                    f"Falha ao versionar o encerramento da sessão '{feature}': {exc}"
                ) from exc

            msg = (
                f"Sessão encerrada com sucesso na feature '{feature}' "
                f"com commit âncora {ancora} e commit de encerramento {commit_encerramento}."
            )
            if reativada:
                msg += (
                    "\n(Sessão estava inativa; reativada automaticamente antes de "
                    "encerrar.)"
                )
            return msg

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
