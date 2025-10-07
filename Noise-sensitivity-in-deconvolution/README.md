# 📘 Waveform LiDAR Signal Deconvolution Analysis

This repository contains the results and visualizations from a series of experiments analyzing **noise sensitivity in waveform LiDAR signal deconvolution**. The primary goal is to determine the effects of noise for different deconvolution algorithms under varying noise and system response conditions.

---

## 🗂️ Repository Contents

### 1. `Signal Deconvolution Analysis Final.pptx`
- Contains the **final results and summarized findings** from all experiments.  
- Provides a concise overview of the comparative performance of different algorithms against different levels of noise and recommendations for selecting the boosting factor across various noise levels.  
- **Use this file for:** high-level summaries and conclusions.

---

### 2. `Waveform Lidar Signal Deconvolution Analysis (Harvard Forest Raw version).pptx`
- Includes **detailed experimental outcomes**, intermediate analyses, and raw visual results for each test condition.  
- Serves as a comprehensive reference with full result breakdowns and supporting figures.  
- **Use this file for:** in-depth analysis and validation of results.

---

### 3. `decon_analysis.ipynb`
- A Jupyter Notebook containing the **visualization code** used to analyze the experimental results.  
- Demonstrates how the **optimal boosting factor** varies between **noiseless** and **noisy system responses** for both **Richardson–Lucy** and **Gold deconvolution** algorithms.  

---

## 🧠 Summary
This repository provides both **summary-level** and **detailed** insights into how deconvolution performance depends on noise characteristics and algorithm parameters.  
It serves as a reference for **tuning deconvolution algorithms in waveform LiDAR signal processing** and supports reproducible analysis of noise-robust performance.

---

**Author:** Ramesh Bhatta  
**Affiliation:** Center for Imaging Science, Rochester Institute of Technology  
