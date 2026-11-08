# TD – Algorithmes génétiques : cédule de maintenance de centrales électriques

## 1. Objectif

Appliquer un algorithme génétique (AG) à un problème d'ordonnancement de ressources : planifier la maintenance préventive de 7 centrales électriques sur 4 intervalles de l'année, de façon à **maximiser la puissance en réserve**, tout en respectant la demande.

Le TD couvre :
- la formulation du problème (codage, fonction objective, contraintes) ;
- l'implémentation en Python d'un AG avec **sélection par loterie (roulette)** et **mutation par inversion** ;
- la comparaison avec une autre mutation (remplacement par un motif valide).

## 2. Énoncé du problème

| Unité | Capacité (MW) | Intervalles de maintenance requis |
|-------|---------------|-----------------------------------|
| 1 | 20 | 2 |
| 2 | 15 | 2 |
| 3 | 35 | 1 |
| 4 | 40 | 1 |
| 5 | 15 | 1 |
| 6 | 15 | 1 |
| 7 | 10 | 1 |

- Capacité totale : **150 MW**.
- L'année est séparée en **4 intervalles**, avec une demande de **80, 90, 65 et 70 MW**.
- La maintenance d'une unité commence au début d'un intervalle et se termine à la fin d'un intervalle ; les intervalles d'une même unité sont consécutifs.
- La réserve pendant un intervalle doit rester positive :
  `Réserve = Capacité totale − P_perdue (maintenance) − Demande`

## 3. Formulation

### Codage
Un chromosome est formé de **7 gènes de 4 bits** (un gène par unité, un bit par intervalle). `1` signifie maintenance, `0` signifie pas de maintenance.

| Unités | Valeurs possibles du gène |
|--------|---------------------------|
| 1 et 2 | `1100`, `0110`, `0011` |
| 3 à 7 | `1000`, `0100`, `0010`, `0001` |

Exemple : `0110 0011 0001 1000 0100 0010 1000`

Le codage garantit par construction le bon nombre d'intervalles et leur continuité : aucune pénalité ni réparation n'est nécessaire.

### Fonction objective
Pour chaque intervalle *i* :

```
R_i = 150 − Σ_u (x[u][i] × C_u) − D_i
```

La performance (fitness) du chromosome est la plus petite réserve, ramenée à 0 si elle est négative :

```
f(chromosome) = max(0, min_i R_i)
```

Objectif : **maximiser f**.

Vérification avec l'exemple du cours : réserves = [20, 25, 35, 30], donc f = 20.

### Opérateurs génétiques

| Opérateur | Choix | Détail |
|-----------|-------|--------|
| Sélection | **Loterie (roulette)** | Probabilité de sélection = f_k / Σ f. Tirage uniforme si Σ f = 0. |
| Croisement | 1 point | Le point est choisi **entre deux blocs de 4 bits**, jamais au milieu d'un gène. |
| Mutation | **Inversion** | Pour chaque gène, avec la probabilité p_m, on inverse l'ordre des 4 bits (`1100`→`0011`, `1000`→`0001`, `0100`→`0010`). Le motif reste valide. |
| Mutation (variante) | Remplacement | Le gène est remplacé par un autre motif valide de la même unité. |
| Élitisme | Oui | Le meilleur individu est conservé à chaque génération. |

## 4. Utilisation

**Prérequis** : Python 3.8 ou plus récent. Aucune bibliothèque externe n'est nécessaire.

```bash
python ag_maintenance.py
```

Le script :
1. vérifie la fonction objective sur l'exemple du cours ;
2. lance l'AG avec chacune des deux mutations ;
3. affiche la meilleure cédule, les réserves par intervalle et l'évolution de la performance.

### Paramètres

```python
algorithme_genetique(
    taille_pop=40,         # taille de la population
    generations=60,        # nombre de générations
    pc=0.8,                # probabilité de croisement
    pm=0.1,                # probabilité de mutation (par gène)
    mutation="inversion",  # "inversion" ou "remplacement"
    elitisme=True,
    graine=1,              # graine aléatoire (reproductibilité)
)
```

La fonction retourne `(meilleur_chromosome, performance, historique)`.

## 5. Structure du code

| Fonction | Rôle |
|----------|------|
| `patterns_possibles(k)` | Génère les motifs de maintenance valides pour k intervalles |
| `chromosome_aleatoire()` | Crée un individu valide |
| `reserves(chrom)` | Calcule la réserve de chaque intervalle |
| `performance(chrom)` | Fonction objective |
| `selection_loterie(pop, perfs)` | Sélection par roulette |
| `croisement(p1, p2, pc)` | Croisement à 1 point par blocs |
| `mutation_inversion(chrom, pm)` | Mutation par inversion |
| `mutation_remplacement(chrom, pm)` | Mutation par remplacement |
| `algorithme_genetique(...)` | Boucle principale |

## 6. Résultats

Les deux types de mutation trouvent la même cédule :

| Unité | Maintenance | Intervalles |
|-------|-------------|-------------|
| 1 | `0011` | 3, 4 |
| 2 | `1100` | 1, 2 |
| 3 | `0001` | 4 |
| 4 | `0010` | 3 |
| 5 | `0100` | 2 |
| 6 | `1000` | 1 |
| 7 | `1000` | 1 |

- Réserves : **30, 30, 25, 25 MW**, donc **performance = 25 MW**.
- C'est l'optimum : la somme des réserves est fixe (4×150 − 185 − 305 = 110 MW), donc la réserve minimale est au plus 27,5 MW ; toutes les valeurs étant des multiples de 5, le maximum atteignable est 25.

## 7. Pistes d'expérimentation

- Faire varier `taille_pop`, `pc` et `pm`, et observer la vitesse de convergence.
- Lancer plusieurs exécutions avec des graines différentes et comparer inversion et remplacement (moyenne de la meilleure performance par génération).
- Désactiver l'élitisme et observer l'effet.
- Ajouter une contrainte (par exemple, deux unités qui ne peuvent pas être en maintenance en même temps) et l'intégrer à la fonction objective.
- Remplacer la loterie par une autre sélection (tournoi, rang) et comparer.

## 8. Remarques

- La mutation et le croisement se font **uniquement sur des blocs de 4 bits**, sinon on obtiendrait des cédules illogiques ou fausses.
- Règle générale pour la population : de 6 à 7 fois le nombre de variables à optimiser. Les probabilités de croisement et de mutation doivent être testées avec plusieurs valeurs, sans se limiter à une seule.
