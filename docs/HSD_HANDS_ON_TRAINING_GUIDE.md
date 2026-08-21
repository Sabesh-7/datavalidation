# Hands-On Training Guide: MoSPI HSD Data Validation Platform

## 🎓 Overview & Learning Objectives

Welcome to the **Household Survey Division (HSD) Data Validation Platform Hands-On Training Module**.

This training guide is designed for MoSPI field statistical officers, quality supervisors, and nodal officers. By completing this manual and interacting with the built-in **HSD Interactive Training Hub**, you will master:
1. Conducting real-time API and batch survey data ingestion.
2. Defining custom **Integrity Validation Rules** (Existential, Referential, Range, & Cross-field).
3. Utilizing **Unsupervised Machine Learning (Isolation Forest)** and **Statistical Distribution Analysis (Benford's Law)** to detect hidden anomalies.
4. Triaging, flagging, and inline-correcting data discrepancies in the **Validation Workbench**.
5. Generating compliance audit reports and exporting validated statistical datasets.

---

## 📚 Curriculum Structure

### 🔹 Module 1: Ingestion Management & Data Onboarding
- **Real-Time Streaming**: Ingest survey submissions via eSigma API connections.
- **Batch Processing**: Upload large historical dataset batches (CSV, Excel, Parquet).
- **Schema Auto-Validation**: Ensure data headers match national standard dictionary codes (NCO-2015, NIC-2008).

### 🔹 Module 2: Integrity Rule Construction
- **Existential Integrity**: Flag mandatory missing fields (e.g. Household Head ID missing).
- **Referential Integrity**: Validate occupation codes against NCO classifications.
- **Logical / Cross-Field Checks**:
  - `Rule 101`: `If Age < 15, Employment Status CANNOT be 'Employed'`.
  - `Rule 102`: `Total Household Monthly Income MUST BE >= Total Household Monthly Expenditure`.
  - `Rule 103`: `Number of household members MUST match total individual records submitted`.

### 🔹 Module 3: ML Anomaly Detection & Statistical Profiling
- **Isolation Forest Multivariate Outliers**: Identify subtle non-linear discrepancies in income-to-expenditure ratios across districts.
- **Benford's Law Digital Analysis**: Flag artificial or fabricated survey data by analyzing leading digit distributions.
- **District/State Aggregate Heatmaps**: Highlight enumerator clusters with unusually high error flags.

### 🔹 Module 4: The HSD Data Validation Workbench (Hands-On Operations)
1. Navigate to **Data Validation Workbench** (`/admin/data-validation`).
2. Run **Interactive Quick Check** on target survey samples.
3. Review the **Discrepancy Drawer** detailing Rule IDs, Violation Descriptions, and Severity Levels (Critical, High, Medium, Low).
4. Perform **Inline Correction** or **Supervisor Escalation / Overwrite** with compulsory audit justification comments.

### 🔹 Module 5: Performance Metrics & Audit Reporting
- Inspect **Data Quality Index (DQI)** gauge.
- Export verified dataset into **Parquet** format for official NSO data lake publication.
- Generate and download executive **PDF Quality & Audit Reports**.

---

## 🎯 Practical Exercise Scenarios

### Exercise 1: Handling Household Expenditure Discrepancies
- **Scenario**: In a Periodic Labour Force Survey (PLFS) sample, Household ID `HH-2026-9941` reports a monthly income of ₹12,000 but total monthly expenditure of ₹85,000 without debt/savings context.
- **Action**:
  1. Filter by `Severity: High` in the Validation Workbench.
  2. Select record `HH-2026-9941`.
  3. Inspect the cross-field flag `RULE_LOGICAL_INC_EXP`.
  4. Flag for Field Enumerator Re-verification or correct data entry typo with supervisor note.

---

## 📜 Compliance & Guidelines Checklist
- [x] Always record a clear audit justification comment when overriding an automated flag.
- [x] Verify that PII masking is enabled before exporting raw survey data.
- [x] Complete the interactive training module annually for HSD certification.
