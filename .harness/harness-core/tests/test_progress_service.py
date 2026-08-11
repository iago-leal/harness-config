"""Testes do serviço de medição e dos renderizadores (feature 026).

O serviço é PURO: mede as quatro fontes em leitura, nunca grava nada (RN-04)
nem persiste fingerprint do gate (D-05). O markdown é estável byte a byte
entre medições do mesmo estado e não carrega timestamp nem caminho absoluto
(RN-01/RN-02); o JSON carimba ``aferido_em`` porque stdout não é versionado.
"""

import json

from src.core.domain.config import HarnessConfig
from src.core.progress.render import render_json, render_markdown
from src.core.progress.service import ProgressService

ANCORA = "a" * 40
HEAD = "b" * 40


class DictFs:
    """FS em memória, com auditoria de escrita (o serviço não pode escrever)."""

    def __init__(self, files=None):
        self.files = dict(files or {})
        self.writes = []

    def exists(self, path):
        p = path.rstrip("/")
        return p in self.files or any(k.startswith(p + "/") for k in self.files)

    def read_file(self, path):
        return self.files[path]

    def is_dir(self, path):
        p = path.rstrip("/")
        return any(k.startswith(p + "/") for k in self.files)

    def list_dir(self, path):
        p = path.rstrip("/") + "/"
        nomes = set()
        for k in self.files:
            if k.startswith(p):
                nomes.add(k[len(p):].split("/", 1)[0])
        return sorted(nomes)

    def write_file(self, path, content):
        self.writes.append(path)

    def write_file_atomic(self, path, content):
        self.writes.append(path)

    def makedirs(self, path):
        self.writes.append(path)


class FakeGit:
    def __init__(self, dirty=None, changed=None):
        self.dirty = dirty or []
        self.changed = changed or []

    def get_head_commit(self, repo_path):
        return HEAD

    def list_dirty_paths(self, repo_path):
        return list(self.dirty)

    def list_changed_paths_since(self, repo_path, ref):
        return list(self.changed)


ACTIONS_1_DE_2 = """# Actions

## Fase 1, Preparação

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T001 | a | - | - | `x` | 🟢 | `[X]` |
| T002 | b | - | - | `y` | 🟢 | `[ ]` |
"""

ACTIONS_DONE = ACTIONS_1_DE_2.replace("`[ ]`", "`[X]`")

SESSAO_ATIVA = (
    f"---\ncommit: {ANCORA}\nfeature: feat-teste\n"
    "start_time: 2026-08-11T10:00:00+00:00\nstatus: active\n---\n\n"
    "## O que foi feito\n- trabalhou\n\n## Próximos passos\n\n"
    "## Pendências / bloqueios\n\n## Ponteiros\n"
)


def _feature_files(dirname, actions=None, com_roadmap=True):
    base = f"_reversa_forward/{dirname}"
    files = {f"{base}/requirements.md": "# r"}
    if com_roadmap:
        files[f"{base}/roadmap.md"] = "# p"
    if actions is not None:
        files[f"{base}/actions.md"] = actions
    return files


def _projeto(declarado="coding", com_sessao=True):
    files = {
        ".reversa/state.json": json.dumps(
            {"output_folder": "_reversa_sdd", "forward_folder": "_reversa_forward"}
        ),
        ".reversa/active-requirements.json": json.dumps(
            {
                "schema-version": 1,
                "feature-dir": "_reversa_forward/026-ativa",
                "feature-id": "026",
                "short-name": "ativa",
                "current-stage": declarado,
                "paused-features": [
                    {
                        "feature-dir": "_reversa_forward/024-pausada",
                        "feature-id": "024",
                        "short-name": "pausada",
                        "paused-from-stage": "coding-em-progresso",
                    }
                ],
            }
        ),
        ".harness/decisoes/MD-0001.md": "ficha",
        ".harness/decisoes/MD-0002.md": "ficha",
        ".harness/decisoes/_cabecalho.md": "cabeçalho",
    }
    files.update(_feature_files("026-ativa", ACTIONS_1_DE_2))
    files.update(_feature_files("024-pausada", ACTIONS_1_DE_2))
    files.update(_feature_files("001-feita", ACTIONS_DONE))
    files.update(_feature_files("002-orfa", actions=None, com_roadmap=False))
    files["_reversa_forward/001-feita/regression-watch.md"] = (
        "# Watch\n\n## Pendência de reconciliação\n\n- re-extração dirigida\n"
    )
    if com_sessao:
        files[".harness/estado-da-sessao.md"] = SESSAO_ATIVA
    return files


def _medir(files, git=None, config=None):
    fs = DictFs(files)
    service = ProgressService(fs, git or FakeGit())
    medicao = service.measure("/repo", config or HarnessConfig())
    return medicao, fs


def test_medicao_completa_do_ciclo_forward():
    medicao, _ = _medir(_projeto())
    assert medicao.forward_disponivel is True
    assert medicao.ativa.feature_id == "026"
    assert medicao.ativa.estagio_fisico == "coding-em-progresso"
    assert (medicao.ativa.feitas, medicao.ativa.total) == (1, 2)
    assert medicao.ativa.fases[0].fase == "Fase 1, Preparação"
    assert [p.feature_id for p in medicao.pausadas] == ["024"]
    assert (medicao.pausadas[0].feitas, medicao.pausadas[0].total) == (1, 2)
    assert medicao.concluidas == 1
    assert medicao.outras_incompletas == 1
    assert medicao.falhas == []


def test_declarado_compativel_com_fisico_nao_alerta():
    # `coding` declarado × `coding-em-progresso` físico: mesmo estágio, sem alerta.
    medicao, _ = _medir(_projeto(declarado="coding"))
    assert [a for a in medicao.alertas if a.severidade == "alta"] == []


def test_divergencia_declarado_fisico_e_alerta_alta():
    medicao, _ = _medir(_projeto(declarado="requirements"))
    altas = [a for a in medicao.alertas if a.severidade == "alta"]
    assert len(altas) == 1
    assert "requirements" in altas[0].mensagem
    assert "coding-em-progresso" in altas[0].mensagem


def test_feature_dir_inexistente_e_alerta_alta():
    files = _projeto()
    for k in list(files):
        if k.startswith("_reversa_forward/026-ativa/"):
            del files[k]
    medicao, _ = _medir(files)
    altas = [a for a in medicao.alertas if a.severidade == "alta"]
    assert len(altas) == 1
    assert "026-ativa" in altas[0].origem


def test_pendencia_de_reconciliacao_e_alerta_media():
    medicao, _ = _medir(_projeto())
    medias = [a for a in medicao.alertas if a.severidade == "media"]
    assert len(medias) == 1
    assert "001-feita/regression-watch.md" in medias[0].origem


def test_sem_active_requirements_forward_vira_na():
    files = {k: v for k, v in _projeto().items() if "active-requirements" not in k}
    medicao, _ = _medir(files)
    assert medicao.forward_disponivel is False
    assert medicao.ativa is None
    assert medicao.alertas == []
    assert medicao.falhas == []


def test_active_requirements_corrompido_e_falha_real():
    files = _projeto()
    files[".reversa/active-requirements.json"] = "{ isso não é json"
    medicao, _ = _medir(files)
    assert len(medicao.falhas) == 1
    assert "active-requirements.json" in medicao.falhas[0]


def test_sessao_malformada_e_falha_real():
    files = _projeto()
    files[".harness/estado-da-sessao.md"] = "---\nlixo sem campos\n"
    medicao, _ = _medir(files)
    assert any("estado" in f for f in medicao.falhas)


def test_harness_medido_com_sessao_fichas_e_gate_puro():
    files = _projeto()
    fs = DictFs(files)
    git = FakeGit(dirty=["src/novo.py"])
    medicao = ProgressService(fs, git).measure("/repo", HarnessConfig())
    assert medicao.harness.sessao_status == "ativa"
    assert medicao.harness.ancora == ANCORA
    assert medicao.harness.fichas_total == 2
    assert medicao.harness.ultima_ficha == "MD-0002"
    assert medicao.harness.gate_pendente is True
    assert medicao.harness.gate_mudancas == 1
    # Leitura pura (D-05, RN-04): nenhuma escrita, nem de fingerprint.
    assert fs.writes == []


def test_sem_sessao_harness_fica_na():
    medicao, _ = _medir(_projeto(com_sessao=False))
    assert medicao.harness.sessao_status == "n/a"
    assert medicao.harness.gate_pendente is None
    assert medicao.harness.fichas_total == 2


def test_markdown_estavel_sem_timestamp_nem_caminho_absoluto():
    a, _ = _medir(_projeto())
    b, _ = _medir(_projeto())
    md = render_markdown(a)
    assert md == render_markdown(b)
    assert "aferido" not in md.lower()
    assert "/Users/" not in md and "/repo" not in md
    assert "## Ciclo forward" in md
    assert "## Harness" in md
    assert "## Alertas" in md
    assert "coding-em-progresso" in md
    assert "1/2" in md
    assert "MD-0002" in md


def test_markdown_sem_alertas_diz_nenhum():
    files = _projeto()
    del files["_reversa_forward/001-feita/regression-watch.md"]
    medicao, _ = _medir(files)
    md = render_markdown(medicao)
    assert "- nenhum" in md.split("## Alertas")[1]


def test_alertas_ordenados_por_severidade():
    medicao, _ = _medir(_projeto(declarado="requirements"))
    severidades = [a.severidade for a in medicao.alertas]
    assert severidades == sorted(severidades, key=lambda s: {"alta": 0, "media": 1}[s])


def test_json_carimba_aferido_em():
    medicao, _ = _medir(_projeto())
    data = json.loads(render_json(medicao, "2026-08-11T12:00:00-03:00"))
    assert data["aferido_em"] == "2026-08-11T12:00:00-03:00"
    assert data["ativa"]["feature_id"] == "026"
    assert data["harness"]["fichas_total"] == 2


# --- Board kanban como quinta fonte (feature 027) --------------------------


def _config_kanban():
    return HarnessConfig(progress={"kanban": {"enabled": True}})


def _board(todo=(), done=()):
    return json.dumps(
        {"todo": list(todo), "in-progress": [], "testing": [], "done": list(done)}
    )


def test_acoes_individuais_com_criacao_derivada_do_jsonl():
    files = _projeto()
    ativos = json.loads(files[".reversa/active-requirements.json"])
    ativos["started-at"] = "2026-08-10T09:00:00Z"
    files[".reversa/active-requirements.json"] = json.dumps(ativos)
    files["_reversa_forward/026-ativa/progress.jsonl"] = (
        '{"ts": "2026-08-11T12:00:00Z", "action": "T001", "status": "done"}\n'
        "linha corrompida do log\n"
        '{"ts": "2026-08-11T13:00:00Z", "action": "T001", "status": "corrected"}\n'
    )
    medicao, _ = _medir(files)
    acoes = medicao.ativa.acoes
    assert [(a.acao_id, a.feita) for a in acoes] == [("T001", True), ("T002", False)]
    assert acoes[0].descricao == "a"
    assert acoes[0].fase == "Fase 1, Preparação"
    # A PRIMEIRA linha da ação no log vence; sem linha, vale o started-at.
    assert acoes[0].criada_em == "2026-08-11T12:00:00Z"
    assert acoes[1].criada_em == "2026-08-10T09:00:00Z"


def test_demandas_sao_os_manuais_fora_de_done():
    manual = {"id": "99", "title": "Nova demanda", "category": "medico"}
    gerenciado = {"id": "hns:026", "title": "resumo", "category": "harness"}
    feito = {"id": "88", "title": "antiga"}
    files = _projeto()
    files[".vscode/vscode-kanban.json"] = _board(
        todo=[manual, gerenciado], done=[feito]
    )
    medicao, fs = _medir(files, config=_config_kanban())
    assert medicao.board_habilitado is True
    assert [(d.card_id, d.titulo, d.coluna) for d in medicao.demandas] == [
        ("99", "Nova demanda", "todo")
    ]
    assert medicao.falhas == []
    assert fs.writes == []


def test_board_ignorado_com_kanban_desligado():
    files = _projeto()
    files[".vscode/vscode-kanban.json"] = "{ ilegível de propósito"
    medicao, _ = _medir(files)
    assert medicao.board_habilitado is False
    assert medicao.demandas == []
    assert medicao.falhas == []


def test_board_ilegivel_e_falha_real():
    files = _projeto()
    files[".vscode/vscode-kanban.json"] = "{ quebrado"
    medicao, _ = _medir(files, config=_config_kanban())
    assert len(medicao.falhas) == 1
    assert "board ilegível" in medicao.falhas[0]


def test_board_ausente_com_kanban_habilitado_nao_e_falha():
    medicao, _ = _medir(_projeto(), config=_config_kanban())
    assert medicao.board_habilitado is True
    assert medicao.demandas == []
    assert medicao.falhas == []


def test_markdown_demandas_so_com_kanban_habilitado():
    files = _projeto()
    files[".vscode/vscode-kanban.json"] = _board(
        todo=[{"id": "99", "title": "Nova demanda"}]
    )
    com_kanban, _ = _medir(files, config=_config_kanban())
    md = render_markdown(com_kanban)
    assert "## Demandas do board" in md
    assert "Nova demanda" in md

    vazio, _ = _medir(_projeto(), config=_config_kanban())
    assert "- nenhuma" in render_markdown(vazio).split("## Demandas do board")[1]

    desligado, _ = _medir(_projeto())
    assert "Demandas do board" not in render_markdown(desligado)


def test_json_inclui_demandas():
    files = _projeto()
    files[".vscode/vscode-kanban.json"] = _board(
        todo=[{"id": "99", "title": "Nova demanda"}]
    )
    medicao, _ = _medir(files, config=_config_kanban())
    data = json.loads(render_json(medicao, "2026-08-11T12:00:00-03:00"))
    assert data["demandas"] == [
        {"card_id": "99", "titulo": "Nova demanda", "coluna": "todo"}
    ]
