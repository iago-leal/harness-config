import os
import re
import subprocess
from src.adapters.fs.local import LocalFileSystemAdapter
from src.adapters.git.subprocess import SubprocessGitAdapter
from src.adapters.process.formatter import HostFormatterAdapter


def test_local_file_system_adapter(tmp_path):
    adapter = LocalFileSystemAdapter()
    test_file = os.path.join(tmp_path, "test.txt")

    # Escrita normal
    adapter.write_file(test_file, "conteudo normal")
    assert adapter.exists(test_file)
    assert adapter.read_file(test_file) == "conteudo normal"

    # Escrita atômica
    adapter.write_file_atomic(test_file, "conteudo atomico")
    assert adapter.exists(test_file)
    assert adapter.read_file(test_file) == "conteudo atomico"

    # Listar dir e remoção
    files = adapter.list_dir(str(tmp_path))
    assert "test.txt" in files

    adapter.remove(test_file)
    assert not adapter.exists(test_file)


def test_subprocess_git_adapter(tmp_path):
    adapter = SubprocessGitAdapter()
    repo_path = str(tmp_path)

    # Repositório portável com um commit, para o rev-parse ter um HEAD.
    # (O teste anterior chumbava /Users/iagoleal/dev/harness e falhava no CI.)
    adapter.init_repo(repo_path)
    run = dict(cwd=repo_path, capture_output=True, check=True)
    subprocess.run(["git", "config", "user.email", "ci@example.com"], **run)
    subprocess.run(["git", "config", "user.name", "CI"], **run)
    subprocess.run(["git", "commit", "--allow-empty", "-m", "init"], **run)

    head_commit = adapter.get_head_commit(repo_path)
    assert len(head_commit) == 40
    assert re.match(r"^[a-f0-9]{40}$", head_commit)


def test_subprocess_git_adapter_init_repo(tmp_path):
    adapter = SubprocessGitAdapter()
    # init_repo deve criar um repositório git novo no diretório vazio.
    assert not os.path.exists(os.path.join(tmp_path, ".git"))
    adapter.init_repo(str(tmp_path))
    assert os.path.isdir(os.path.join(tmp_path, ".git"))


def test_subprocess_git_adapter_commit_paths_isola_arquivo(tmp_path):
    adapter = SubprocessGitAdapter()
    repo_path = str(tmp_path)

    adapter.init_repo(repo_path)
    run = dict(cwd=repo_path, capture_output=True, check=True)
    subprocess.run(["git", "config", "user.email", "ci@example.com"], **run)
    subprocess.run(["git", "config", "user.name", "CI"], **run)
    subprocess.run(["git", "commit", "--allow-empty", "-m", "trabalho"], **run)
    work_head = adapter.get_head_commit(repo_path)

    # Alvo a versionar + arquivo alheio que NÃO deve entrar no commit.
    with open(os.path.join(repo_path, "estado.md"), "w") as f:
        f.write("registro de encerramento\n")
    with open(os.path.join(repo_path, "OUTRO.md"), "w") as f:
        f.write("mudança pendente alheia\n")

    new_head = adapter.commit_paths(repo_path, ["estado.md"], "chore(sessao): encerrar")

    # Devolve o novo HEAD, por cima do commit de trabalho.
    assert re.match(r"^[a-f0-9]{40}$", new_head)
    assert new_head != work_head
    parent = subprocess.run(
        ["git", "rev-parse", "HEAD~1"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    assert parent == work_head

    # O commit contém EXCLUSIVAMENTE o alvo.
    names = subprocess.run(
        ["git", "show", "--name-only", "--pretty=format:", "HEAD"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()
    assert names == ["estado.md"]

    # O arquivo alheio permanece não rastreado, fora do commit.
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    assert "?? OUTRO.md" in status


def test_host_formatter_adapter_non_existent():
    adapter = HostFormatterAdapter()
    # Executa formatador inexistente e deve retornar 127 (command not found)
    exit_code, stdout, stderr = adapter.execute_formatter(
        formatter_name="nonexistent_formatter_cmd", file_path="dummy.txt"
    )
    assert exit_code == 127
    assert "não encontrado" in stderr


# --- Capacidades de fim de sessão (feature 014) ---------------------------


def _init_repo(adapter, path, branch="work"):
    """Repo git portável com identidade, um commit e nome de branch fixo."""
    adapter.init_repo(path)
    run = dict(cwd=path, capture_output=True, check=True)
    subprocess.run(["git", "config", "user.email", "ci@example.com"], **run)
    subprocess.run(["git", "config", "user.name", "CI"], **run)
    subprocess.run(["git", "commit", "--allow-empty", "-m", "init"], **run)
    subprocess.run(["git", "branch", "-M", branch], **run)


def test_get_current_branch(tmp_path):
    adapter = SubprocessGitAdapter()
    p = str(tmp_path)
    _init_repo(adapter, p, branch="feature-x")
    assert adapter.get_current_branch(p) == "feature-x"


def test_get_default_branch_fallback_sem_remoto(tmp_path):
    adapter = SubprocessGitAdapter()
    p = str(tmp_path)
    _init_repo(adapter, p, branch="main")
    # Sem remoto configurado: recai sobre main/master por existência de ref.
    assert adapter.get_default_branch(p) == "main"


def test_count_commits_ahead_sem_tracking_devolve_zero(tmp_path):
    adapter = SubprocessGitAdapter()
    p = str(tmp_path)
    _init_repo(adapter, p, branch="main")
    # Sem upstream tracking, @{u} é indefinido: 0 (não levanta).
    assert adapter.count_commits_ahead(p) == 0


def test_push_e_ahead_com_remoto_bare(tmp_path):
    adapter = SubprocessGitAdapter()
    remote = str(tmp_path / "remote.git")
    subprocess.run(["git", "init", "--bare", remote], capture_output=True, check=True)
    work = str(tmp_path / "work")
    os.makedirs(work)
    _init_repo(adapter, work, branch="main")
    run = dict(cwd=work, capture_output=True, check=True)
    subprocess.run(["git", "remote", "add", "origin", remote], **run)
    subprocess.run(["git", "push", "-u", "origin", "main"], **run)

    # Em dia com o tracking → 0 à frente.
    assert adapter.count_commits_ahead(work) == 0

    # Um commit local não publicado → 1 à frente.
    subprocess.run(["git", "commit", "--allow-empty", "-m", "c2"], **run)
    assert adapter.count_commits_ahead(work) == 1

    # push publica e zera o ahead, sem --force.
    adapter.push(work)
    assert adapter.count_commits_ahead(work) == 0


def test_get_file_at_ref(tmp_path):
    adapter = SubprocessGitAdapter()
    p = str(tmp_path)
    _init_repo(adapter, p, branch="main")
    with open(os.path.join(p, "v.txt"), "w") as f:
        f.write("conteudo-x")
    run = dict(cwd=p, capture_output=True, check=True)
    subprocess.run(["git", "add", "v.txt"], **run)
    subprocess.run(["git", "commit", "-m", "add v"], **run)

    assert "conteudo-x" in (adapter.get_file_at_ref(p, "HEAD", "v.txt") or "")
    # Arquivo ausente na ref → None (não levanta).
    assert adapter.get_file_at_ref(p, "HEAD", "naoexiste.txt") is None


def test_is_working_tree_clean(tmp_path):
    adapter = SubprocessGitAdapter()
    p = str(tmp_path)
    _init_repo(adapter, p, branch="main")
    assert adapter.is_working_tree_clean(p) is True
    with open(os.path.join(p, "new.txt"), "w") as f:
        f.write("z")
    assert adapter.is_working_tree_clean(p) is False


def test_merge_ff_only_aplica_e_recusa_divergencia(tmp_path):
    adapter = SubprocessGitAdapter()
    p = str(tmp_path)
    _init_repo(adapter, p, branch="main")
    run = dict(cwd=p, capture_output=True, check=True)
    subprocess.run(["git", "checkout", "-b", "feature"], **run)
    subprocess.run(["git", "commit", "--allow-empty", "-m", "c2"], **run)
    subprocess.run(["git", "checkout", "main"], **run)

    # main está estritamente atrás de feature → fast-forward aplica.
    assert adapter.merge_ff_only(p, "feature") is True

    # Diverge: novo commit em cada lado → não-FF, devolve False sem aplicar.
    subprocess.run(["git", "commit", "--allow-empty", "-m", "c3main"], **run)
    subprocess.run(["git", "checkout", "feature"], **run)
    subprocess.run(["git", "commit", "--allow-empty", "-m", "c3feat"], **run)
    subprocess.run(["git", "checkout", "main"], **run)
    assert adapter.merge_ff_only(p, "feature") is False
