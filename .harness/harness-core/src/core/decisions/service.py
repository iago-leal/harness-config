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
            # Extrai o título do H1
            title = dec.id
            if dec.raw_content:
                h1_match = re.search(r"^#\s+MD-\d{4}\s+—\s+(.*)", dec.raw_content, re.MULTILINE)
                if h1_match:
                    title = h1_match.group(1).strip()
            
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

        # 4. Gravação atômica no arquivo de saída
        self.fs.write_file_atomic(output_filepath, consolidated_content)
