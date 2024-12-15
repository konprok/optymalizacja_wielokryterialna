import numpy as np

def rsm(decision_matrix, weights=None):
    """
    RSM dla wariantu ciągłego z dynamicznym punktem docelowym i nadirem.
    Wszystkie kryteria są traktowane jako minimalizacyjne.
    """
    num_alternatives, num_criteria = decision_matrix.shape

    if weights is None:
        weights = np.ones(num_criteria) / num_criteria

    weights = weights / np.sum(weights)

    target = np.min(decision_matrix, axis=0)
    nadir = np.max(decision_matrix, axis=0)

    norm_matrix = (decision_matrix - target) / (nadir - target + 1e-6)

    distances_to_target = np.sqrt(np.sum(weights * norm_matrix ** 2, axis=1))
    distances_to_nadir = np.sqrt(np.sum(weights * (1 - norm_matrix) ** 2, axis=1))

    rsm_scores = distances_to_nadir - distances_to_target
    
    ranking = np.argsort(rsm_scores)

    return ranking, rsm_scores


def fuzzy_topsis(decision_matrix, weights):
    """
    Fuzzy TOPSIS z założeniem, że wszystkie kryteria są minimalizacyjne.
    """
    num_alternatives, num_criteria, _ = decision_matrix.shape

    normalized_matrix = np.zeros_like(decision_matrix)
    for j in range(num_criteria):
        min_l = np.min(decision_matrix[:, j, 0])
        normalized_matrix[:, j, :] = min_l / decision_matrix[:, j, :]

    weighted_matrix = np.zeros_like(normalized_matrix)
    for j in range(num_criteria):
        weighted_matrix[:, j, :] = normalized_matrix[:, j, :] * weights[j]

    fpis = np.min(weighted_matrix, axis=0)
    fnis = np.max(weighted_matrix, axis=0)

    distances_to_fpis = np.sqrt(np.sum((weighted_matrix - fpis) ** 2, axis=(1, 2)))
    distances_to_fnis = np.sqrt(np.sum((weighted_matrix - fnis) ** 2, axis=(1, 2)))

    scores = distances_to_fpis / (distances_to_fpis + distances_to_fnis)

    ranking = np.argsort(scores)
    return ranking, scores


def uta(decision_matrix, num_segments, weights=None):
    """
    UTA dla minimalizacji kryteriów.
    """
    num_alternatives, num_criteria = decision_matrix.shape

    norm_matrix = (decision_matrix - decision_matrix.min(axis=0)) / (
        decision_matrix.max(axis=0) - decision_matrix.min(axis=0) + 1e-6
    )

    if weights is None:
        weights = np.ones(num_criteria) / num_criteria

    utility_functions = np.zeros((num_segments + 1, num_criteria))
    for crit in range(num_criteria):
        utility_functions[:, crit] = np.linspace(1, 0, num_segments + 1)

    utilities = np.zeros(num_alternatives)
    for i in range(num_alternatives):
        for crit in range(num_criteria):
            value = norm_matrix[i, crit]
            segment_index = int(value * num_segments)
            segment_index = min(segment_index, num_segments - 1)
            utilities[i] += weights[crit] * utility_functions[segment_index, crit]

    ranking = np.argsort(utilities)

    return utilities, ranking, utility_functions


def topsis(decision_matrix, weights):
    """
    TOPSIS dla minimalizacji kryteriów.
    """
    norm_matrix = decision_matrix / np.sqrt(np.sum(decision_matrix**2, axis=0))

    weighted_matrix = norm_matrix * weights

    ideal_solution = np.min(weighted_matrix, axis=0)
    anti_ideal_solution = np.max(weighted_matrix, axis=0)

    distances_to_ideal = np.sqrt(np.sum((weighted_matrix - ideal_solution)**2, axis=1))
    distances_to_anti_ideal = np.sqrt(np.sum((weighted_matrix - anti_ideal_solution)**2, axis=1))

    scores = distances_to_ideal / (distances_to_ideal + distances_to_anti_ideal)

    ranking = np.argsort(scores)
    return ranking, scores
