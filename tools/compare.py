import argparse
from pathlib import Path

import matplotlib

# so gera imagens, sem janela propria (funciona sem tkinter)
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

from backend.runner import ALGORITHMS, COLORS, run_all
from backend.scenario import list_scenarios, load_scenario

SURFACE = "#fcfcfb"
TEXT = "#0b0b0b"
MUTED = "#52514e"
GRID = "#e4e3df"


def style_axis(ax, title, ylabel):
    ax.set_facecolor(SURFACE)
    ax.set_title(title, color=TEXT, fontsize=11, loc="left")
    ax.set_ylabel(ylabel, color=MUTED, fontsize=9)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRID)


def bar_metric(ax, results, values, title, ylabel, fmt="{:.0f}", needs_path=False):
    names = [r.algorithm for r in results]
    bars = ax.bar(names, values, color=[COLORS[n] for n in names], width=0.6,
                  edgecolor=SURFACE, linewidth=2)
    style_axis(ax, title, ylabel)
    for bar, r, v in zip(bars, results, values):
        # custo e recompensas nao existem quando nao ha caminho
        label = "sem caminho" if needs_path and not r.found else fmt.format(v)
        ax.annotate(label, (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    xytext=(0, 3), textcoords="offset points",
                    ha="center", va="bottom", fontsize=8, color=TEXT)
    ax.margins(y=0.15)
    # sem nenhum valor (ex.: ninguem achou caminho) fixa o eixo em 0..1
    if max(values) == 0:
        ax.set_ylim(0, 1)
    else:
        ax.set_ylim(bottom=0)
    # contagens usam so numeros inteiros no eixo
    if fmt == "{:.0f}":
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))


def scenario_figure(scenario, results, figsize=(10, 7)):
    # figura com os 4 paineis, usada no png e na tela de graficos da interface
    fig, axes = plt.subplots(2, 2, figsize=figsize, facecolor=SURFACE)
    bar_metric(axes[0][0], results, [r.time_ms for r in results],
               "Tempo de execucao", "ms (media)", "{:.3f}")
    bar_metric(axes[0][1], results, [r.expanded for r in results],
               "Nos expandidos", "nos")
    bar_metric(axes[1][0], results, [r.cost for r in results],
               "Custo da rota", "custo", needs_path=True)
    bar_metric(axes[1][1], results, [len(r.collected) for r in results],
               f"Recompensas coletadas (de {len(scenario.rewards)})", "recompensas", needs_path=True)
    fig.suptitle(scenario.name, color=TEXT, fontsize=13, x=0.02, ha="left")
    fig.tight_layout()
    return fig


def plot_scenario(scenario, results, out_dir):
    fig = scenario_figure(scenario, results)
    path = out_dir / f"{Path(scenario.path).stem}.png"
    fig.savefig(path, dpi=120, facecolor=SURFACE)
    plt.close(fig)
    return path


def plot_overview(all_results, out_dir):
    names = list(ALGORITHMS)
    labels = [s.name for s, _ in all_results]
    width = 0.8 / len(names)
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), facecolor=SURFACE)

    metrics = [("Nos expandidos por cenario", "nos (escala log)", lambda r: r.expanded),
               ("Tempo de execucao por cenario", "ms (escala log)", lambda r: r.time_ms)]
    for ax, (title, ylabel, getter) in zip(axes, metrics):
        for i, name in enumerate(names):
            xs = [j + (i - (len(names) - 1) / 2) * width for j in range(len(labels))]
            values = [getter(next(r for r in res if r.algorithm == name)) for _, res in all_results]
            ax.bar(xs, values, width=width, color=COLORS[name], label=name,
                   edgecolor=SURFACE, linewidth=2)
        # escala log porque o a* expande muito mais nos que os outros
        ax.set_yscale("log")
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, fontsize=9)
        style_axis(ax, title, ylabel)
        ax.legend(frameon=False, fontsize=9, ncol=len(names), loc="upper right", labelcolor=TEXT)

    fig.tight_layout()
    path = out_dir / "geral.png"
    fig.savefig(path, dpi=120, facecolor=SURFACE)
    plt.close(fig)
    return path


def main():
    parser = argparse.ArgumentParser(description="compara os algoritmos de busca nos cenarios")
    parser.add_argument("target", nargs="?", default="scenarios", help="pasta de cenarios ou um arquivo json")
    parser.add_argument("--repeats", type=int, default=20, help="repeticoes para medir o tempo medio")
    parser.add_argument("--out", default="results", help="pasta onde os graficos sao salvos")
    args = parser.parse_args()

    target = Path(args.target)
    files = [target] if target.is_file() else list_scenarios(target)
    out_dir = Path(args.out)
    out_dir.mkdir(exist_ok=True)

    all_results = []
    for file in files:
        scenario = load_scenario(file)
        results = run_all(scenario, args.repeats)
        all_results.append((scenario, results))
        path = plot_scenario(scenario, results, out_dir)
        print(f"{scenario.name}: grafico salvo em {path}")

    if len(all_results) > 1:
        path = plot_overview(all_results, out_dir)
        print(f"visao geral salva em {path}")


if __name__ == "__main__":
    main()
