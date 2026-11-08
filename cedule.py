"""
Ordonnancement de la maintenance de centrales électriques par algorithme génétique
- Codage : 7 gènes (un par unité) de 4 bits (un bit par intervalle)
- Sélection : loterie (roulette proportionnelle à la performance)
- Croisement : à 1 point, uniquement aux frontières de blocs de 4 bits
- Mutation : par inversion (inversion des bits d'un bloc) ou remise à zéro aléatoire
"""
import random

# ----------------------------------------------------------------- DONNEES
CAPACITE = [20, 15, 35, 40, 15, 15, 10]      # MW par unité
NB_INTERVALLES_MAINT = [2, 2, 1, 1, 1, 1, 1]  # intervalles requis
DEMANDE = [80, 90, 65, 70]                    # MW par intervalle
N_UNITES = len(CAPACITE)
N_INT = len(DEMANDE)
CAPACITE_TOTALE = sum(CAPACITE)               # 150 MW


def patterns_possibles(k, n=N_INT):
    """Toutes les séquences de n bits avec k '1' consécutifs (maintenance continue)."""
    return [[1 if s <= i < s + k else 0 for i in range(n)] for s in range(n - k + 1)]


PATTERNS = [patterns_possibles(k) for k in NB_INTERVALLES_MAINT]


# ----------------------------------------------------------------- CHROMOSOME
def chromosome_aleatoire():
    """Liste de 7 gènes ; chaque gène est un bloc de 4 bits valide."""
    return [random.choice(PATTERNS[u])[:] for u in range(N_UNITES)]


def afficher(chrom):
    return " ".join("".join(map(str, g)) for g in chrom)


# ----------------------------------------------------------------- FONCTION OBJECTIVE
def reserves(chrom):
    res = []
    for i in range(N_INT):
        p_perdue = sum(chrom[u][i] * CAPACITE[u] for u in range(N_UNITES))
        res.append(CAPACITE_TOTALE - p_perdue - DEMANDE[i])
    return res


def performance(chrom):
    """Performance = plus petite réserve ; 0 si une réserve est négative."""
    return max(0, min(reserves(chrom)))


# ----------------------------------------------------------------- SELECTION PAR LOTERIE
def selection_loterie(pop, perfs):
    """Roulette : probabilité de sélection proportionnelle à la performance."""
    total = sum(perfs)
    if total == 0:                       # population sans solution valide
        return random.choice(pop)
    tirage = random.uniform(0, total)
    cumul = 0
    for ind, f in zip(pop, perfs):
        cumul += f
        if tirage <= cumul:
            return ind
    return pop[-1]


# ----------------------------------------------------------------- CROISEMENT
def croisement(p1, p2, pc):
    """Croisement à 1 point, point choisi entre deux blocs de 4 bits."""
    if random.random() < pc:
        pt = random.randint(1, N_UNITES - 1)
        return p1[:pt] + p2[pt:], p2[:pt] + p1[pt:]
    return p1[:], p2[:]


# ----------------------------------------------------------------- MUTATIONS
def mutation_inversion(chrom, pm):
    """Pour chaque gène, avec proba pm, on inverse l'ordre des 4 bits du bloc
    (1100 -> 0011, 1000 -> 0001, 0100 -> 0010). Reste toujours valide."""
    return [g[::-1] if random.random() < pm else g[:] for g in chrom]


def mutation_remplacement(chrom, pm):
    """Alternative (celle des notes) : remplace le bloc par un autre motif valide."""
    return [random.choice(PATTERNS[u])[:] if random.random() < pm else chrom[u][:]
            for u, _ in enumerate(chrom)]


MUTATIONS = {"inversion": mutation_inversion, "remplacement": mutation_remplacement}


# ----------------------------------------------------------------- BOUCLE PRINCIPALE
def algorithme_genetique(taille_pop=40, generations=60, pc=0.8, pm=0.1,
                         mutation="inversion", elitisme=True, graine=None):
    if graine is not None:
        random.seed(graine)
    muter = MUTATIONS[mutation]
    pop = [chromosome_aleatoire() for _ in range(taille_pop)]
    historique = []
    meilleur, meilleure_perf = None, -1

    for g in range(generations):
        perfs = [performance(c) for c in pop]
        i_best = max(range(taille_pop), key=lambda i: perfs[i])
        if perfs[i_best] > meilleure_perf:
            meilleur, meilleure_perf = pop[i_best][:], perfs[i_best]
        historique.append((max(perfs), sum(perfs) / taille_pop))

        nouvelle = [meilleur[:]] if elitisme else []
        while len(nouvelle) < taille_pop:
            p1 = selection_loterie(pop, perfs)
            p2 = selection_loterie(pop, perfs)
            e1, e2 = croisement(p1, p2, pc)
            nouvelle.append(muter(e1, pm))
            if len(nouvelle) < taille_pop:
                nouvelle.append(muter(e2, pm))
        pop = nouvelle

    return meilleur, meilleure_perf, historique


if __name__ == "__main__":
    # Vérification avec l'exemple des notes de cours
    ex = [[0,1,1,0],[0,0,1,1],[0,0,0,1],[1,0,0,0],[0,1,0,0],[0,0,1,0],[1,0,0,0]]
    print("Exemple du cours :", afficher(ex), "-> réserves", reserves(ex),
          "-> performance", performance(ex))
    print()

    for type_mut in MUTATIONS:
        sol, perf, hist = algorithme_genetique(mutation=type_mut, graine=1)
        print(f"=== Mutation : {type_mut} ===")
        print("Meilleure cédule :", afficher(sol))
        print("Réserves par intervalle :", reserves(sol))
        print("Performance (réserve min) :", perf)
        for u in range(N_UNITES):
            ints = [i + 1 for i, b in enumerate(sol[u]) if b]
            print(f"  Unité {u+1} ({CAPACITE[u]} MW) : maintenance aux intervalles {ints}")
        print("Évolution (meilleure perf, tous les 10 gén.) :",
              [h[0] for h in hist][::10])
        print()