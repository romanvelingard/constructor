# Future Roadmap: Persistent Meal Tracker

This document outlines the architectural plan for transitioning the **Food Planning Tool** from a lightweight in-memory prototype to a fully persistent, history-tracking meal tracker.

---

## 🎯 Primary Goals
1. **Persistence**: Eliminate data loss when the browser refreshes or the server restarts.
2. **History Tracking**: Keep track of daily protein intake and meal choices over time.
3. **Advanced Reporting**: Generate summaries and consistency metrics.

---

## 🛠️ Phase 1: Local SQLite Database
*Suitable for single-user running locally or on a single persistent server.*

### 1. Database Schema (SQLite)

#### Table: `foods`
Stores all protein sources, garnishes, and snacks.
| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | INTEGER (PK) | Unique food identifier |
| `name` | TEXT | Display name (unique) |
| `category` | TEXT | Category: `Протеин`, `Гарнир`, `Снэк` |
| `protein_density`| REAL | Grams of protein per 100g |

#### Table: `meal_plan`
Stores scheduled meal slots for each calendar date.
| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | INTEGER (PK) | Unique entry identifier |
| `date` | TEXT | ISO date string (`YYYY-MM-DD`) |
| `meal_type` | TEXT | `Обед`, `Ужин`, `Снэк` |
| `food_name` | TEXT | FK reference to `foods.name` or raw text |

#### Table: `shopping_checklist`
Stores checked item states for the grocery lists.
| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | INTEGER (PK) | Unique checkbox identifier |
| `item_key` | TEXT | Unique identifier for checked status (e.g. `chk_protein_Chicken_600`) |
| `is_checked` | INTEGER | `0` for false, `1` for true |

---

## ☁️ Phase 2: Cloud Database (Serverless Deployment)
*Required if deploying to serverless platforms like Google Cloud Run or Streamlit Cloud, where local SQLite database files are wiped on container shutdowns.*

### Recommended Options:
*   **Supabase (PostgreSQL)**: Offers a generous free tier with Postgres. We can connect using SQLAlchemy or Supabase's native Python SDK.
*   **Google Cloud Firestore / Firebase**: NoSQL database that works well for JSON-like documents and has a robust free tier.

---

## 📝 Implementation Tasks

- [ ] **Data Migration**:
  - Export current defaults (`proteins_db`, `garnishes_db`, `snacks_db`) into seed data SQL scripts.
- [ ] **Database Connection Setup**:
  - Write a `db.py` module to initialize connections, create tables, and handle CRUD transactions.
- [ ] **App Integration**:
  - Replace `st.session_state` storage for recipes, choices, and checklists with SQL lookup and update functions.
- [ ] **History Tab**:
  - Add a date picker calendar to view previous weeks' meal menus and intake metrics.
- [ ] **Reports Export**:
  - Generate copyable Markdown or downloadable PDF reports containing weekly nutrition statistics.
