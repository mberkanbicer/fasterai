# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/0b_criteria.ipynb (unless otherwise specified).

__all__ = ['Criteria', 'random', 'large_final', 'squared_final', 'small_final', 'large_init', 'small_init',
           'large_init_large_final', 'small_init_small_final', 'magnitude_increase', 'movement',
           'updating_magnitude_increase', 'updating_movement', 'updating_movmag', 'available_criterias', 'criterias',
           'grad_crit']

# Cell
import torch
import torch.nn as nn
import torch.nn.functional as F
from fastcore.basics import *
from fastcore.imports import *
from .granularity import *

# Cell
class Criteria():
    def __init__(self, f, needs_init=False, needs_update=False, output_f=None, return_init=False):
        store_attr()
        assert (needs_init and needs_update)==False, "The init values will be overwritten by the updating ones."

    def __call__(self, m, g):
        if self.needs_update and hasattr(m, '_old_weights') == False:
            m.register_buffer("_old_weights", m._init_weights.clone()) # If the previous value of weights is not known, take the initial value

        if g in granularities[m.__class__.__name__]:
            dim = granularities[m.__class__.__name__][g]
            wf = self.f(m.weight)[None].mean(dim=dim, keepdim=True).squeeze(0)
            if self.needs_init: wi = self.f(m._init_weights)[None].mean(dim=dim, keepdim=True).squeeze(0)
            if self.needs_update: wi = self.f(m._old_weights)[None].mean(dim=dim, keepdim=True).squeeze(0)

        else: raise NameError('Invalid Granularity')

        if self.needs_update: m._old_weights = m.weight.clone() # The current value becomes the old one for the next iteration

        if self.output_f: return self.output_f(wf, wi)
        elif self.return_init: return wi
        else: return wf

# Cell
random = Criteria(torch.randn_like)

# Cell
large_final = Criteria(torch.abs)

# Cell
squared_final = Criteria(torch.square)

# Cell
small_final = Criteria(compose(torch.abs, torch.neg))

# Cell
large_init = Criteria(torch.abs, needs_init=True, return_init=True)

# Cell
small_init = Criteria(compose(torch.abs, torch.neg), needs_init=True, return_init=True)

# Cell
large_init_large_final = Criteria(torch.abs, needs_init=True, output_f=torch.min)

# Cell
small_init_small_final = Criteria(torch.abs, needs_init=True, output_f=lambda x,y: torch.neg(torch.max(x,y)))

# Cell
magnitude_increase = Criteria(torch.abs, needs_init=True, output_f= torch.sub)

# Cell
movement = Criteria(noop, needs_init=True, output_f= lambda x,y: torch.abs(torch.sub(x,y)))

# Cell
updating_magnitude_increase = Criteria(torch.abs, needs_update=True, output_f= torch.sub)

# Cell
updating_movement = Criteria(noop, needs_update=True, output_f= lambda x,y: torch.abs(torch.sub(x,y)))

# Cell
updating_movmag = Criteria(noop, needs_update=True, output_f=lambda x,y: torch.abs(torch.mul(x, torch.sub(x,y))))

# Cell
criterias = ('random', 'large_final', 'small_final', 'squared_final', 'small_init', 'small_final', 'large_init_large_final', 'small_init_small_final', 'magnitude_increase', 'movement', 'updating_magnitude_increase', 'updating_movement', 'updating_movmag')
def available_criterias():
    print(criterias)

# Cell
def grad_crit(m, g):
    if g in granularities[m.__class__.__name__]:
        dim = granularities[m.__class__.__name__][g]
        if m.weight.grad is not None:
            return (m.weight*m.weight.grad)[None].pow(2).mean(dim=dim, keepdim=True).squeeze(0)
        else:
            return m.weight[None].pow(2).mean(dim=dim, keepdim=True).squeeze(0)
    else: raise NameError('Invalid Granularity')