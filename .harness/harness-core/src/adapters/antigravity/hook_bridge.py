"""Adaptador de borda do protocolo de ganchos do Antigravity.

Terceiro driver de entrada do hexágono (simétrico à CLI e ao servidor MCP):
fala o contrato stdin/stdout do Antigravity (JSON camelCase, um formato por
evento) e delega aos serviços de domínio já existentes, mantendo o core
agnóstico ao harness (RN-N5).

Eventos suportados (ver `interfaces/antigravity-hook-io.md`):
- ``pre-tool-use``  → grava o mapa ``stepIdx → TargetFile`` no scratch e emite
  ``{"decision": "allow"}`` (nunca bloqueia).
- ``post-tool-use`` → recupera o caminho pelo ``stepIdx`` e chama o serviço de
  formatação; emite ``{}``.
- ``stop``          → roda o serviço de decisões; emite ``{}`` (nunca
  ``{"decision": "continue"}``).

Garantia não-bloqueante: toda exceção é capturada, logada em ``stderr`` (erro
barulhento) e o stdout exigido por evento é emitido mesmo assim, com saída 0,
preservando o laço do agente.
"""

import json
import os
import sys

# Subdiretório de scratch sob o `artifactDirectoryPath` informado no payload.
_SCRATCH_DIRNAME = ".harness-agy"
_SCRATCH_FILENAME = "pending-format.json"


class AntigravityHookBridge:
    """Traduz o protocolo de ganchos do Antigravity para os serviços de domínio.

    Os serviços de domínio e o sistema de arquivos entram por injeção; a
    seleção/instanciação dos adaptadores concretos fica na borda (CLI), não
    aqui — o adaptador permanece testável com dublês.
    """

    def __init__(
        self,
        fs,
        formatting_service,
        decision_service,
        decisions_dir: str,
        decisions_index_file: str,
        decisions_header_file: str,
        gate_evaluator=None,
    ):
        self.fs = fs
        self.formatting_service = formatting_service
        self.decision_service = decision_service
        self.decisions_dir = decisions_dir
        self.decisions_index_file = decisions_index_file
        self.decisions_header_file = decisions_header_file
        # Feature 022 (advisory): callable sem argumentos, montado na borda, que
        # devolve um GateVerdict (ou None quando o gate não se aplica). O bridge
        # não conhece git/config — só consome o veredito para AVISAR em stderr;
        # o contrato do Stop (RN-N26: nunca bloquear) permanece intocado.
        self.gate_evaluator = gate_evaluator

    # -- API pública -------------------------------------------------------- #

    def handle(self, event: str, stdin_text: str) -> str:
        """Despacha por evento e devolve o stdout JSON exigido pelo contrato.

        Nunca levanta: a exceção é logada e o stdout-padrão do evento é
        emitido mesmo assim (não-bloqueante).
        """
        if event == "pre-tool-use":
            return self._safe(
                event, self._handle_pre_tool_use, stdin_text, {"decision": "allow"}
            )
        if event == "post-tool-use":
            return self._safe(event, self._handle_post_tool_use, stdin_text, {})
        if event == "stop":
            return self._safe(event, self._handle_stop, stdin_text, {})
        # Evento desconhecido: não-bloqueante, objeto vazio.
        self._log(f"evento desconhecido: {event!r}")
        return json.dumps({})

    # -- Handlers por evento ------------------------------------------------ #

    def _handle_pre_tool_use(self, stdin_text: str) -> dict:
        """Captura: grava ``stepIdx → TargetFile`` no scratch da conversa."""
        payload = json.loads(stdin_text)
        step_idx = payload.get("stepIdx")
        tool_call = payload.get("toolCall") or {}
        args = tool_call.get("args") or {}
        target_file = args.get("TargetFile")

        if step_idx is not None and target_file:
            scratch_path = self._scratch_path(payload)
            if scratch_path:
                mapa = self._read_map(scratch_path)
                mapa[str(step_idx)] = target_file
                self._write_map(scratch_path, mapa)

        return {"decision": "allow"}

    def _handle_post_tool_use(self, stdin_text: str) -> dict:
        """Formatação: resolve o caminho pelo ``stepIdx`` e formata, se elegível."""
        payload = json.loads(stdin_text)
        step_idx = payload.get("stepIdx")
        tool_error = payload.get("error")

        # Tool falhou ou índice ausente: nada a formatar (não-bloqueante).
        if step_idx is not None and not tool_error:
            scratch_path = self._scratch_path(payload)
            if scratch_path and self.fs.exists(scratch_path):
                mapa = self._read_map(scratch_path)
                target_file = mapa.get(str(step_idx))
                if target_file:
                    # format_file já honra opt-out, exclusões e retorna sempre 0.
                    self.formatting_service.format_file(target_file)

        return {}

    def _handle_stop(self, stdin_text: str) -> dict:
        """Decisões: valida e reindexa as microdecisões (equivale a `harness decisions`)."""
        decisions = self.decision_service.load_decisions(self.decisions_dir)
        errors = self.decision_service.validate_integrity(decisions)
        if errors:
            # Erro barulhento, mas não-bloqueante: nunca reentra no laço.
            self._log("microdecisões com erros de integridade: " + "; ".join(errors))
        self.decision_service.compile_index(
            decisions, self.decisions_index_file, self.decisions_header_file
        )

        # Advisory do gate de registro (022): pendência vira aviso em stderr,
        # nunca bloqueio nem reentrada no laço (RN-N26). Falha do avaliador é
        # capturada aqui para não descartar a reindexação já feita acima.
        if self.gate_evaluator is not None:
            try:
                verdict = self.gate_evaluator()
                if verdict is not None and verdict.pendente:
                    self._log(
                        "gate de registro: decisão pendente de registro — "
                        f"{len(verdict.mudancas)} mudança(s) sem ficha MD-NNNN; "
                        "registre em .harness/decisoes/ ou encerre a sessão com "
                        "--sem-decisao (advisory, nunca bloqueia)"
                    )
            except Exception as exc:  # noqa: BLE001 — advisory jamais bloqueia
                self._log(f"gate de registro (advisory) falhou: {exc}")

        return {}

    # -- Scratch (mapa stepIdx → TargetFile) -------------------------------- #

    def _scratch_path(self, payload: dict):
        """Resolve o arquivo de scratch sob ``artifactDirectoryPath``."""
        artifact_dir = payload.get("artifactDirectoryPath")
        if not artifact_dir:
            return None
        return os.path.join(artifact_dir, _SCRATCH_DIRNAME, _SCRATCH_FILENAME)

    def _read_map(self, scratch_path: str) -> dict:
        """Lê o mapa do scratch; mapa vazio se ausente ou ilegível."""
        if not self.fs.exists(scratch_path):
            return {}
        try:
            data = json.loads(self.fs.read_file(scratch_path))
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def _write_map(self, scratch_path: str, mapa: dict) -> None:
        """Grava o mapa de forma atômica, criando o diretório de scratch."""
        scratch_dir = os.path.dirname(scratch_path)
        if scratch_dir:
            self.fs.makedirs(scratch_dir)
        self.fs.write_file_atomic(scratch_path, json.dumps(mapa))

    # -- Robustez ----------------------------------------------------------- #

    def _safe(self, event: str, handler, stdin_text: str, fallback: dict) -> str:
        """Executa o handler; em qualquer falha, loga e emite o fallback do evento."""
        try:
            return json.dumps(handler(stdin_text))
        except Exception as exc:  # noqa: BLE001 — blindagem deliberada, não-bloqueante
            self._log(f"falha no gancho {event}: {exc}")
            return json.dumps(fallback)

    def _log(self, message: str) -> None:
        """Erro barulhento em stderr, jamais em stdout (reservado ao contrato)."""
        print(f"[harness agy-hook] {message}", file=sys.stderr)
