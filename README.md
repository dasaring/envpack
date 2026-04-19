# envpack

> CLI tool to snapshot, diff, and restore environment variable sets across projects.

---

## Installation

```bash
pip install envpack
```

Or install from source:

```bash
pip install git+https://github.com/yourname/envpack.git
```

---

## Usage

**Snapshot** your current environment:

```bash
envpack snapshot --name myproject
```

**Diff** two snapshots:

```bash
envpack diff myproject other-project
```

**Restore** a snapshot:

```bash
envpack restore myproject
```

**List** saved snapshots:

```bash
envpack list
```

Snapshots are stored locally in `~/.envpack/` as lightweight JSON files. Sensitive values can be excluded using a `.envpackignore` file in your project root.

---

## Example Workflow

```bash
# Save current env before switching projects
envpack snapshot --name project-a

# Switch context, then compare
envpack diff project-a project-b

# Restore when coming back
envpack restore project-a
```

---

## License

MIT © [yourname](https://github.com/yourname)