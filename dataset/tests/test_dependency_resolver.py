import pytest
from solution import resolve_order


def is_valid_order(order, tasks):
    """Check that all dependencies appear before each task."""
    pos = {task: i for i, task in enumerate(order)}
    for task, deps in tasks.items():
        for dep in deps:
            if pos[dep] >= pos[task]:
                return False
    return True


def test_linear_chain():
    tasks = {"a": [], "b": ["a"], "c": ["b"]}
    order = resolve_order(tasks)
    assert order == ["a", "b", "c"] or is_valid_order(order, tasks)


def test_no_dependencies():
    tasks = {"x": [], "y": [], "z": []}
    order = resolve_order(tasks)
    assert set(order) == {"x", "y", "z"}


def test_diamond_dependency():
    tasks = {"a": [], "b": ["a"], "c": ["a"], "d": ["b", "c"]}
    order = resolve_order(tasks)
    assert set(order) == {"a", "b", "c", "d"}
    assert is_valid_order(order, tasks)


def test_single_task_no_deps():
    assert resolve_order({"only": []}) == ["only"]


def test_cycle_raises():
    tasks = {"a": ["b"], "b": ["c"], "c": ["a"]}
    with pytest.raises(ValueError, match="cycle"):
        resolve_order(tasks)


def test_self_loop_raises():
    tasks = {"a": ["a"]}
    with pytest.raises(ValueError, match="cycle"):
        resolve_order(tasks)


def test_complex_graph():
    tasks = {
        "build": [],
        "test": ["build"],
        "lint": ["build"],
        "package": ["test", "lint"],
        "deploy": ["package"],
    }
    order = resolve_order(tasks)
    assert set(order) == set(tasks.keys())
    assert is_valid_order(order, tasks)


def test_empty():
    assert resolve_order({}) == []


def test_all_tasks_present_in_output():
    tasks = {"a": [], "b": ["a"], "c": ["a"], "d": ["b"]}
    order = resolve_order(tasks)
    assert set(order) == set(tasks.keys())
    assert len(order) == len(tasks)
