# Adapter: CLI (operator entry point)

`aegis` command line for human operators. Thin over core: every command goes
through contracts + core guards. Uses stdlib `argparse` until dependencies are
installed in the environment (logged in the Decision Log; typer stays in
pyproject extras).

```bash
python3 -m adapters.cli.main mission validate contracts/fixtures/mission.instance.json
python3 -m adapters.cli.main scope check 203.0.113.200 --mission contracts/fixtures/mission.instance.json
python3 -m adapters.cli.main audit verify <audit.jsonl>
```
