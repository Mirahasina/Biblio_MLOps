# Librairy - GitOps DevSecOps

Projet examen DevOps/MLOps : application CRUD **livres** (bibliothèque) déployée via GitOps (GitHub → ArgoCD → Kubernetes) avec Ingress SSL, Nginx et pipeline ETL Airflow.

**Domaine :** `www.librairy.lcl`  
**Devise :** Ariary (Ar)

## Architecture

```
Machine (dev)
    │
    ▼
Dossier projet - CRUD Livres (React + FastAPI/Uvicorn + PostgreSQL)
    │
    ▼
GitHub - CI/CD (build, scan sécurité, push images)
    │
    ▼
ArgoCD - GitOps (sync automatique des manifests K8S)
    │
    ▼
Kubernetes - Deployments, Services, Ingress SSL (www.librairy.lcl)
    │
    ▼
Job Airflow / CronJob - ETL (extract → filter → load)
```

## Stack technique

| Composant | Technologie |
|-----------|-------------|
| Frontend | React.js + Vite + Nginx |
| Backend | Python FastAPI + Uvicorn |
| Base de données | PostgreSQL 16 (`library`) |
| Orchestration | Kubernetes (K8S) |
| Namespace K8S | `librairy` |
| GitOps | ArgoCD |
| Ingress | NGINX Ingress Controller + SSL (`file.crt`) |
| Domaine local | `www.librairy.lcl` via `/etc/hosts` |
| CI/CD | GitHub Actions (DevSecOps + Trivy scan) |
| ETL | Apache Airflow DAG + CronJob K8S |
| Images Docker | `librairy-backend` / `librairy-frontend` |

## Structure du projet

```
projet_exam/
├── backend/              # API CRUD FastAPI + Uvicorn
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── database.py
│   │   └── routes/books.py
│   ├── scripts/seed_books.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/             # Interface CRUD React.js
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/BookCRUD.jsx
│   │   └── api/api.js
│   ├── Dockerfile
│   └── nginx.conf
├── k8s/                  # Manifests Kubernetes (namespace: librairy)
│   ├── namespace.yaml
│   ├── postgres/
│   ├── backend/
│   ├── frontend/
│   ├── ingress/          # Ingress + TLS pour www.librairy.lcl
│   └── airflow/          # CronJob ETL
├── argocd/               # Configuration ArgoCD GitOps
│   ├── application.yaml
│   └── project.yaml
├── airflow/dags/         # DAG ETL (extract → filter → load)
├── certs/                # Certificats SSL (CN=www.librairy.lcl)
│   ├── generate-certs.sh
│   ├── file.crt
│   └── file.key
├── .github/workflows/    # CI/CD DevSecOps
└── docker-compose.yaml   # Dev local
```

## Démarrage rapide (local)

### 1. Prérequis

- Docker & Docker Compose
- Node.js 20+ (dev frontend)
- Python 3.12+ (dev backend)

### 2. Lancer en local

```bash
docker compose up --build
```

- Frontend : http://localhost:3000
- Backend API : http://localhost:8000
- Swagger docs : http://localhost:8000/docs

### 3. Charger des données de test

```bash
python3 backend/scripts/seed_books.py
```

### 4. Dev sans Docker

```bash
# Backend
cd backend
pip install -r requirements.txt
DATABASE_URL=postgresql://library:library@localhost:5433/library \
  uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

> En Docker Compose, PostgreSQL est exposé sur le port **5433** (host).

## Déploiement Kubernetes

### 1. Configurer le domaine local

```bash
echo "127.0.0.1  www.librairy.lcl" | sudo tee -a /etc/hosts
```

### 2. Générer le certificat SSL

```bash
cd certs
./generate-certs.sh
```

### 3. Installer NGINX Ingress Controller

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.11.1/deploy/static/provider/cloud/deploy.yaml
```

### 4. Créer le secret TLS

```bash
kubectl create secret tls tls-secret \
  --cert=certs/file.crt \
  --key=certs/file.key \
  -n librairy
```

### 5. Déployer l'application

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/postgres/
kubectl apply -f k8s/backend/
kubectl apply -f k8s/frontend/
kubectl apply -f k8s/ingress/
kubectl apply -f k8s/airflow/
```

### 6. Accéder à l'application

```
https://www.librairy.lcl
```

## GitOps avec ArgoCD

### 1. Installer ArgoCD

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

### 2. Appliquer l'Application ArgoCD

Vérifier `argocd/application.yaml` (repo GitHub + namespace `librairy`), puis :

```bash
kubectl apply -f argocd/application.yaml
kubectl apply -f argocd/project.yaml
```

ArgoCD synchronise automatiquement les manifests K8S depuis GitHub.

## CI/CD DevSecOps (GitHub Actions)

Le pipeline `.github/workflows/ci-cd.yaml` exécute :

1. **Scan sécurité** - Trivy (vulnérabilités CRITICAL/HIGH)
2. **Build & Push** - Images `librairy-backend` / `librairy-frontend` vers GHCR
3. **GitOps sync** - ArgoCD détecte les changements et redéploie

## Pipeline ETL (Airflow)

Le DAG `airflow/dags/etl_filter_dag.py` :

1. **Extract** - Lit tous les livres depuis PostgreSQL
2. **Filter** - Garde uniquement les livres disponibles avec prix > 0 (Ar)
3. **Load** - Insère dans la table `books_report`

Alternative K8S : CronJob `k8s/airflow/cronjob-etl.yaml` (exécution quotidienne à 2h).

## API CRUD Livres

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/books/` | Liste tous les livres |
| GET | `/api/books/{id}` | Détail d'un livre |
| POST | `/api/books/` | Créer un livre |
| PUT | `/api/books/{id}` | Modifier un livre |
| DELETE | `/api/books/{id}` | Supprimer un livre |
| GET | `/health` | Health check |

### Champs d'un livre

| Champ | Type | Description |
|-------|------|-------------|
| `title` | string | Titre du livre |
| `author` | string | Auteur |
| `isbn` | string | Numéro ISBN |
| `genre` | string | Genre (roman, science, etc.) |
| `price` | float | Prix en **Ariary (Ar)** |
| `available` | boolean | Disponible en bibliothèque |

## Auteur

Projet examen L3 INSI - DevOps / MLOps - Librairy (`www.librairy.lcl`)
