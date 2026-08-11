"""Medidor de progresso de entregáveis (feature 026).

Serviço PURO de medição: computa uma ``Medicao`` a partir de quatro fontes
só-leitura — ``.reversa/active-requirements.json``, os artefatos físicos de
``_reversa_forward/*``, os ``regression-watch.md`` das features e o estado do
próprio harness (sessão, fichas MD, gate de registro em leitura pura). Nada
aqui grava coisa alguma: a ``Medicao`` é transitória (espelho do
``GateVerdict``) e a projeção em markdown/JSON cabe a ``render.py``; a escrita
do artefato derivado cabe à borda (``main.py``).

Fail-soft barulhento (RN-N43): fonte legitimamente ausente vira ``n/a``;
fonte presente mas ilegível vira entrada em ``falhas`` (a borda ecoa em
stderr e sai com 2, sem sobrescrever o artefato com medição degradada), sem
derrubar a medição das demais fontes.
"""

import json
import os
import re
from typing import List, Optional

from pydantic import BaseModel, Field

from src.core.commands.service import CommandService
from src.core.decisions.gate import evaluate_registration_gate
from src.core.progress import kanban, stages

_FICHA_RE = re.compile(r"^MD-.*\.md$")
_FEATURE_DIR_RE = re.compile(r"^\d")
_MARCA_RECONCILIACAO = "pendência de reconciliação"

_STATE_PATH = ".reversa/state.json"
_ACTIVE_REQUIREMENTS_PATH = ".reversa/active-requirements.json"
_FORWARD_FOLDER_DEFAULT = "_reversa_forward"


class FasesProgresso(BaseModel):
    """Contagem de checkboxes de uma fase do ``actions.md``."""

    fase: str
    feitas: int = 0
    total: int = 0


class AcaoProgresso(BaseModel):
    """Uma ação individual do ``actions.md``, com o ID real da tabela.

    ``criada_em`` deriva da primeira linha da ação no ``progress.jsonl`` (ou,
    em fallback, do ``started-at`` da feature): nunca da hora corrente, para
    que a medição siga 100% recomputável (feature 027, D-06).
    """

    acao_id: str
    descricao: str = ""
    fase: str = ""
    feita: bool = False
    criada_em: str = ""


class FeatureProgresso(BaseModel):
    """Uma feature do ciclo forward, medida pelos artefatos físicos."""

    feature_id: str
    short_name: str = ""
    papel: str = "ativa"  # ativa | pausada
    estagio_fisico: str = "vazio"
    estagio_declarado: str = ""
    iniciada_em: str = ""
    fases: List[FasesProgresso] = Field(default_factory=list)
    acoes: List[AcaoProgresso] = Field(default_factory=list)
    feitas: int = 0
    total: int = 0


class Demanda(BaseModel):
    """Card manual do board kanban em coluna não-``done``: entrada de demanda
    do mantenedor para o agente executar pelo processo forward (027, RN-06)."""

    card_id: str = ""
    titulo: str = ""
    coluna: str = ""


class Alerta(BaseModel):
    """Achado persistente: existe enquanto a causa existir (RN-03, D-07)."""

    severidade: str  # alta | media
    origem: str
    mensagem: str


class HarnessMedicao(BaseModel):
    """Estado do próprio harness: sessão, fichas MD e pendência do gate."""

    sessao_status: str = "n/a"  # ativa | encerrada | n/a
    ancora: str = ""
    fichas_total: int = 0
    ultima_ficha: str = ""
    gate_pendente: Optional[bool] = None
    gate_mudancas: int = 0


class Medicao(BaseModel):
    """Resultado completo da medição. Transitória, nunca persistida."""

    forward_disponivel: bool = False
    ativa: Optional[FeatureProgresso] = None
    pausadas: List[FeatureProgresso] = Field(default_factory=list)
    concluidas: int = 0
    outras_incompletas: int = 0
    harness: HarnessMedicao = Field(default_factory=HarnessMedicao)
    board_habilitado: bool = False
    demandas: List[Demanda] = Field(default_factory=list)
    alertas: List[Alerta] = Field(default_factory=list)
    avisos: List[str] = Field(default_factory=list)
    falhas: List[str] = Field(default_factory=list)


class ProgressService:
    """Computa a ``Medicao`` das quatro fontes, em leitura pura."""

    def __init__(self, fs, git):
        self.fs = fs
        self.git = git

    def measure(self, repo_path: str, config) -> Medicao:
        medicao = Medicao()
        self._medir_forward(medicao)
        self._medir_harness(medicao, repo_path, config)
        self._medir_demandas(medicao, config)
        ordem = {"alta": 0, "media": 1}
        medicao.alertas.sort(
            key=lambda a: (ordem.get(a.severidade, 9), a.origem, a.mensagem)
        )
        return medicao

    # --- Ciclo forward ----------------------------------------------------

    def _medir_forward(self, medicao: Medicao) -> None:
        forward_folder = self._forward_folder(medicao)
        if not self.fs.exists(_ACTIVE_REQUIREMENTS_PATH):
            # Projeto sem ciclo forward: n/a legítimo, não é falha (RN-05).
            return
        try:
            ativos = json.loads(self.fs.read_file(_ACTIVE_REQUIREMENTS_PATH))
        except Exception as exc:
            medicao.falhas.append(f"{_ACTIVE_REQUIREMENTS_PATH}: JSON inválido ({exc})")
            return

        medicao.forward_disponivel = True
        registradas = set()

        feature_dir = str(ativos.get("feature-dir") or "").strip().rstrip("/")
        if feature_dir:
            registradas.add(os.path.basename(feature_dir))
            medicao.ativa = self._medir_feature(
                feature_dir,
                str(ativos.get("feature-id") or ""),
                str(ativos.get("short-name") or ""),
                papel="ativa",
                declarado=str(ativos.get("current-stage") or ""),
                iniciada_em=str(ativos.get("started-at") or ""),
            )
            if not self.fs.exists(feature_dir):
                medicao.alertas.append(
                    Alerta(
                        severidade="alta",
                        origem=feature_dir,
                        mensagem=(
                            "feature-dir declarado em active-requirements.json "
                            "não existe em disco"
                        ),
                    )
                )
            else:
                declarado = medicao.ativa.estagio_declarado
                fisico = medicao.ativa.estagio_fisico
                # `coding` declarado casa com `coding-em-progresso` físico; o
                # metadado é informativo, mas duas medidas do mesmo fato que
                # discordam viram alerta, jamais reconciliação silenciosa (RN-03).
                if declarado and not (
                    fisico == declarado or fisico.startswith(declarado)
                ):
                    medicao.alertas.append(
                        Alerta(
                            severidade="alta",
                            origem=feature_dir,
                            mensagem=(
                                f"estágio declarado '{declarado}' diverge do "
                                f"estágio físico '{fisico}'"
                            ),
                        )
                    )

        for pausada in ativos.get("paused-features") or []:
            pausada_dir = str(pausada.get("feature-dir") or "").strip().rstrip("/")
            if not pausada_dir:
                continue
            registradas.add(os.path.basename(pausada_dir))
            medicao.pausadas.append(
                self._medir_feature(
                    pausada_dir,
                    str(pausada.get("feature-id") or ""),
                    str(pausada.get("short-name") or ""),
                    papel="pausada",
                    declarado=str(pausada.get("paused-from-stage") or ""),
                    iniciada_em=str(pausada.get("started-at") or ""),
                )
            )
        medicao.pausadas.sort(key=lambda f: f.feature_id)

        self._varrer_forward_folder(medicao, forward_folder, registradas)

    def _forward_folder(self, medicao: Medicao) -> str:
        if not self.fs.exists(_STATE_PATH):
            return _FORWARD_FOLDER_DEFAULT
        try:
            state = json.loads(self.fs.read_file(_STATE_PATH))
            return str(state.get("forward_folder") or _FORWARD_FOLDER_DEFAULT)
        except Exception as exc:
            medicao.avisos.append(
                f"{_STATE_PATH} ilegível; assumindo '{_FORWARD_FOLDER_DEFAULT}' ({exc})"
            )
            return _FORWARD_FOLDER_DEFAULT

    def _medir_feature(
        self,
        feature_dir: str,
        feature_id: str,
        short_name: str,
        papel: str,
        declarado: str,
        iniciada_em: str = "",
    ) -> FeatureProgresso:
        progresso = FeatureProgresso(
            feature_id=feature_id or os.path.basename(feature_dir).split("-", 1)[0],
            short_name=short_name,
            papel=papel,
            estagio_declarado=declarado,
            iniciada_em=iniciada_em,
            estagio_fisico=stages.detectar_estagio(self.fs, feature_dir),
        )
        actions_path = f"{feature_dir}/actions.md"
        if self.fs.exists(actions_path):
            texto = self.fs.read_file(actions_path)
            progresso.fases = [
                FasesProgresso(fase=fase, feitas=feitas, total=total)
                for fase, feitas, total in stages.contar_por_fase(texto)
            ]
            progresso.feitas, progresso.total = stages.contar_checkboxes(texto)
            criacao = self._criacao_por_acao(feature_dir)
            progresso.acoes = [
                AcaoProgresso(
                    acao_id=acao_id,
                    descricao=descricao,
                    fase=fase,
                    feita=feita,
                    criada_em=criacao.get(acao_id, iniciada_em),
                )
                for fase, acao_id, descricao, feita in stages.listar_acoes(texto)
            ]
        return progresso

    def _criacao_por_acao(self, feature_dir: str) -> dict:
        """``{acao_id: ts}`` da PRIMEIRA linha de cada ação no progress.jsonl.

        Fonte determinística do ``creation_time`` dos cards (027, D-06);
        linhas corrompidas do log são puladas em silêncio (append-only,
        auxiliar). Log ausente → mapa vazio (fallback: ``started-at``).
        """
        log_path = f"{feature_dir}/progress.jsonl"
        if not self.fs.exists(log_path):
            return {}
        criacao: dict = {}
        for linha in self.fs.read_file(log_path).splitlines():
            try:
                registro = json.loads(linha)
            except Exception:
                continue
            acao = str(registro.get("action") or "")
            ts = str(registro.get("ts") or "")
            if acao and ts and acao not in criacao:
                criacao[acao] = ts
        return criacao

    def _varrer_forward_folder(
        self, medicao: Medicao, forward_folder: str, registradas: set
    ) -> None:
        if not self.fs.exists(forward_folder):
            return
        try:
            nomes = sorted(self.fs.list_dir(forward_folder))
        except Exception as exc:
            medicao.avisos.append(f"{forward_folder} ilegível ({exc})")
            return
        for nome in nomes:
            caminho = f"{forward_folder}/{nome}"
            if not _FEATURE_DIR_RE.match(nome) or not self.fs.is_dir(caminho):
                continue
            watch_path = f"{caminho}/regression-watch.md"
            if self.fs.exists(watch_path):
                try:
                    if _MARCA_RECONCILIACAO in self.fs.read_file(watch_path).lower():
                        medicao.alertas.append(
                            Alerta(
                                severidade="media",
                                origem=watch_path,
                                mensagem="pendência de reconciliação em aberto",
                            )
                        )
                except Exception as exc:
                    medicao.avisos.append(f"{watch_path} ilegível ({exc})")
            if nome in registradas:
                continue
            if stages.detectar_estagio(self.fs, caminho) == "done":
                medicao.concluidas += 1
            else:
                medicao.outras_incompletas += 1

    # --- Harness ----------------------------------------------------------

    def _medir_harness(self, medicao: Medicao, repo_path: str, config) -> None:
        session = None
        try:
            session = CommandService(self.fs, self.git).load_session(
                config.session.state_file
            )
        except Exception as exc:
            medicao.falhas.append(
                f"{config.session.state_file}: estado de sessão ilegível ({exc})"
            )

        if session is not None:
            medicao.harness.sessao_status = "ativa" if session.is_active else "encerrada"
            medicao.harness.ancora = session.commit_hash
            # Reuso do gate em LEITURA PURA (D-05): o veredito informa a
            # pendência, mas nenhum fingerprint é persistido daqui.
            verdict = evaluate_registration_gate(self.git, repo_path, session, config)
            if verdict.aviso:
                medicao.avisos.append(verdict.aviso)
            else:
                medicao.harness.gate_pendente = verdict.pendente
                medicao.harness.gate_mudancas = len(verdict.mudancas)

        decisoes_dir = config.decisions.dir
        if self.fs.exists(decisoes_dir):
            try:
                fichas = sorted(
                    nome
                    for nome in self.fs.list_dir(decisoes_dir)
                    if _FICHA_RE.match(nome)
                )
            except Exception as exc:
                medicao.avisos.append(f"{decisoes_dir} ilegível ({exc})")
                return
            medicao.harness.fichas_total = len(fichas)
            if fichas:
                medicao.harness.ultima_ficha = fichas[-1][: -len(".md")]

    # --- Board kanban (quinta fonte, feature 027) -------------------------

    def _medir_demandas(self, medicao: Medicao, config) -> None:
        """Cards MANUAIS do board em coluna não-``done`` viram demandas.

        O board só é lido com ``[progress.kanban] enabled = true`` (opt-in,
        D-03) e SOMENTE pelos cards manuais: os gerenciados são projeção da
        própria ``Medicao`` e jamais fonte (RN-05). Board presente mas
        ilegível é falha real (RN-07): a borda sai com 2 sem regravar nada.
        """
        secao = config.progress.kanban
        if not secao.enabled:
            return
        medicao.board_habilitado = True
        if not self.fs.exists(secao.file):
            # Primeira exportação: ausência legítima, não é falha.
            return
        try:
            manuais = kanban.extrair_manuais(self.fs.read_file(secao.file))
        except Exception as exc:
            medicao.falhas.append(f"{secao.file}: board ilegível ({exc})")
            return
        for coluna in ("todo", "in-progress", "testing"):
            for card in manuais.get(coluna, []):
                if not isinstance(card, dict):
                    continue
                medicao.demandas.append(
                    Demanda(
                        card_id=str(card.get("id") or ""),
                        titulo=str(card.get("title") or ""),
                        coluna=coluna,
                    )
                )
