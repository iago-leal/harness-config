import os
import re
import yaml

class LegacyDecisionImporter:
    @staticmethod
    def import_file(source_path: str, target_dir: str) -> str:
        """
        Importa um arquivo de decisão legado MD-*.md, convertendo-o para o novo formato com YAML Front-matter.
        Retorna o caminho do arquivo criado.
        """
        filename = os.path.basename(source_path)
        if not filename.startswith("MD-") or not filename.endswith(".md"):
            raise ValueError(f"Nome de arquivo inválido: {filename}")

        with open(source_path, 'r', encoding='utf-8') as f:
            content = f.read()

        lines = content.splitlines()
        
        # 1. Identificar ID
        id_match = re.search(r"^#\s+(MD-\d{4})", lines[0])
        if not id_match:
            raise ValueError(f"ID não identificado na primeira linha de {filename}")
        decision_id = id_match.group(1)

        # 2. Identificar Gancho e Relações
        gancho = None
        relations = []
        body_start_line = 1

        for i, line in enumerate(lines[1:], start=1):
            stripped_line = line.strip()
            if not stripped_line:
                continue

            if not stripped_line.startswith(">"):
                body_start_line = i
                break

            # Procura por Gancho
            gancho_match = re.search(r"\*\*Gancho:?\*\*:?\s*(.*)", stripped_line, re.IGNORECASE)
            if gancho_match:
                gancho = gancho_match.group(1).strip()
                body_start_line = i + 1
                continue

            # Procura por Relações
            relations_match = re.search(r"\*\*Relações:?\*\*:?\s*(.*)", stripped_line, re.IGNORECASE)
            if relations_match:
                relations_str = relations_match.group(1).strip()
                # Pode haver múltiplas relações separadas por vírgula ou ponto-e-vírgula
                for rel in re.split(r"[,;]\s*", relations_str):
                    rel = rel.strip()
                    if not rel:
                        continue
                    tokens = rel.split()
                    if len(tokens) != 2:
                        raise ValueError(f"Relação malformada '{rel}' em {filename} (deve ter exatamente 2 tokens)")
                    relations.append(rel)
                body_start_line = i + 1
                continue

        if not gancho:
            raise ValueError(f"Campo 'Gancho' obrigatório não encontrado em {filename}")

        # 3. Identificar Estado
        estado = "ativo"
        # Varre o resto do arquivo procurando pelo Estado
        for line in lines[body_start_line:]:
            estado_match = re.search(r"-\s+\*\*ESTADO\*\*:\s*(.*)", line, re.IGNORECASE)
            if estado_match:
                estado_text = estado_match.group(1).lower()
                if "descartado" in estado_text or "descartada" in estado_text:
                    estado = "descartado"
                break

        # 4. Montar o Front-matter YAML
        front_matter = {
            "id": decision_id,
            "gancho": gancho,
            "relacoes": relations,
            "estado": estado
        }

        yaml_block = yaml.dump(front_matter, allow_unicode=True, default_flow_style=False)
        
        # Pegar o H1 original e o corpo, pulando as linhas de metadados legados
        new_content_lines = [
            "---",
            yaml_block.rstrip(),
            "---",
            "",
            lines[0], # H1 original
        ]
        
        # Adicionar o corpo, pulando linhas vazias extras logo após os metadados
        body_lines = lines[body_start_line:]
        while body_lines and not body_lines[0].strip():
            body_lines.pop(0)
            
        new_content_lines.extend(body_lines)
        
        # Gravar no destino
        os.makedirs(target_dir, exist_ok=True)
        target_path = os.path.join(target_dir, filename)
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(new_content_lines) + "\n")

        return target_path

    @classmethod
    def import_directory(cls, source_dir: str, target_dir: str) -> int:
        """
        Varre o diretório legado e importa todos os arquivos MD-*.md.
        Retorna o total de arquivos importados.
        """
        if not os.path.exists(source_dir):
            raise FileNotFoundError(f"Diretório de origem não existe: {source_dir}")

        count = 0
        for filename in sorted(os.listdir(source_dir)):
            if filename.startswith("MD-") and filename.endswith(".md"):
                source_path = os.path.join(source_dir, filename)
                cls.import_file(source_path, target_dir)
                count += 1

        return count
