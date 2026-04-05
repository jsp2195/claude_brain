# Coarse-to-Fine Generative Modeling of PBX Microstructures

## Overview

Graph- and diffusion-based generative modeling for polymer-bonded explosive microstructures. Condition on a coarse particle assembly and generate finer particle structure that is physically plausible, mechanically meaningful, and useful for downstream simulation. Includes correcting CT segmentation bias by reconstructing fine-particle structure missing or under-resolved in CT-derived PBX data.

## Status

Active model development and debugging. Iterating on architecture, conditioning behavior, morphology prediction, overlap penalties, and generation quality.

## Key Goals

- Get the conditional generation pipeline working cleanly
- Make the model actually respect coarse conditioning
- Reduce particle overlap
- Improve geometry realism
- Reconstruct more realistic fine-scale structure from biased CT segmentations
- Validate with diagnostics and visualization
- Push toward a research-grade generative pipeline, potentially including iterative packing logic for progressively finer particles in void space

## Deadlines

No single hard external deadline. One of the main active research threads — tied to near-term technical progress and research output.

## People

Jarett Poliner, Eric Bryant, Kane Bennett
