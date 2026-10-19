# Agente de busca em grid com recompensas

Trabalho da disciplina de Fundamentos de Inteligência Artificial (agentes inteligentes).

Um agente navega por um mapa com terrenos de custos diferentes até chegar a um prêmio, coletando recompensas pelo caminho. A rota é calculada por quatro algoritmos de busca (largura, profundidade, gulosa e A*), a movimentação é animada em Pygame e os algoritmos são comparados em tempo de execução, nós expandidos e qualidade da rota.

## Enunciado resumido

- O ambiente é um grafo com pelo menos 30 vértices, representado como um grid.
- Paredes são intransponíveis. Os terrenos andáveis têm custo para entrar:

  | Terreno | Custo |
  |---|---|
  | Sólido e plano | 1 |
  | Arenoso | 4 |
  | Rochoso | 10 |
  | Pântano | 20 |

- O agente parte de um nó inicial e deve chegar ao prêmio (estado objetivo) pela rota de menor custo.
- Existem pelo menos 5 recompensas espalhadas no mapa.
- Busca cega (largura e profundidade): pega as recompensas que estão nos vértices do caminho encontrado.
- Busca com heurística (gulosa e A*): a heurística deve avaliar se compensa desviar da rota para pegar recompensas próximas.
- O programa deve detectar quando não existe caminho (paredes, becos, salas sem entrada).
- Depois de calcular a rota, o programa mostra o agente se movendo por ela.
- Os algoritmos devem ser comparados em tempo de execução e quantidade de nós expandidos.

## Como executar

Requer Python 3. As dependências são `pygame-ce` e `matplotlib`.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Usamos `pygame-ce`, a versão do pygame mantida pela comunidade, porque o pacote `pygame` original não tem build para Python 3.14. A API é a mesma e o import continua sendo `import pygame`.

Interface:

```bash
python main.py                                     # abre no primeiro cenário
python main.py scenarios/05_recompensas_longe.json # abre um cenário específico
```

Gráficos comparativos em PNG (salvos em `results/`):

```bash
python -m tools.compare                                      # todos os cenários
python -m tools.compare scenarios/04_pantano_vs_volta.json   # um cenário
python -m tools.compare --repeats 50 --out outra_pasta
```

## Controles da interface

| Tecla | Ação |
|---|---|
| `1` `2` `3` `4` ou clique nos botões | Roda BFS, DFS, Gulosa ou A* |
| `ESPACO` | Pula a animação da exploração ou pausa o agente |
| `+` `-` | Altera a velocidade (x0.25 até x8) |
| `R` | Reinicia o cenário |
| `N` `P` | Próximo e anterior cenário da pasta `scenarios/` |
| `T` | Mostra as rotas dos 4 algoritmos ao mesmo tempo |
| `C` | Abre e fecha a tabela comparativa |
| `G` | Abre e fecha os gráficos comparativos |
| `ESC` | Sai do programa |

Passando o mouse sobre o mapa, o rodapé mostra a posição, o terreno, o custo e se há recompensa na célula.

## Estrutura do projeto

```
main.py                  ponto de entrada da interface
requirements.txt
scenarios/               cenários em JSON
backend/                 lógica, sem dependência de pygame
  terrain.py             tipos de terreno: caractere, custo, nome, cor
  grid.py                classe Grid: custo, paredes, vizinhos
  scenario.py            leitura e validação do JSON, dataclass Scenario
  result.py              dataclass SearchResult
  heuristics.py          distância Manhattan e heurística com recompensas
  runner.py              registro dos algoritmos, cores, execução com média de tempo
  search/
    common.py            métricas, reconstrução do caminho, estado com recompensas
    bfs.py
    dfs.py
    greedy.py
    astar.py
frontend/                interface em pygame
  app.py                 loop principal, teclas, estados da animação
  renderer.py            desenho do mapa, itens, exploração, rotas e agente
  panel.py               painel lateral e tabela comparativa
tools/
  compare.py             gráficos com matplotlib
```

O backend não conhece a interface. O frontend só consome dois objetos: `Scenario` (o mapa carregado) e `SearchResult` (o resultado de uma busca). Os algoritmos podem ser executados e testados sem abrir janela.

## Formato do cenário

Cada cenário é um arquivo JSON com duas camadas de mesmo tamanho: `terrain` define o terreno de cada célula e `items` define o que está em cima dela. Assim uma recompensa, o início ou o prêmio podem ficar em qualquer terreno.

```json
{
  "name": "Pantano ou volta",
  "description": "Caminho curto pelo pantano contra uma volta maior em terreno plano.",
  "reward_value": 15,
  "terrain": [
    "###############",
    "#.............#",
    "#.###########.#",
    "#...ppppp.....#",
    "#.###########.#",
    "#.............#",
    "###############"
  ],
  "items": [
    "               ",
    " $      $      ",
    "               ",
    " S           G ",
    "               ",
    " $     $     $ ",
    "               "
  ]
}
```

| Camada | Caractere | Significado |
|---|---|---|
| `terrain` | `#` | parede |
| `terrain` | `.` | sólido e plano (1) |
| `terrain` | `a` | arenoso (4) |
| `terrain` | `r` | rochoso (10) |
| `terrain` | `p` | pântano (20) |
| `items` | `S` | início do agente |
| `items` | `G` | prêmio |
| `items` | `$` | recompensa |
| `items` | espaço | vazio |

`reward_value` é o valor de cada recompensa, na mesma unidade do custo de terreno. É o número que a heurística usa para decidir se um desvio compensa. O padrão é 15.

O carregamento gera erro com mensagem clara quando:
- as linhas têm tamanhos diferentes ou as camadas não batem;
- aparece um caractere desconhecido;
- não há exatamente um `S` e um `G`;
- um item está em cima de parede.

Menos de 30 células livres ou menos de 5 recompensas gera apenas um aviso no terminal, para permitir mapas pequenos de teste. Na interface, um JSON inválido mostra o erro no painel sem fechar o programa.

Para criar um cenário novo, basta copiar um arquivo de `scenarios/`, editar as duas camadas e abrir com `python main.py`.

## Modelagem

- Cada célula andável é um vértice. Duas células vizinhas na horizontal ou na vertical são ligadas por uma aresta (4 direções).
- O custo de um passo é o custo do terreno da célula de destino. O custo de uma rota é a soma dos passos, sem contar a célula inicial.
- Os vizinhos são gerados sempre na mesma ordem (cima, direita, baixo, esquerda), o que deixa os resultados determinísticos.

## Algoritmos

Todos os algoritmos devolvem um `SearchResult` com:
- `found` e `message`;
- `path`, `cost` e `collected` (recompensas na rota);
- `expanded`, `generated` e `max_frontier`;
- `time_ms` e `explored_order` (a ordem de expansão, usada na animação).

### Busca em largura (BFS)
- Estado: posição.
- Fronteira: fila FIFO (`collections.deque`), com conjunto de visitados.
- Encontra o caminho com menos passos, que não é necessariamente o de menor custo.
- Recompensas: as que estiverem no caminho encontrado.

### Busca em profundidade (DFS)
- Estado: posição.
- Fronteira: pilha explícita, sem recursão, para não esbarrar no limite de recursão do Python.
- Encontra um caminho qualquer, geralmente longo.
- Recompensas: as que estiverem no caminho encontrado.

### Busca gulosa
- Estado: `(posição, recompensas coletadas)`.
- Fronteira: fila de prioridade (`heapq`) ordenada só por `h(n)`.
- É rápida, mas não garante a melhor rota.

### A*
- Estado: `(posição, recompensas coletadas)`.
- Fronteira: fila de prioridade ordenada por `g(n) + h(n)`. Guarda o melhor `g` de cada estado e descarta entradas desatualizadas.
- Com a heurística admissível abaixo, encontra a rota ótima para o objetivo definido.

### Como a recompensa entra na busca com heurística

As recompensas coletadas fazem parte do estado e ficam guardadas numa máscara de bits, um bit por recompensa. Passar por uma célula com `$` liga o bit correspondente. Assim o mesmo lugar visitado com conjuntos de recompensas diferentes conta como estados diferentes.

O objetivo minimizado é:

```
custo da rota + reward_value * recompensas não coletadas
```

Isso equivale a "custo menos valor das recompensas", mas sem custo negativo, o que mantém o A* correto. A penalidade é somada no passo que entra no prêmio. Chegar ao prêmio encerra a viagem: o agente não passa por ele para pegar algo depois.

Na prática, o agente pega toda recompensa cujo desvio custa menos do que ela vale e ignora as que custam mais. Aumentar `reward_value` no JSON faz o agente desviar mais; diminuir faz desviar menos.

### Heurística

Usa apenas a distância Manhattan `d(a, b) = |l1 - l2| + |c1 - c2|` e o valor da recompensa `V`:

```
h(pos) = max( d(pos, G),
              max sobre cada recompensa r não coletada de
                  min( d(pos, r) + d(r, G),    se for buscar r
                       d(pos, G) + V ) )       se desistir de r
```

Para cada recompensa que falta, a heurística compara o custo mínimo de ir buscá-la e depois seguir para o prêmio com o custo de ir direto ao prêmio pagando a penalidade, e fica com o menor. Essa é a avaliação de "compensa desviar" pedida no enunciado.

Como o menor custo de terreno é 1, a distância Manhattan nunca superestima o custo real. Cada termo é um limite inferior do custo restante, então a heurística é admissível e o A* devolve a rota ótima. A gulosa usa a mesma heurística sem o `g`. No prêmio, `h = 0`.

### Detecção de ausência de caminho

Cada algoritmo detecta sozinho: se a fronteira esvazia sem chegar ao prêmio, o resultado volta com `found = False` e a mensagem "nao existe caminho ate o premio". Becos e salas fechadas são tratados naturalmente, porque os vizinhos se esgotam. Não há verificação prévia no carregamento.

### Métricas

| Métrica | Significado |
|---|---|
| Tempo | `time.perf_counter()` em volta da busca. No comparativo, é a média de várias execuções. |
| Nós expandidos | Estados retirados da fronteira e expandidos. |
| Nós gerados | Estados colocados na fronteira. |
| Fronteira máxima | Maior tamanho da fronteira durante a busca, uma medida de memória. |
| Passos, custo, recompensas | Qualidade da rota encontrada. |

## Interface

- **Mapa:** cada terreno tem uma cor, as paredes são blocos escuros, as recompensas são moedas, o prêmio é uma estrela e o agente é uma carinha.
- **Rodar um algoritmo** gera duas animações:
  1. **Exploração:** as células expandidas são sombreadas na ordem em que a busca as visitou, mostrando o padrão de cada algoritmo.
  2. **Movimento:** a rota aparece na cor do algoritmo e o agente anda casa por casa. Em terreno mais caro ele demora mais, e as moedas somem quando coletadas. O painel mostra passo, custo acumulado e recompensas em tempo real.
- **Resultado:** ao final, o painel mostra todas as métricas.
- **Sem caminho:** a exploração cobre toda a área alcançável e aparece uma faixa vermelha avisando. O agente não se move.
- **Tabela comparativa (`C`):** roda os quatro algoritmos no cenário atual e destaca em verde o melhor valor de cada coluna.
- **Gráficos (`G`):** o matplotlib desenha a figura em memória e o pygame exibe dentro da própria janela, sem depender de tkinter.

## Cenários incluídos

| Arquivo | O que testa |
|---|---|
| `01_padrao.json` | Mapa principal com todos os terrenos, becos e recompensas em terrenos variados |
| `02_sem_caminho.json` | Prêmio dentro de uma sala sem entrada |
| `03_labirinto_becos.json` | Labirinto com vários becos sem saída |
| `04_pantano_vs_volta.json` | Caminho curto pelo pântano contra uma volta maior em terreno plano |
| `05_recompensas_longe.json` | Recompensas dentro de rocha e pântano, onde o desvio não compensa |
| `06_recompensa_compensa.json` | Recompensas na areia perto da rota, onde o desvio compensa |

Resultados com `reward_value = 15`:

| Cenário | BFS custo / $ | DFS custo / $ | Gulosa custo / $ | A* custo / $ | Expandidos BFS / DFS / Gulosa / A* |
|---|---|---|---|---|---|
| 01 padrão | 95 / 0 | 119 / 1 | 91 / 1 | 73 / 2 | 112 / 57 / 52 / 4091 |
| 02 sem caminho | sem caminho | sem caminho | sem caminho | sem caminho | 56 / 56 / 1712 / 1712 |
| 03 labirinto | 38 / 1 | 38 / 1 | 38 / 1 | 38 / 1 | 70 / 39 / 149 / 553 |
| 04 pântano | 107 / 0 | 16 / 2 | 115 / 2 | 34 / 5 | 36 / 17 / 31 / 125 |
| 05 recompensas longe | 15 / 0 | 217 / 0 | 182 / 3 | 24 / 1 | 97 / 22 / 94 / 482 |
| 06 desvio compensa | 17 / 0 | 75 / 3 | 80 / 6 | 59 / 6 | 78 / 22 / 85 / 2208 |

O que os resultados mostram:
- **BFS:** encontra menos passos, mas no cenário 04 atravessa o pântano e paga caro.
- **DFS:** expande poucos nós, mas costuma gerar rotas ruins.
- **Gulosa:** é rápida, mas não garante a melhor rota.
- **A*:** sempre atinge o menor valor de custo mais penalidade. No cenário 05 desvia só para a recompensa na areia; no 06 pega todas.
- **Custo de memória:** o A* expande muito mais nós, porque o espaço de estados inclui quais recompensas já foram coletadas.

## Requisitos atendidos

| Requisito | Onde |
|---|---|
| Grafo com 30 ou mais vértices | Todos os cenários (43 a 150 células livres), checado em `scenario.py` |
| Paredes e 4 terrenos com custos | `terrain.py`, `grid.py` |
| 5 ou mais recompensas | Todos os cenários, checado em `scenario.py` |
| BFS, DFS, gulosa e A* | `backend/search/` |
| Busca cega pega recompensas do caminho | `build_result` em `search/common.py` |
| Heurística avalia se compensa desviar | `heuristics.py`, estado com recompensas em `search/common.py` |
| Rota de menor custo | A* com heurística admissível |
| Detectar ausência de caminho | Fronteira vazia em cada algoritmo, cenário `02_sem_caminho.json` |
| Animação do agente seguindo a rota | `frontend/` |
| Comparativo de tempo e nós expandidos | Tabela (`C`), gráficos (`G`) e `tools/compare.py` |
