# Yantai VR spatial configuration review

Research materials for **VR-enabled spatial configuration review: a post-occupancy museum case**, by Fan Huang, Yan Zhu and Jia Ning Luo. This repository accompanies a revised manuscript; it does not imply publication or acceptance.

## Start here
- **Supplementary data/Read me.txt** explains the de-identified ratings, source conflicts, item-specific denominators and sensitivity bounds.
- Run **Supplementary data/Recalculate results.py** with Python 3 to reproduce the reported statistical summaries.
- **VR reproduction/Reproduction guide.txt** explains source recovery, controller mappings, installation and the checks completed on 6 November 2026.
- Download and extract **Yantai VR - Unity source.zip** to inspect the complete retained scene and source. **Yantai VR - Archived Windows build.zip** contains the archived application and runtime data.
- **Figures/** contains analytical diagrams and plots. Photographs of participants, identifying questionnaire scans and the unpublished manuscript are not included.

## Verification status
The recovered project was imported and compiled in Unity 2022.3.62f3c1, compared with recorded original version 2022.3.53f1c1. The scene audit found no missing scripts and confirmed all three manipulation targets. The archived executable started in a headless smoke test but could not initialize a headset. The author confirms that headset/controller functions were tested and worked normally during the original work. Hardware interaction has not been revalidated in the current environment.

Historical package/shader logs, the present-day audit and a future hardware-verification template are distinct records. No missing historical design trajectory or participant observation has been fabricated. The paper compares retained design endpoints and describes questionnaire responses; it does not establish an isolated causal advantage of VR.

## Rights and citation
Existing third-party notices and licences are retained; see VR reproduction/Third-party notices.txt. No blanket relicensing of Unity, Valve, model or other third-party material is intended. Cite the eventual published article when available; until then identify this repository version and its commit. No DOI or acceptance status is claimed.
