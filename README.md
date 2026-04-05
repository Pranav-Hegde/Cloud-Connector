# GitHub Cloud Connector

A simple, modular cloud connector to GitHub built with **Python 3.12** and **FastAPI**. This project demonstrates the ability to integrate with external APIs, handle authentication securely, and expose usable REST actions.

## Features

- **Authentication**: Supports GitHub Personal Access Token (PAT).
- **Core API Integration**:
  - Fetch repositories for any user/organization.
  - List issues from a specific repository.
  - Create a new issue in a specific repository.
  - Fetch recent commits from a repository.
- **REST Interface**: Clean, easy-to-use API endpoints with proper error handling and Pydantic validation.

## Prerequisites

- **Python 3.12+**
- **GitHub Personal Access Token (PAT)**: [Generate one here](https://github.com/settings/tokens) with `repo` scope if you want to create issues.

## Setup Instructions

1.  **Clone the repository** (if applicable) or navigate to the project directory.
2.  **Create a Virtual Environment**:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate  # Windows
    # source venv/bin/activate # Linux/macOS
    ```
3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure Environment Variables**:
    - Copy `.env.example` to `.env`:
      ```bash
      cp .env.example .env
      ```
    - Open `.env` and replace `your_personal_access_token_here` with your actual GitHub PAT.

## Running the Project

Run the application using Uvicorn:

```bash
python main.py
```

The server will start at `http://127.0.0.1:8000`.

## API Endpoints

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/repos` | `GET` | Fetch repositories for a user. (Query Param: `username`) |
| `/issues` | `GET` | List issues from a repository. (Query Params: `owner`, `repo`) |
| `/create-issue` | `POST` | Create a new issue. (Body: `owner`, `repo`, `title`, `body`) |
| `/commits` | `GET` | Fetch commits from a repository. (Query Params: `owner`, `repo`) |
| `/create-pr` | `POST` | Create a new pull request. **(Bonus Feature)** |

### Interactive Documentation

Once the server is running, visit:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## Security

The application ensures the token is handled securely by loading it from environment variables using `python-dotenv`. No sensitive credentials are hardcoded.

## Error Handling

Standard HTTP status codes are used to communicate API failures (e.g., `401` for unauthorized, `404` for not found, `400` for bad requests).
