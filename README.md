# Open-Source Code Review: AI Network Threat Detection Framework

## 🔍 Context & Research Objective
This repository serves as a **Threat Intelligence & Code Auditing Case Study**[span_1](start_span)[span_1](end_span). I discovered an automated network monitoring script utilizing `IsolationForest` and `tshark` during my monitoring of threat-intel nodes[span_2](start_span)[span_2](end_span). As an independent researcher, my objective is to reverse-engineer, document, and critically audit its structural workflows[span_3](start_span)[span_3](end_span).

## 🛠️ Code Audit Highlights
* **Shared Resource Hazard:** Identified a critical file-system race condition where asynchronous threads read/write to a single un-locked static file (`traffic.csv`)[span_4](start_span)[span_4](end_span).
* **Feature Constraints:** Highlighted the vulnerability of the 1-Dimensional volumetric feature space to slow-brute network techniques[span_5](start_span)[span_5](end_span).
* 
