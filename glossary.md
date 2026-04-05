# Glossary

## Institutional and Organizational

- **LANL** – Los Alamos National Laboratory. Jarett's current institution.
- **EES-17** – Jarett's LANL group (Earth and Environmental Sciences, team 17). Eric Bryant is also in EES-17.
- **ALDW-PO** – Kane Bennett's organizational context at LANL.
- **DLT** – Division Leadership Team. Relevant to internal LANL presentations and meetings.
- **AML26 / AML summer student** – The 2026 Applied Machine Learning summer student project context. Tied to the graph autoencoder effort for PBX microstructures. The student comes from Jiun-Shyan Chen's lab at UCSD.
- **GENESIS** – DOE / NNSA proposal context for AI-driven materials discovery. Not a generic project name – refers to a specific mission and funding structure.
- **CMT** – [To be defined carefully based on the actual project/partner context. Placeholder – Jarett to confirm.]

## Project and Modeling Acronyms

- **PBX** – Polymer-bonded explosive. In Jarett's work, treated as a heterogeneous microstructural materials system composed of explosive crystal particles in a polymeric binder.
- **IDOX** – The explosive crystal phase in PBX. Central to the microstructure, segmentation-bias, and fine-particle reconstruction discussion – specifically missing or under-resolved IDOX fines.
- **CT** – Computed tomography. In this context, refers to segmented microstructure data (CT-derived PBX images), not medical imaging.
- **FEM** – Finite element method. Comes up frequently in simulation and mechanics contexts.
- **DEM** – Discrete element method. Relevant for particle assembly generation and synthetic microstructure creation.
- **UQ** – Uncertainty quantification. Important in proposal framing and model design.
- **VGAE / graph autoencoder** – Variational graph autoencoder or graph autoencoder. Central to the PBX latent-compression project.
- **GraphRNN** – Prior generative graph modeling work and conceptual precedent for the graph-based generation efforts.
- **DDPM / diffusion model** – Denoising diffusion probabilistic model. Central to the coarse-to-fine generative work.
- **LAMMPS** – Simulation package that comes up in PBX mechanics and material parameter discussions.
- **rot6d** – 6D rotation representation. Specific technical shorthand used in particle parameterization within the generative models.
- **PyTorch** – ML framework used in most of Jarett's code work.
- **Johnson-Cook** – Constitutive plasticity model used in an active mechanics project.
- **Lode angle** – Stress-state descriptor relevant to the Johnson-Cook extension and constitutive modeling work.
- **Yield surface** – Recurring mechanics concept and one of Jarett's active project areas – representing the boundary of elastic behavior in stress space.
- **PyUMAT** – Python-based constitutive-material implementation context, especially for custom constitutive modeling workflows (e.g., Johnson-Cook with Lode angle).

## Recurring Technical Shorthand and Framing Language

- **Microstructure-to-response** – Shorthand for the broader research direction of linking material structure to constitutive or mechanical behavior.
- **CT segmentation bias** – The systematic under-resolution or misrepresentation of fine particles (especially IDOX fines) in CT-derived PBX data. A specific technical problem, not just generic CT noise.
- **Fine-particle reconstruction** – Recurring shorthand for reconstructing the fine-scale particle structure that is missing or under-resolved in biased CT segmentations.
- **Coarse-to-fine generation** – The generative modeling approach of conditioning on a coarse particle assembly and generating progressively finer structure. More meaningful than just "conditional generation."
- **Latent compression** – Shorthand for the graph autoencoder project's goal of learning compact latent representations of microstructure.
- **Physically meaningful** – Recurring framing term. Models and representations should encode actual physical structure, not just optimize statistical fit.
- **Mechanistically grounded** – Recurring framing term. Methods should be connected to the underlying mechanics of the system rather than treating it as a black box.
- **Structure-property relationships** – The connection between material microstructure and macroscopic mechanical properties. A central theme across multiple projects.
- **Sparse-data setting** – Recurring context descriptor. Many of Jarett's problems involve limited, expensive, or physics-constrained data where purely data-hungry methods fail.
