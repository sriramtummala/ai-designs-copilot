from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATHS = [
    "package.json",
    "pnpm-workspace.yaml",
    "nx.json",
    "apps/web/project.json",
    "apps/api/project.json",
    "libs/ui/project.json",
    "libs/tokens/project.json",
    "libs/compliance/project.json",
    "libs/cms-adapter/project.json",
    "libs/ai-workflows/project.json",
    "docs/problem-statement.md",
    "docs/architecture-v1.md"
]
 
EXPECTED_PROJECTS = {
    "web": "application",
    "api": "application",
    "ui": "library",
    "tokens": "library",
    "compliance": "library",
    "cms-adapter": "library",
    "ai-workflows": "library",
}
 
errors = []
for relative_path in REQUIRED_PATHS:
    if not (ROOT / relative_path).exists():
        errors.append(f"Missing required path: {relative_path}")
 
for relative_path in [
    "apps/web/project.json",
    "apps/api/project.json",
    "libs/ui/project.json",
    "libs/tokens/project.json",
    "libs/compliance/project.json",
    "libs/cms-adapter/project.json",
    "libs/ai-workflows/project.json",
]:
    path = ROOT / relative_path
    if not path.exists():
        continue
    data = json.loads(path.read_text())
    name = data.get("name")
    project_type = data.get("projectType")
    if name not in EXPECTED_PROJECTS:
        errors.append(f"Unexpected project name in {relative_path}: {name}")
    elif EXPECTED_PROJECTS[name] != project_type:
        errors.append(
            f"Project {name} should be {EXPECTED_PROJECTS[name]}, got {project_type}"
        )
    if not data.get("tags"):
        errors.append(f"Project {name} should have boundary tags")
    for target in ["lint", "test", "build"]:
        if target not in data.get("targets", {}):
            errors.append(f"Project {name} missing target: {target}")
 
if errors:
    print("Workspace validation failed:")
    for error in errors:
        print(f"- {error}")
    sys.exit(1)
 
print("Workspace validation passed.")
print(f"Validated {len(EXPECTED_PROJECTS)} projects with required targets and tags.")
