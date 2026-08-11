"""Renderizadores da ``Medicao`` (feature 026).

``render_markdown`` produz o artefato derivado versionado: SEM timestamp de
geração nem qualquer valor volátil (RN-02 — o diff só existe quando o estado
muda) e sem caminhos absolutos da máquina. ``render_json`` produz a medição
para máquina no stdout; ``aferido_em`` é injetado pela borda, permitido
porque stdout não é versionado.
"""

import json


def _abreviar(commit: str) -> str:
    return commit[:7]


def _nome(feature) -> str:
    if feature.short_name:
        return f"{feature.feature_id}-{feature.short_name}"
    return feature.feature_id


def render_markdown(medicao) -> str:
    linhas = [
        "# Progresso do projeto",
        "",
        "> Artefato derivado; não edite. Toda linha é recomputada das fontes;",
        "> regenere com `./harness progress`.",
        "",
        "## Ciclo forward",
        "",
    ]

    if not medicao.forward_disponivel:
        linhas.append(
            "- n/a (sem `.reversa/active-requirements.json`; projeto sem ciclo "
            "forward do Reversa)"
        )
    else:
        ativa = medicao.ativa
        if ativa:
            linhas.append(
                f"- Feature ativa: `{_nome(ativa)}` (estágio físico: "
                f"{ativa.estagio_fisico}; ações: {ativa.feitas}/{ativa.total})"
            )
            if ativa.fases:
                linhas.extend(["", "| Fase | Concluídas | Total |", "|------|------------|-------|"])
                for fase in ativa.fases:
                    linhas.append(f"| {fase.fase} | {fase.feitas} | {fase.total} |")
                linhas.append("")
        else:
            linhas.append("- Feature ativa: nenhuma")
        linhas.append(f"- Features pausadas: {len(medicao.pausadas)}")
        for pausada in medicao.pausadas:
            pausada_em = pausada.estagio_declarado or pausada.estagio_fisico
            linhas.append(
                f"  - `{_nome(pausada)}` (pausada em: {pausada_em}; "
                f"ações: {pausada.feitas}/{pausada.total})"
            )
        linhas.append(f"- Features concluídas: {medicao.concluidas}")
        if medicao.outras_incompletas:
            linhas.append(
                f"- Outras não concluídas (sem registro ativo): "
                f"{medicao.outras_incompletas}"
            )

    linhas.extend(["", "## Harness", ""])
    harness = medicao.harness
    if harness.sessao_status == "n/a":
        linhas.append("- Sessão: n/a (sem estado de sessão)")
    else:
        linhas.append(
            f"- Sessão: {harness.sessao_status} (âncora: `{_abreviar(harness.ancora)}`)"
        )
    fichas = f"- Microdecisões: {harness.fichas_total} fichas"
    if harness.ultima_ficha:
        fichas += f" (última: {harness.ultima_ficha})"
    linhas.append(fichas)
    if harness.gate_pendente is None:
        linhas.append("- Registro de decisão pendente: n/a")
    elif harness.gate_pendente:
        linhas.append(
            f"- Registro de decisão pendente: sim ({harness.gate_mudancas} "
            "mudanças sem ficha)"
        )
    else:
        linhas.append("- Registro de decisão pendente: não")

    # Seção só existe com o kanban habilitado (opt-in da 027): projetos sem
    # board não ganham ruído novo no artefato.
    if medicao.board_habilitado:
        linhas.extend(["", "## Demandas do board", ""])
        if medicao.demandas:
            for demanda in medicao.demandas:
                linhas.append(
                    f"- `{demanda.card_id}` [{demanda.coluna}] {demanda.titulo}"
                )
        else:
            linhas.append("- nenhuma")

    linhas.extend(["", "## Alertas", ""])
    if medicao.alertas:
        for alerta in medicao.alertas:
            linhas.append(f"- [{alerta.severidade}] {alerta.origem}: {alerta.mensagem}")
    else:
        linhas.append("- nenhum")
    linhas.append("")
    return "\n".join(linhas)


def render_json(medicao, aferido_em: str) -> str:
    data = {"aferido_em": aferido_em}
    data.update(medicao.model_dump())
    return json.dumps(data, ensure_ascii=False, indent=2)
