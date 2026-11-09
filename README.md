# Yantai VR spatial configuration review

Research materials for *Editing linked spaces in virtual reality: A museum study of layout and representation*, by Fan Huang, Yan Zhu and Jia Ning Luo.

The participant study includes 15 architecture students and 15 anonymous architectural experts. The repository contains anonymous ratings, descriptive summaries, CAD plans, graph attributes, analytical figures, the VR prototype and instructions for reproducing the paper’s analyses.

Table 5 presents high-rating counts for each of the eleven scheme and tool items (Q10–20), with separate columns for students and experts and a pooled count. Figures 9 and 10 show the distributions for the two groups on identical count axes. Expert rating sensitivity by item.csv gives an alternate tabulation for the same experts. Run **Joint circulation and display ratings.py** to reproduce the Q10–Q11 overlap and its bounds. A high Q17 score indicates physical discomfort.

## Reproduction

From **Supplementary data**, first run **Check landmark visibility.py** (Python 3.10+) to generate the local medians used in Figure 4, grid membership and the alternate-tread check. Then run **paper_ratings.py** for Tables 4–6, **Spatial measurements.py** for the geometric and graph comparisons, and **Generate analytical figures.py** for Figures 1, 4 and 7–10. The figure script requires NumPy and Matplotlib. Run **Check spatial and paired relationships.py** (Python 3.10 or later) to reproduce the within-plan rank correlations and the full-cohort bounds on paired rating directions. The numerical analyses use the Python standard library. See **Read me.txt** for definitions, denominators and study conditions.

**VR reproduction/Reproduction guide.txt** covers the Unity project, the archived Windows build, controller mappings and checks. Third-party licences are retained. **Checksums.csv** provides file hashes. The repository accompanies a manuscript and does not imply acceptance or publication.
