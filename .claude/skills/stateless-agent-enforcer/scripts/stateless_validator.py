#!/usr/bin/env python3
"""
Stateless Architecture Validator

Scans Python code for violations of stateless architecture:
- Class instance variables storing conversation state
- Global dictionaries caching messages
- Session-based state management
- Unbounded caches

Usage:
    python stateless_validator.py <directory>
    python stateless_validator.py backend/app/agents

Exit codes:
    0: No violations
    1: Violations detected
"""

import ast
import sys
from pathlib import Path
from typing import List, Dict


class StatelessValidator(ast.NodeVisitor):
    """AST visitor to detect stateless architecture violations."""

    # Keywords that suggest conversation state
    STATE_KEYWORDS = [
        'conversation', 'message', 'history', 'cache',
        'state', 'session', 'context', 'memory'
    ]

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.violations = []

    def visit_ClassDef(self, node):
        """Check for instance variables that store conversation state."""
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == '__init__':
                self._check_init_method(node, item)

        self.generic_visit(node)

    def _check_init_method(self, class_node, init_node):
        """Check __init__ method for suspicious instance variables."""
        for stmt in init_node.body:
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Attribute):
                        attr_name = target.attr

                        # Check if instance variable name suggests state storage
                        if any(keyword in attr_name.lower()
                               for keyword in self.STATE_KEYWORDS):

                            # Check if it's a dict or list (common state containers)
                            if isinstance(stmt.value, (ast.Dict, ast.List)):
                                self.violations.append({
                                    'type': 'instance_variable',
                                    'severity': 'HIGH',
                                    'class': class_node.name,
                                    'variable': f'self.{attr_name}',
                                    'line': stmt.lineno,
                                    'message': (
                                        f'Instance variable "{attr_name}" appears to store '
                                        f'conversation state (violates stateless architecture)'
                                    )
                                })

    def visit_Assign(self, node):
        """Check for global dictionaries storing conversation state."""
        for target in node.targets:
            if isinstance(target, ast.Name):
                var_name = target.id

                # Check if global variable name suggests state storage
                if any(keyword in var_name.lower()
                       for keyword in self.STATE_KEYWORDS):

                    # Check if it's a dict (common state container)
                    if isinstance(node.value, ast.Dict):
                        self.violations.append({
                            'type': 'global_dict',
                            'severity': 'HIGH',
                            'variable': var_name,
                            'line': node.lineno,
                            'message': (
                                f'Global dictionary "{var_name}" appears to store '
                                f'conversation state (violates stateless architecture)'
                            )
                        })

        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        """Check for unbounded LRU caches."""
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Attribute):
                    if decorator.func.attr == 'lru_cache':
                        # Check if maxsize is None or not specified
                        has_maxsize = False
                        for keyword in decorator.keywords:
                            if keyword.arg == 'maxsize':
                                has_maxsize = True
                                if isinstance(keyword.value, ast.Constant):
                                    if keyword.value.value is None:
                                        self.violations.append({
                                            'type': 'unbounded_cache',
                                            'severity': 'MEDIUM',
                                            'function': node.name,
                                            'line': node.lineno,
                                            'message': (
                                                f'Function "{node.name}" uses unbounded '
                                                f'lru_cache (maxsize=None) - can grow '
                                                f'indefinitely and retain stale state'
                                            )
                                        })

                        if not has_maxsize:
                            self.violations.append({
                                'type': 'unbounded_cache',
                                'severity': 'MEDIUM',
                                'function': node.name,
                                'line': node.lineno,
                                'message': (
                                    f'Function "{node.name}" uses lru_cache without '
                                    f'maxsize - specify maxsize to prevent unbounded growth'
                                )
                            })

        self.generic_visit(node)


def validate_file(file_path: Path) -> List[Dict]:
    """Validate a Python file for stateless architecture compliance."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
    except Exception as e:
        print(f"Warning: Could not read {file_path}: {e}")
        return []

    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        print(f"Warning: Syntax error in {file_path}: {e}")
        return []

    validator = StatelessValidator(str(file_path))
    validator.visit(tree)

    return validator.violations


def validate_directory(directory: str) -> Dict:
    """Validate all Python files in directory."""
    path = Path(directory)

    if not path.exists():
        print(f"Error: Directory '{directory}' does not exist")
        sys.exit(1)

    all_violations = []
    file_count = 0

    for py_file in path.rglob('*.py'):
        # Skip __pycache__ and .venv directories
        if '__pycache__' in str(py_file) or '.venv' in str(py_file):
            continue

        file_count += 1
        violations = validate_file(py_file)

        if violations:
            all_violations.append({
                'file': str(py_file),
                'violations': violations
            })

    return {
        'total_files': file_count,
        'files_with_violations': len(all_violations),
        'violations': all_violations
    }


def print_results(results: Dict):
    """Print validation results in readable format."""
    if not results['violations']:
        print(f"✅ No stateless architecture violations detected")
        print(f"   Scanned {results['total_files']} Python files")
        return

    print("❌ Stateless architecture violations detected:\n")

    high_severity_count = 0
    medium_severity_count = 0

    for file_violations in results['violations']:
        print(f"📄 File: {file_violations['file']}")

        for violation in file_violations['violations']:
            severity = violation['severity']
            icon = "🔴" if severity == "HIGH" else "🟡"

            if severity == "HIGH":
                high_severity_count += 1
            else:
                medium_severity_count += 1

            print(f"  {icon} Line {violation['line']}: {violation['message']}")

        print()

    print(f"Summary:")
    print(f"  Files scanned: {results['total_files']}")
    print(f"  Files with violations: {results['files_with_violations']}")
    print(f"  High severity: {high_severity_count}")
    print(f"  Medium severity: {medium_severity_count}")
    print(f"\n⚠️  Fix these violations to ensure stateless architecture compliance")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python stateless_validator.py <directory>")
        print("Example: python stateless_validator.py backend/app/agents")
        sys.exit(1)

    directory = sys.argv[1]

    print(f"Validating stateless architecture in: {directory}\n")

    results = validate_directory(directory)
    print_results(results)

    # Exit with code 1 if violations detected
    if results['violations']:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
