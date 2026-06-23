import os
import argparse
from src.core.ports.fs import FileSystemPort
from src.core.install.harness_profiles import get_profile


class InstallPromptService:
    """Renderiza o prompt de instalação colável no agente.

    O texto é derivado por composição — template estático, bloco de ganchos do
    perfil do harness ativo e a superfície da CLI obtida por introspecção do
    argparse — de modo que nada é mantido à mão em paralelo (fonte única).
    """

    def __init__(self, fs: FileSystemPort):
        self.fs = fs
        self._template_path = os.path.join(os.path.dirname(__file__), "template.md")

    def render(self, active_harness: str, parser: argparse.ArgumentParser) -> str:
        # Resolve o perfil primeiro: harness inválido falha antes de qualquer I/O.
        profile = get_profile(active_harness)
        template = self.fs.read_file(self._template_path)
        return (
            template.replace("{{ACTIVE_HARNESS}}", active_harness)
            .replace("{{APPLY_HOOKS}}", profile.apply_instructions())
            .replace("{{HOOKS_BLOCK}}", profile.hooks_block())
            .replace("{{COMMANDS}}", self._introspect_commands(parser))
        )

    @staticmethod
    def _introspect_commands(parser: argparse.ArgumentParser) -> str:
        """Lista os subcomandos da CLI por introspecção do argparse.

        Reaproveita o padrão de `DocumentationService.extract_commands`, mantendo
        o prompt sincronizado com a CLI real.
        """
        lines = []
        for action in parser._actions:
            if isinstance(action, argparse._SubParsersAction):
                for name, sub in action.choices.items():
                    help_text = (sub.description or "").strip()
                    lines.append(
                        f"- `{name}` — {help_text}" if help_text else f"- `{name}`"
                    )
        return "\n".join(lines)
