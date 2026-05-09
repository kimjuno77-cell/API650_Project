# API 650 Tank Design Project - Team Handoff & Status Report

**Date:** 2025-12-08
**Version:** Phase 2.2 (Security & KDS Integrated)

## 1. Project Overview

This project is a Python-based **API 650 Storage Tank Design Calculator** with a Streamlit web interface. It allows users to perform API 650 (13th Ed) calculations for Shell, Roof, and Seismic/Wind loads, and compares them with Korean Design Standards (KDS).

### Key Features Implemented

- **Core Calculation**:
  - Shell Thickness (1-Foot Method, Variable Design Point Method logic draft).
  - Roof Design (Supported Cone).
  - Seismic Loads (API 650 Annex E).
  - Wind Loads (ASCE 7 / API 650).
- **Security System (`AuthManager.py`)**:
  - Role-based Access: **Admin** (Manage users) vs **User** (Design only).
  - Secure Login with Hashed Passwords.
  - Account Expiration & Renewal logic.
  - Source Code & Menu Protection (Streamlit menu hidden).
- **KDS Standards Integration (`Loads.py`)**:
  - **KDS 41 12 00**: Korean Wind Load calculation (comparative).
  - **KDS 41 17 00**: Korean Seismic Load calculation (comparative).
  - UI Toggle & Comparison Table in Results.

## 2. Current Architecture

- **`app.py`**: Main entry point. Handles UI (Streamlit), Session State, Authentication, and orchestration of modules.
- **`AuthManager.py`**: Handles user credentials (`auth.json`), login checks, password hashing.
- **`Loads.py`**: Contains `WindLoad`, `SeismicLoad`, `KDSWindLoad`, `KDSSeismicLoad` classes.
- **`Shell_Design.py`**: Logic for Shell Course thickness and weight.
- **`Roof_Design.py`**: Logic for Roof Plate and Structure.
- **`InputReader.py`**: Excel/JSON data handling.

## 3. Completed Features (Phase 3)

The following tasks have been completed as of 2025-12-10:

### A. Advanced Roof Design

- [x] **Self-Supported Cone Roof** (API 650 5.10.5).
- [x] **Dome/Umbrella Roof** (API 650 5.10.6).
- [x] **Structure Analysis** (Rafter/Girder loads).

### B. Venting Design (API 2000 7th Ed)

- [x] **Logic Implementation**: `Venting_Design.py` covers Normal Inbreathing/Outbreathing and Emergency Venting.
- [x] **UI Integration**: Tab 3 displays detailed venting requirements.

### C. Wind Girder & Nozzles

- [x] **Wind Girder**: Intermediate Stiffener calculation and Section Recommendation (Angle/Channel).
- [x] **Nozzle Schedule**: Interactive editor, Reinforcement Area check (A_req vs A_avail).

### D. Refinements & Viz (Latest)

- [x] **Seismic Graph**: Dual plot (API vs KDS) with distinct colors.
- [x] **Seismic Hoop Stress**: Implemented API 650 E.6.2.4 check with Max(KDS, API) logic.
- [x] **Shell Method**: Explicit reporting of equations (VDM/1-Foot/Annex S).
- [x] **Visualization**: SVG Crash fixed (`MediaFileStorageError` resolved).

## 4. Maintenance Notes

- **Indentation**: Python is sensitive to indentation. `app.py` has been patched multiple times. Ensure any future direct edits respect the block structure (especially mixed 4-space vs 8-space indentations).
- **Auth Credentials**:
  - Admin: `admin` / `[HIDDEN]`
  - User: `user` / `[HIDDEN]`
  - Data stored in `c:\Users\User\Desktop\API650_Project\auth.json`.
- **KDS Logic**: Currently uses simplified coefficients. For certified design, integration with detailed Map Data/Tables is recommended.

## 5. How to Run

```bash
cd c:\Users\User\Desktop\API650_Project
python -m streamlit run app.py
```
