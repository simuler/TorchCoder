"""K-Means clustering task."""

TASK = {
    "category": "ML 基础与解码策略",
    "title": "K-Means Clustering",
    "difficulty": "Medium",
    "function_name": "kmeans",
    "hint": (
        "Initialize centroids from the first k points for deterministic behavior. "
        "Then alternate: assign each point to the nearest centroid, and recompute "
        "each centroid as the mean of its assigned points. If a cluster is empty, "
        "keep its previous centroid."
    ),
    "tests": [
        {
            "name": "Output shapes",
            "code": """
import torch
x = torch.tensor([
    [0.0, 0.0],
    [5.0, 5.0],
    [0.2, -0.1],
    [4.8, 5.2],
], dtype=torch.float32)
centroids, assignments = {fn}(x, num_clusters=2, num_iters=4)
assert centroids.shape == (2, 2), f'Centroid shape mismatch: {centroids.shape}'
assert assignments.shape == (4,), f'Assignment shape mismatch: {assignments.shape}'
assert assignments.dtype in (torch.int32, torch.int64), f'Assignments should be integer typed, got {assignments.dtype}'
""",
        },
        {
            "name": "Finds two simple clusters",
            "code": """
import torch
x = torch.tensor([
    [0.0, 0.0],
    [5.0, 5.0],
    [0.0, 1.0],
    [1.0, 0.0],
    [5.0, 6.0],
    [6.0, 5.0],
], dtype=torch.float32)
centroids, assignments = {fn}(x, num_clusters=2, num_iters=10)
expected = torch.tensor([[1.0 / 3.0, 1.0 / 3.0], [16.0 / 3.0, 16.0 / 3.0]])
assert torch.allclose(centroids, expected, atol=1e-4), f'Wrong centroids: {centroids} vs {expected}'
assert torch.equal(assignments[[0, 2, 3]], torch.zeros(3, dtype=assignments.dtype)), f'First cluster assignments wrong: {assignments}'
assert torch.equal(assignments[[1, 4, 5]], torch.ones(3, dtype=assignments.dtype)), f'Second cluster assignments wrong: {assignments}'
""",
        },
        {
            "name": "Matches nearest-centroid rule after convergence",
            "code": """
import torch
x = torch.tensor([
    [0.0, 0.0],
    [10.0, 10.0],
    [0.2, 0.1],
    [9.9, 10.2],
    [0.1, -0.2],
    [10.1, 9.8],
], dtype=torch.float32)
centroids, assignments = {fn}(x, num_clusters=2, num_iters=8)
distances = torch.cdist(x, centroids)
expected_assignments = distances.argmin(dim=1)
assert torch.equal(assignments, expected_assignments), 'Assignments are not the nearest centroids'
""",
        },
        {
            "name": "Empty clusters keep previous centroid",
            "code": """
import torch
x = torch.tensor([
    [0.0, 0.0],
    [10.0, 10.0],
    [10.0, 10.0],
    [10.0, 10.0],
], dtype=torch.float32)
centroids, assignments = {fn}(x, num_clusters=3, num_iters=5)
expected = torch.tensor([
    [0.0, 0.0],
    [10.0, 10.0],
    [10.0, 10.0],
], dtype=torch.float32)
assert torch.allclose(centroids, expected, atol=1e-5), f'Unexpected centroids with empty cluster: {centroids}'
assert assignments.shape == (4,), 'Assignments shape changed unexpectedly'
""",
        },
    ],
}
