import json
from pathlib import Path
from unittest import mock

import pytest

from agent.repo_migrate import run_migrate_java_path

@pytest.fixture
def mock_codegen():
    with mock.patch("agent.repo_migrate.codegen_generate") as mock_gen, \
         mock.patch("agent.repo_utils.add_python_comments", side_effect=lambda c: c):
        # Return a simple valid python code
        mock_gen.return_value = "class MockedClass:\n    pass\n"
        yield mock_gen

def test_repo_migrate_single_file(tmp_path: Path, mock_codegen):
    java_file = tmp_path / "Main.java"
    java_file.write_text("public class Main {}", encoding="utf-8")
    
    result = run_migrate_java_path(str(java_file))
    
    assert "Done" in result["status"]
    
    # Check if .py was created
    py_file = tmp_path / "Main.py"
    assert py_file.exists()
    assert py_file.read_text(encoding="utf-8") == "class MockedClass:\n    pass\n"
    
    # Check trace
    traces = [t["step"] for t in result.get("trace", [])]
    assert "generate" in traces
    assert "validate" in traces
    assert "write" in traces

def test_repo_migrate_folder_main_and_test(tmp_path: Path, mock_codegen):
    # Setup src/main/java and src/test/java
    main_dir = tmp_path / "src" / "main" / "java" / "com" / "example"
    test_dir = tmp_path / "src" / "test" / "java" / "com" / "example"
    main_dir.mkdir(parents=True)
    test_dir.mkdir(parents=True)
    
    (main_dir / "App.java").write_text("package com.example; public class App {}", encoding="utf-8")
    (main_dir / "Util.java").write_text("package com.example; public class Util {}", encoding="utf-8")
    (test_dir / "AppTest.java").write_text("package com.example; public class AppTest {}", encoding="utf-8")
    
    # Run migrate on src/
    result = run_migrate_java_path(str(tmp_path / "src"), max_files=10)
    
    written = result.get("written_paths", [])
    assert len(written) == 3
    
    assert (main_dir / "App.py").exists()
    assert (main_dir / "Util.py").exists()
    assert (test_dir / "AppTest.py").exists()

def test_repo_migrate_dependency_awareness(tmp_path: Path, mock_codegen):
    # Setup two files where one uses the other
    main_dir = tmp_path / "src" / "main" / "java" / "com" / "example"
    main_dir.mkdir(parents=True)
    
    (main_dir / "Logger.java").write_text("public class Logger { public void log() {} }", encoding="utf-8")
    
    # App uses Logger
    app_code = "import com.example.Logger;\npublic class App { Logger logger; }"
    app_file = main_dir / "App.java"
    app_file.write_text(app_code, encoding="utf-8")
    
    # Run only on App.java
    result = run_migrate_java_path(str(app_file))
    
    # Check trace for read_dep
    dep_reads = [t["detail"] for t in result.get("trace", []) if t["step"] == "read_dep"]
    assert any("Logger.java" in d for d in dep_reads)
    
    # Assert App.py was created
    assert (main_dir / "App.py").exists()

def test_repo_migrate_validation_fix_loop(tmp_path: Path):
    java_file = tmp_path / "Bad.java"
    java_file.write_text("public class Bad {}", encoding="utf-8")
    
    # Mock codegen to return bad python first, then good python
    # We need to mock codegen_generate AND fix_python
    
    with mock.patch("agent.repo_migrate.codegen_generate") as mock_gen, \
         mock.patch("agent.repo_migrate.fix_python") as mock_fix, \
         mock.patch("agent.repo_utils.add_python_comments", side_effect=lambda c: c):
        
        # First attempt produces bad syntax
        mock_gen.return_value = "class Bad { " # Syntax error
        
        # Fix attempt produces good syntax
        mock_fix.return_value = {"python_code": "class Bad:\n    pass\n", "trace": [{"step": "fix", "detail": "Fixed"}]}
        
        result = run_migrate_java_path(str(java_file), max_retries=1)
        
        traces = [t["step"] for t in result.get("trace", [])]
        assert "validate_fail" in traces
        assert "fix" in traces
        assert "validate" in traces # Passed on attempt 2
        
        assert (tmp_path / "Bad.py").exists()
        assert (tmp_path / "Bad.py").read_text(encoding="utf-8") == "class Bad:\n    pass\n"
