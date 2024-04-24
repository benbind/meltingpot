import numpy as np
import torch

def care_graph_uniform_init(sigma):
    """
    Initializes a care graph where weight (1-sigma) is divided equally for all n-1 neighbors.
    """
    n = len(sigma)
    care_graph = [[0]*n for _ in range(n)]

    # Populate the care_graph matrix using nested for loops
    for i in range(n):
        for j in range(n):
            if i == j:
                care_graph[i][j] = sigma[i]
            else:
                care_graph[i][j] = (1 - sigma[i]) / (n - 1)
    return care_graph



def median_of_weighted_median_vote(sigma, care_graph):
    """
    STRATEGY PROOF!
    Calculate the median vote of a list of votes.
    Parameters:
        sigma (list): A list of votes, where each vote is a float between 0 and 1.
    Returns:
        float: The median vote.
    """
    weighted_sigmas = []

    # In [2]: values = torch.tensor([10, 20, 30])
    # ...: frequencies = torch.tensor([1, 2, 3])

    # In [3]: torch.repeat_interleave(values, frequencies, dim=0)
    # Out[3]: tensor([10, 20, 20, 30, 30, 30])

    # first compute the weighted median using torch.repeat_interleave
    for care_i in care_graph:
        weighted_sigmas.append(
            torch.median(
                torch.repeat_interleave(
                    torch.tensor(sigma), torch.floor(torch.tensor(care_i) * 1000).int()
                )
            )
        )

    # next return the median
    return torch.median(torch.tensor(weighted_sigmas)).item()
