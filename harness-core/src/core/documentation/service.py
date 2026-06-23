import json
import re
from typing import List, Dict, Any
from src.core.ports.fs import FileSystemPort


class DocumentationService:
    def __init__(self, fs: FileSystemPort):
        self.fs = fs

    def extract_commands(self, parser) -> List[Dict[str, Any]]:
        """
        Extrai programaticamente a ajuda dos comandos do parser argparse.
        """
        import argparse

        commands = []
        for action in parser._actions:
            if isinstance(action, argparse._SubParsersAction):
                # add_parser(help=...) guarda o texto na pseudo-ação do parser pai,
                # não em subparser.description. Mapeamos para usá-lo como fallback.
                help_by_name = {
                    ca.dest: ca.help for ca in action._choices_actions if ca.help
                }
                for choice, subparser in action.choices.items():
                    cmd_info = {
                        "name": choice,
                        "help": subparser.description
                        or help_by_name.get(choice)
                        or "Sem descrição.",
                        "arguments": [],
                    }
                    for subaction in subparser._actions:
                        if subaction.dest == "help":
                            continue
                        cmd_info["arguments"].append(
                            {
                                "flags": subaction.option_strings,
                                "help": subaction.help or "Sem descrição.",
                                "required": subaction.required,
                                "default": subaction.default,
                            }
                        )
                    commands.append(cmd_info)
        return commands

    def parse_markdown_rules(self, domain_filepath: str) -> List[Dict[str, Any]]:
        """
        Extrai as Regras de Negócio de domain.md.
        """
        rules = []
        if not self.fs.exists(domain_filepath):
            return rules

        content = self.fs.read_file(domain_filepath)
        # Encontra seções de regras de negócio em domain.md
        # Geralmente listadas como "RN-XX"
        matches = re.finditer(
            r"\*\*(RN-\d+):\s*([^*]+)\*\*\s*([^\n🟢🟡🔴]*)\s*([🟢🟡🔴])", content
        )
        for m in matches:
            rules.append(
                {
                    "id": m.group(1).strip(),
                    "title": m.group(2).strip(),
                    "details": m.group(3).strip(),
                    "confidence": m.group(4).strip(),
                }
            )
        return rules

    def load_checkpoints(self, state_filepath: str) -> Dict[str, Any]:
        """
        Carrega o estado dos checkpoints do Reversa a partir do state.json.
        """
        if not self.fs.exists(state_filepath):
            return {}
        try:
            content = self.fs.read_file(state_filepath)
            return json.loads(content)
        except Exception:
            return {}

    def generate_html(
        self,
        parser,
        template_path: str,
        domain_path: str,
        state_path: str,
        output_path: str,
    ) -> None:
        """
        Compila todos os metadados no template HTML e gera o arquivo final de documentação.
        """
        if not self.fs.exists(template_path):
            raise FileNotFoundError(f"Template não encontrado: {template_path}")

        template = self.fs.read_file(template_path)

        commands = self.extract_commands(parser)
        rules = self.parse_markdown_rules(domain_path)
        state_data = self.load_checkpoints(state_path)

        # Injeta variáveis estruturadas no HTML via JSON
        injected_data = {"commands": commands, "rules": rules, "state": state_data}

        json_data = json.dumps(injected_data, ensure_ascii=False, indent=2)

        # Substitui o placeholder no template
        final_html = template.replace(
            "/* INJECTED_DATA_PLACEHOLDER */", f"const HARNESS_DOC_DATA = {json_data};"
        )

        self.fs.write_file_atomic(output_path, final_html)
