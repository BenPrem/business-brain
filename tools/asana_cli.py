#!/usr/bin/env python3
"""
asana_cli.py — small task-system CLI (Asana is the worked example).

Stdlib-only. Reads ASANA_TOKEN from the environment or a repo-root .env.
The token is used in request headers only — it is NEVER printed, logged,
or echoed back, and no command exists that would output it.

Setup (see guides/connecting-tools.md):
    - Create a scoped Personal Access Token in Asana developer settings.
    - Put it in .env at the repo root as ASANA_TOKEN=... (the file is gitignored).
    - Optionally set ASANA_WORKSPACE_GID and ASANA_DEFAULT_PROJECT_GID in .env so
      you don't have to pass --workspace/--project on every call. Discover the
      GIDs with the `workspaces` and `projects` commands — they are IDs, not
      secrets, but they are still business-identifying, so keep them out of
      public forks.

Usage:
    python3 tools/asana_cli.py me
    python3 tools/asana_cli.py workspaces
    python3 tools/asana_cli.py projects [--workspace GID] [--find NAME]
    python3 tools/asana_cli.py tasks --project GID [--include-completed]
    python3 tools/asana_cli.py create-task --project GID --name "..." [--notes ...] [--due-on YYYY-MM-DD]
    python3 tools/asana_cli.py move --task GID --section GID
    python3 tools/asana_cli.py comment --task GID --message "..."
    python3 tools/asana_cli.py complete --task GID
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


API_BASE = "https://app.asana.com/api/1.0"


def load_env(path=None):
    """Load KEY=value lines from the repo-root .env into os.environ (no override)."""
    if path is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def token():
    value = os.environ.get("ASANA_TOKEN")
    if not value:
        print("ERROR: ASANA_TOKEN is not set (add it to .env — see guides/connecting-tools.md)", file=sys.stderr)
        sys.exit(1)
    return value


def request(method, path, params=None, data=None):
    url = f"{API_BASE}{path}"
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"

    body = None
    headers = {
        "Authorization": f"Bearer {token()}",
        "Accept": "application/json",
    }
    if data is not None:
        body = json.dumps({"data": data}).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = resp.read().decode("utf-8")
            return json.loads(payload) if payload else {}
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        # API error bodies never contain the token; safe to surface.
        print(f"ERROR: Asana API {e.code}: {detail}", file=sys.stderr)
        sys.exit(1)


def print_rows(rows, fields):
    for row in rows:
        print(" | ".join(str(row.get(field, "")) for field in fields))


def _require_workspace(args):
    workspace = getattr(args, "workspace", None) or os.environ.get("ASANA_WORKSPACE_GID")
    if not workspace:
        print("ERROR: pass --workspace or set ASANA_WORKSPACE_GID in .env", file=sys.stderr)
        sys.exit(1)
    return workspace


def _require_project(args):
    project = getattr(args, "project", None) or os.environ.get("ASANA_DEFAULT_PROJECT_GID")
    if not project:
        print("ERROR: pass --project or set ASANA_DEFAULT_PROJECT_GID in .env", file=sys.stderr)
        sys.exit(1)
    return project


def cmd_me(_args):
    data = request("GET", "/users/me").get("data", {})
    print(json.dumps({
        "gid": data.get("gid"),
        "name": data.get("name"),
        "email": data.get("email"),
    }, indent=2))


def cmd_workspaces(_args):
    rows = request("GET", "/workspaces", {"opt_fields": "gid,name"}).get("data", [])
    print_rows(rows, ["gid", "name"])


def cmd_projects(args):
    workspace = _require_workspace(args)
    params = {
        "workspace": workspace,
        "archived": "false",
        "limit": 100,
        "opt_fields": "gid,name,archived,team.name,permalink_url",
    }
    rows = request("GET", "/projects", params).get("data", [])
    if args.find:
        needle = args.find.lower()
        rows = [p for p in rows if needle in p.get("name", "").lower()]
    for row in rows:
        team = (row.get("team") or {}).get("name", "")
        print(f"{row.get('gid')} | {row.get('name')} | {team} | {row.get('permalink_url')}")


def cmd_teams(args):
    workspace = _require_workspace(args)
    rows = request("GET", f"/workspaces/{workspace}/teams", {"opt_fields": "gid,name"}).get("data", [])
    print_rows(rows, ["gid", "name"])


def cmd_create_project(args):
    workspace = _require_workspace(args)
    data = {
        "name": args.name,
        "workspace": workspace,
    }
    if args.team:
        data["team"] = args.team
    project = request("POST", "/projects", data=data).get("data", {})
    print(f"{project.get('gid')} | {project.get('name')} | {project.get('permalink_url')}")


def cmd_sections(args):
    project = _require_project(args)
    rows = request("GET", f"/projects/{project}/sections", {"opt_fields": "gid,name"}).get("data", [])
    print_rows(rows, ["gid", "name"])


def cmd_create_section(args):
    project = _require_project(args)
    section = request("POST", f"/projects/{project}/sections", data={"name": args.name}).get("data", {})
    print(f"{section.get('gid')} | {section.get('name')}")


def cmd_tasks(args):
    project = _require_project(args)
    params = {
        "project": project,
        "completed_since": "now" if not args.include_completed else "1970-01-01T00:00:00Z",
        "limit": 100,
        "opt_fields": "gid,name,completed,due_on,assignee.name,permalink_url",
    }
    rows = request("GET", "/tasks", params).get("data", [])
    for row in rows:
        assignee = (row.get("assignee") or {}).get("name", "")
        print(f"{row.get('gid')} | {row.get('name')} | due={row.get('due_on')} | assignee={assignee} | {row.get('permalink_url')}")


def cmd_create_task(args):
    project = _require_project(args)
    workspace = _require_workspace(args)
    data = {
        "workspace": workspace,
        "projects": [project],
        "name": args.name,
    }
    if args.notes:
        data["notes"] = args.notes
    if args.notes_file:
        with open(args.notes_file, "r", encoding="utf-8") as f:
            data["notes"] = f.read()
    if args.due_on:
        data["due_on"] = args.due_on
    task = request("POST", "/tasks", data=data).get("data", {})
    if args.section:
        request("POST", f"/sections/{args.section}/addTask", data={"task": task.get("gid")})
    print(f"{task.get('gid')} | {task.get('name')} | {task.get('permalink_url')}")


def cmd_move(args):
    request("POST", f"/sections/{args.section}/addTask", data={"task": args.task})
    print(f"moved | task={args.task} | section={args.section}")


def cmd_comment(args):
    if args.message_file:
        with open(args.message_file, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        text = args.message
    if not text:
        print("ERROR: pass --message or --message-file", file=sys.stderr)
        sys.exit(1)
    data = request("POST", f"/tasks/{args.task}/stories", data={"text": text}).get("data", {})
    print(f"commented | {data.get('gid')}")


def cmd_complete(args):
    data = request("PUT", f"/tasks/{args.task}", data={"completed": args.completed}).get("data", {})
    print(f"updated | {data.get('gid')} | completed={data.get('completed')}")


def build_parser():
    parser = argparse.ArgumentParser(description="Task-system CLI (Asana worked example)")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("me").set_defaults(func=cmd_me)
    sub.add_parser("workspaces").set_defaults(func=cmd_workspaces)

    projects = sub.add_parser("projects")
    projects.add_argument("--workspace")
    projects.add_argument("--find")
    projects.set_defaults(func=cmd_projects)

    teams = sub.add_parser("teams")
    teams.add_argument("--workspace")
    teams.set_defaults(func=cmd_teams)

    create_project = sub.add_parser("create-project")
    create_project.add_argument("--workspace")
    create_project.add_argument("--team")
    create_project.add_argument("--name", required=True)
    create_project.set_defaults(func=cmd_create_project)

    sections = sub.add_parser("sections")
    sections.add_argument("--project")
    sections.set_defaults(func=cmd_sections)

    create_section = sub.add_parser("create-section")
    create_section.add_argument("--project")
    create_section.add_argument("--name", required=True)
    create_section.set_defaults(func=cmd_create_section)

    tasks = sub.add_parser("tasks")
    tasks.add_argument("--project")
    tasks.add_argument("--include-completed", action="store_true")
    tasks.set_defaults(func=cmd_tasks)

    create_task = sub.add_parser("create-task")
    create_task.add_argument("--workspace")
    create_task.add_argument("--project")
    create_task.add_argument("--section")
    create_task.add_argument("--name", required=True)
    create_task.add_argument("--notes")
    create_task.add_argument("--notes-file")
    create_task.add_argument("--due-on")
    create_task.set_defaults(func=cmd_create_task)

    move = sub.add_parser("move")
    move.add_argument("--task", required=True)
    move.add_argument("--section", required=True)
    move.set_defaults(func=cmd_move)

    comment = sub.add_parser("comment")
    comment.add_argument("--task", required=True)
    comment.add_argument("--message")
    comment.add_argument("--message-file")
    comment.set_defaults(func=cmd_comment)

    complete = sub.add_parser("complete")
    complete.add_argument("--task", required=True)
    complete.add_argument("--completed", action=argparse.BooleanOptionalAction, default=True)
    complete.set_defaults(func=cmd_complete)

    return parser


def main():
    load_env()
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
