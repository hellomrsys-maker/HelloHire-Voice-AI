"""
gradient_routing.py - Projected Conflicting Gradients (PCGrad) for Multi-Task Learning.

Eliminates negative transfer and gradient interference between disparate training objectives:
- VCE Acoustic CTC & Prosody Losses
- CCTE 8-Dimensional Cognitive Losses
- RSSE Register Classification
- AEEE IRT Parameter Estimation

Mathematical formulation:
If g_i · g_j < 0:
    g_i = g_i - ((g_i · g_j) / ||g_j||^2) * g_j
"""

from __future__ import annotations
import copy
import random
from typing import List, Tuple
import torch
import torch.nn as nn

class PCGradOptimizer:
    """
    Projected Conflicting Gradients (PCGrad) wrapper around any standard PyTorch optimizer.
    """

    def __init__(self, optimizer: torch.optim.Optimizer, reduction: str = "mean"):
        self.optimizer = optimizer
        self.reduction = reduction

    @property
    def param_groups(self):
        return self.optimizer.param_groups

    def zero_grad(self):
        self.optimizer.zero_grad()

    def step(self):
        self.optimizer.step()

    def pcgrad_backward(self, task_losses: List[torch.Tensor]) -> None:
        """
        Performs multi-task backward pass with orthogonal gradient projection.
        
        Args:
            task_losses: List of scalar loss tensors, one per task objective.
        """
        num_tasks = len(task_losses)
        if num_tasks == 0:
            return
        if num_tasks == 1:
            task_losses[0].backward()
            return

        # 1. Compute individual task gradients
        task_grads: List[List[torch.Tensor]] = []
        shared_params = [p for p in self.optimizer.param_groups[0]["params"] if p.requires_grad]

        for i, loss in enumerate(task_losses):
            self.optimizer.zero_grad()
            loss.backward(retain_graph=(i < num_tasks - 1))

            grad_vector = []
            for p in shared_params:
                if p.grad is not None:
                    grad_vector.append(p.grad.detach().clone())
                else:
                    grad_vector.append(torch.zeros_like(p))
            task_grads.append(grad_vector)

        # 2. Project conflicting gradients
        projected_grads = copy.deepcopy(task_grads)
        order = list(range(num_tasks))

        for i in range(num_tasks):
            random.shuffle(order)
            for j in order:
                if i == j:
                    continue

                # Compute inner product g_i · g_j across all parameters
                dot_product = sum(
                    torch.sum(projected_grads[i][k] * task_grads[j][k])
                    for k in range(len(shared_params))
                )

                # If conflicting (dot product < 0), project g_i onto normal plane of g_j
                if dot_product < 0:
                    norm_sq = sum(
                        torch.sum(task_grads[j][k] ** 2)
                        for k in range(len(shared_params))
                    )
                    if norm_sq > 1e-12:
                        projection_scale = dot_product / norm_sq
                        for k in range(len(shared_params)):
                            projected_grads[i][k] -= projection_scale * task_grads[j][k]

        # 3. Aggregate projected gradients across tasks
        self.optimizer.zero_grad()
        for k, p in enumerate(shared_params):
            if self.reduction == "mean":
                combined_grad = torch.stack([projected_grads[i][k] for i in range(num_tasks)], dim=0).mean(dim=0)
            else:
                combined_grad = torch.stack([projected_grads[i][k] for i in range(num_tasks)], dim=0).sum(dim=0)
            p.grad = combined_grad
