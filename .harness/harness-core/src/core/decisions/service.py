import os
import re
import yaml
from typing import List, Dict, Tuple, Optional
from src.core.ports.fs import FileSystemPort
from src.core.domain.models import Decision, Relationship

class DecisionService:
    def __init__(self, fs: FileSystemPort):
        self.fs = fs

    def load_decisions(self, directory: str) -> List[Decision]:
        """
        Carrega todas as microdecisões MD-*.md de um diretório e faz o parse do Front-matter YAML.
        """
        decisions = []
        if not self.fs.exists(directory):
            return decisions

        for filename in sorted(self.fs.list_dir(directory)):
            if filename.startswith("MD-") and filename.endswith(".md"):
                filepath = os.path.join(directory, filename)
                raw_content = self.fs.read_file(filepath)
                
                # Parse do Front-matter YAML
                # O front-matter é delimitado por '---' no topo
                parts = raw_content.split("---", 2)
                if len(parts) >= 3:
                    yaml_content = parts[1].strip()
                    try:
                        metadata = yaml.safe_load(yaml_content) or {}
                    except Exception as e:
                        raise ValueError(f"Falha ao ler YAML Front-matter em {filename}: {e}")
                    
                    decision_id = metadata.get("id")
                    gancho = metadata.get("gancho")
                    status = metadata.get("estado", "ativo")
                    
                    relationships = []
                    for rel_str in metadata.get("relacoes", []):
                        tokens = rel_str.strip().split()
                        if len(tokens) == 2:
                            relationships.append(Relationship(rel_type=tokens[0], target_id=tokens[1]))
                    
                    decisions.append(Decision(
                        id=decision_id,
                        gancho=gancho,
                        status=status,
                        relationships=relationships,
                        filepath=filepath,
                        raw_content=raw_content
                    ))
                else:
                    raise ValueError(f"Front-matter YAML não encontrado no arquivo {filename}")
                    
        return decisions

    def validate_integrity(self, decisions: List[Decision]) -> List[str]:
        """
        Valida a consistência individual de cada decisão e a integridade de referências no grafo.
        """
        errors = []
        decision_map: Dict[str, Decision] = {d.id: d for d in decisions}

        for dec in decisions:
            # 1. Validações individuais do conteúdo
            individual_errors = dec.validate_integrity()
            for err in individual_errors:
                errors.append(f"[{dec.id}] {err}")

            # 2. Validações de Grafo/Arestas
            for rel in dec.relationships:
                # Auto-relação
                if rel.target_id == dec.id:
                    errors.append(f"[{dec.id}] Auto-relação inválida apontando para si mesma.")
                # Aresta órfã (destino não existe)
                elif rel.target_id not in decision_map:
                    errors.append(f"[{dec.id}] Referência órfã apontando para {rel.target_id} que não existe.")

        return errors

    @staticmethod
    def _extract_title(dec: Decision) -> str:
        """Extrai o título do H1 da ficha — ponto ÚNICO compartilhado pelo
        índice completo e pela visão compacta (028/D-03: uma divergência de
        formato entre as duas visões seria bug de fonte dupla)."""
        title = dec.id
        if dec.raw_content:
            h1_match = re.search(r"^#\s+MD-\d{4}\s+—\s+(.*)", dec.raw_content, re.MULTILINE)
            if h1_match:
                title = h1_match.group(1).strip()
        return title

    def _write_if_changed(self, filepath: str, content: str) -> bool:
        """Escrita condicionada a mudança (028/D-05, padrão 026/027): artefato
        derivado só é regravado quando os bytes diferem — sem mudança nas
        fichas, nem o mtime se move."""
        if self.fs.exists(filepath) and self.fs.read_file(filepath) == content:
            return False
        self.fs.write_file_atomic(filepath, content)
        return True

    def derive_views_for_close(self, config, err) -> List[str]:
        """Deriva índice completo + visão compacta com a semântica da borda de
        encerramento (MD-0025/MD-0026, RN-N56) — fonte única compartilhada pelo
        ``SessionCloseFlow`` e pela borda MCP ``session_command``.

        Estritamente não-bloqueante: erro de integridade ou falha interna vira
        chamada a ``err`` e o encerramento segue. Com o grafo inválido, as
        visões NÃO são regravadas (semântica da CLI menos o abort): visão
        derivada de acervo quebrado seria pior que visão velha. Sem fichas,
        sem derivação: o init cria ``decisions.dir`` em todo projeto, então o
        critério é o acervo vazio — projeto que nunca registrou decisão não
        ganha visões inventadas no fechamento.

        Devolve os caminhos das visões derivadas (para a borda incluí-los no
        commit de encerramento) ou lista vazia quando a derivação foi pulada.
        """
        try:
            decisions = self.load_decisions(config.decisions.dir)
            if not decisions:
                return []
            errors = self.validate_integrity(decisions)
            if errors:
                err(
                    "Aviso: visões de decisões não derivadas no encerramento "
                    "(erros de integridade no grafo):"
                )
                for e in errors:
                    err(f" - {e}")
                return []
            self.compile_index(
                decisions, config.decisions.index_file, config.decisions.header_file
            )
            self.compile_compact_view(
                decisions,
                config.decisions.compact_file,
                config.decisions.index_file,
                config.decisions.dir,
                config.decisions.compact_index_size,
            )
            return [config.decisions.index_file, config.decisions.compact_file]
        except Exception as exc:
            err(
                "Aviso: derivação das visões de decisões falhou "
                f"(não-bloqueante): {exc}"
            )
            return []

    def compile_compact_view(
        self,
        decisions: List[Decision],
        output_filepath: str,
        index_file: str,
        decisions_dir: str,
        max_items: int,
    ) -> None:
        """Deriva a visão compacta do acervo (feature 028): as `max_items`
        fichas mais recentes por ID (a mais nova primeiro), só títulos, mais a
        contagem total e os ponteiros de consulta sob demanda. É esta visão que
        o `cmd resume` injeta no SessionStart; o índice completo fica a um passo
        de leitura. `max_items = 0` degrada para cabeçalho + contagem + ponteiros.
        """
        n = len(decisions)
        plural = "ficha" if n == 1 else "fichas"
        lines = [
            "# Decisões recentes",
            "",
            "> Visão DERIVADA por `./harness decisions` (hook Stop). Não edite à mão.",
            f"> Acervo completo: índice em `{index_file}`; fichas em `{decisions_dir}/MD-NNNN.md`.",
            "> Antes de buscas amplas, ou antes de redecidir algo, consulte o índice completo.",
            "",
            f"Total: {n} {plural}",
        ]
        recentes = sorted(decisions, key=lambda d: d.id or "", reverse=True)[:max_items]
        if recentes:
            lines.append("")
            for dec in recentes:
                lines.append(f"- **{dec.id}** — {self._extract_title(dec)}")
        self._write_if_changed(output_filepath, "\n".join(lines) + "\n")

    def compile_index(self, decisions: List[Decision], output_filepath: str, header_filepath: Optional[str] = None) -> None:
        """
        Deriva os backlinks e compila o índice consolidado microdecisoes.md.
        """
        # Dicionário de inverso de relações
        inverso_verbos = {
            "refina": "refinado-por",
            "depende-de": "requerido-por",
            "estende": "estendido-por",
            "substitui": "substituído-por",
            "relaciona": "relacionado-com",
            "bloqueia": "bloqueado-por"
        }

        # 1. Mapear backlinks
        # backlinks[target_id] = list of (verbo_inverso, source_id)
        backlinks: Dict[str, List[Tuple[str, str]]] = {d.id: [] for d in decisions}
        for dec in decisions:
            for rel in dec.relationships:
                if rel.target_id in backlinks:
                    verbo_inv = inverso_verbos.get(rel.rel_type, f"inverso-de-{rel.rel_type}")
                    backlinks[rel.target_id].append((verbo_inv, dec.id))

        # 2. Ler cabeçalho se fornecido
        header_content = ""
        if header_filepath and self.fs.exists(header_filepath):
            header_content = self.fs.read_file(header_filepath).strip() + "\n\n"

        # 3. Gerar a lista de decisões formatadas
        index_lines = []
        for dec in decisions:
            title = self._extract_title(dec)

            # Montar relações de saída
            saidas = []
            for rel in dec.relationships:
                saidas.append(f"{rel.rel_type} {rel.target_id}")

            # Montar backlinks de entrada
            entradas = []
            # Ordena backlinks por ID de origem para manter determinismo
            for verbo_inv, src_id in sorted(backlinks.get(dec.id, []), key=lambda x: x[1]):
                entradas.append(f"{verbo_inv} {src_id}")

            # Formata a sub-linha de relacionamento: ↳ [saídas] · [entradas]
            rel_parts = []
            if saidas:
                rel_parts.append(", ".join(saidas))
            if entradas:
                rel_parts.append(" · ".join(entradas))

            sub_line = ""
            if rel_parts:
                sub_line = f"\n  ↳ { ' · '.join(rel_parts) }"

            index_lines.append(f"- **{dec.id}** — {title}{sub_line}")

        consolidated_content = header_content + "\n".join(index_lines) + "\n"

        # 4. Gravação atômica, condicionada a mudança (028/D-05).
        self._write_if_changed(output_filepath, consolidated_content)
