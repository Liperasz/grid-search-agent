import sys
from pathlib import Path

from backend.scenario import list_scenarios
from frontend.app import run_app


def main():
    files = list_scenarios("scenarios")
    index = 0
    # cenario passado na linha de comando abre direto
    if len(sys.argv) > 1:
        chosen = Path(sys.argv[1])
        if not chosen.exists():
            print(f"arquivo nao encontrado: {chosen}")
            return
        if chosen.resolve() not in [f.resolve() for f in files]:
            files.append(chosen)
        index = [f.resolve() for f in files].index(chosen.resolve())
    if not files:
        print("nenhum cenario encontrado em scenarios/")
        return
    run_app(files, index)


if __name__ == "__main__":
    main()
