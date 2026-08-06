# SpendWise – Personal Finance Analytics Platform

A production-style full-stack personal finance application with REST API + analytics dashboard.

**Track income & expenses • Auto-categorize bank statements • Visualize spending insights**

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)
![Docker](https://img.shields.io/badge/Docker-ready-blue)
![CI](https://github.com/Satyam-2004/spendwise/actions/workflows/ci.yml/badge.svg)

---

## Features

| Feature | Description |
|---------|-------------|
| **JWT Authentication** | Secure register / login |
| **Transaction CRUD** | Add, edit, delete income & expenses |
| **Smart Categories** | 15 default categories created on signup |
| **CSV Import** | Upload bank statements → auto-import + keyword-based categorization |
| **Analytics** | Summary, category breakdown, monthly trends |
| **Dashboard** | Streamlit frontend for visual demo |
| **Dockerized** | One-command setup with PostgreSQL |
| **CI** | GitHub Actions for syntax/import checks |

---

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, Pydantic, JWT (python-jose), Passlib
- **Database**: PostgreSQL 16
- **Frontend / Demo**: Streamlit
- **Data**: Pandas
- **DevOps**: Docker, docker-compose, Github Actions, Render

---

## Live Demo

| Service | URL |
|---------|-----|
| **API** | https://spendwise-api-umej.onrender.com |
| **Swagger Docs** | https://spendwise-api-umej.onrender.com/docs |
| **Health Check** | https://spendwise-api-umej.onrender.com/health |

> Note: Free-tier Render services may take 30–50 seconds to wake up on the first request.

---

## Quick Start

### Prerequisites
- Docker & Docker Compose

### Run the full stack

```bash
git clone https://github.com/Satyam-2004/spendwise.git
cd spendwise
docker-compose up --build
```

| Service | URL |
|---------|-----|
| API | http://localhost:8000 |
| Interactive Docs (Swagger) | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |

### Run the Dashboard (optional)

```bash
pip install streamlit requests
streamlit run dashboard.py
```

### Seed demo data

```bash
# After API is running
python scripts/seed_demo_data.py
```

Demo login:
- Email: `demo@spendwise.app`
- Password: `demo1234`

---

## API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Create account + default categories |
| POST | `/api/auth/login` | Get JWT token |

### Transactions
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/transactions/` | Create transaction |
| GET | `/api/transactions/` | List (filter by type, category, date) |
| PATCH | `/api/transactions/{id}` | Update |
| DELETE | `/api/transactions/{id}` | Delete |
| POST | `/api/transactions/import-csv` | Upload bank CSV |
| GET/POST | `/api/transactions/categories` | Manage categories |

### Analytics
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/analytics/summary` | Income, expense, savings rate |
| GET | `/api/analytics/by-category` | Breakdown by category |
| GET | `/api/analytics/monthly-trend` | Last N months trend |

---

## Project Structure

```
spendwise/
├── app/
│   ├── api/              # Route handlers (auth, transactions, analytics)
│   ├── core/             # Security, JWT, dependencies
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic request/response models
│   ├── services/         # Business logic (categories, CSV import)
│   ├── config.py
│   ├── database.py
│   └── main.py
├── scripts/
│   └── seed_demo_data.py
├── dashboard.py          # Streamlit frontend
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## Key Implementation Highlights

- Clean architecture – separation of models, schemas, routes, services
- JWT auth with password hashing (bcrypt)
- Auto-categorization on CSV import using keyword matching (Swiggy → Food, Uber → Transport, etc.)
- Flexible CSV parser – supports common bank statement column names
- Analytics powered by SQL aggregations (SUM, GROUP BY, date extraction)
- Docker Compose with healthchecks and volume persistence

---

## Possible Extensions

- Budget goals & alerts
- Recurring transactions
- Multi-currency support
- PDF report export
- React frontend
- Unit & integration tests

---

## Author

**Satyam Pravinkumar Sharma**  
BCA · Manipal University Jaipur  
GitHub: https://github.com/Satyam-2004  
LinkedIn: https://linkedin.com/in/satyam-pravinkumar-sharma  
Email: skpsharma2004@gmail.com

---

## License

MIT
