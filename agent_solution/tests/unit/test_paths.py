from agent_solution.core.paths import project_root


def test_project_root_contains_readme() -> None:
    assert (project_root() / "README.md").is_file()
