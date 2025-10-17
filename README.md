# PantryPal API (FastAPI)

Inventory + daily count workflow with approvals.

## Quickstart

```bash
# install
python -m venv venv && ./venv/Scripts/activate
pip install -r requirements.txt

# env
cp .env.example .env
# edit .env as needed

# db
alembic upgrade head

# seeds
python -m app.seed_users
python -m app.seed_items
python -m app.seed_counts

# run
uvicorn app.main:app --reload
