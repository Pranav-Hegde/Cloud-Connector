import os
from contextlib import asynccontextmanager
from typing import List, Optional, Any, Dict
from fastapi import FastAPI, HTTPException, Header, Query, Depends
from pydantic import BaseModel, ConfigDict
from dotenv import load_dotenv

from fastapi.middleware.cors import CORSMiddleware

from github_client import GitHubClient, GitHubAPIError

# Load environment variables
load_dotenv()

# Initialize FastAPI app
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Potential startup logic
    yield

app = FastAPI(
    title="GitHub Connector Tool",
    description="A FastAPI-based connector that fetches and manages GitHub repositories and issues.",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration settings (preferring environment variables)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Models for request validation
class IssueCreate(BaseModel):
    owner: str
    repo: str
    title: str
    body: Optional[str] = None
    model_config = ConfigDict(populate_by_name=True)

class PullRequestCreate(BaseModel):
    owner: str
    repo: str
    title: str
    head: str  # The name of the branch where your changes are implemented.
    base: str  # The name of the branch you want your changes pulled into.
    body: Optional[str] = None
    model_config = ConfigDict(populate_by_name=True)

# Function to get client from headers or default token
def get_client(token: Optional[str] = Header(None)) -> GitHubClient:
    effective_token = token if token else GITHUB_TOKEN
    if not effective_token:
        raise HTTPException(
            status_code=401, 
            detail="GitHub token is required. Provide it as 'token' header or set 'GITHUB_TOKEN' env var."
        )
    return GitHubClient(effective_token)

@app.get("/", tags=["Home"])
async def root():
    return {"message": "GitHub Cloud Connector is running", "endpoints": ["/repos", "/issues", "/create-issue", "/commits", "/create-pr"]}

@app.get("/repos", tags=["GitHub Actions"])
async def get_repositories(
    username: Optional[str] = Query(None, description="GitHub username or organization to fetch repos for. Defaults to authenticated user."),
    client: GitHubClient = Depends(get_client)
):
    """Fetch repositories for a user or an organization."""
    try:
        repos = await client.get_user_repos(username)
        # Select key fields for cleaner output
        return [{"name": r["name"], "full_name": r["full_name"], "url": r["html_url"], "language": r.get("language")} for r in repos]
    except GitHubAPIError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/issues", tags=["GitHub Actions"])
async def list_issues(
    owner: str = Query(..., description="The owner of the repository."),
    repo: str = Query(..., description="The name of the repository."),
    client: GitHubClient = Depends(get_client)
):
    """List issues from a specific repository."""
    try:
        issues = await client.list_issues(owner, repo)
        return [{"id": i["id"], "number": i["number"], "title": i["title"], "state": i["state"], "user": i["user"]["login"]} for i in issues]
    except GitHubAPIError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/create-issue", tags=["GitHub Actions"])
async def create_new_issue(
    issue_data: IssueCreate,
    client: GitHubClient = Depends(get_client)
):
    """Create a new issue in a specific repository."""
    try:
        issue = await client.create_issue(
            owner=issue_data.owner, 
            repo=issue_data.repo, 
            title=issue_data.title, 
            body=issue_data.body
        )
        return {"message": "Issue created successfully", "issue_url": issue["html_url"]}
    except GitHubAPIError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/commits", tags=["GitHub Actions"])
async def get_commits(
    owner: str = Query(..., description="The owner of the repository."),
    repo: str = Query(..., description="The name of the repository."),
    client: GitHubClient = Depends(get_client)
):
    """Fetch commits from a repository."""
    try:
        commits = await client.get_commits(owner, repo)
        return [{"sha": c["sha"], "author": c["commit"]["author"]["name"], "message": c["commit"]["message"], "date": c["commit"]["author"]["date"]} for c in commits]
    except GitHubAPIError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/create-pr", tags=["GitHub Actions (Bonus)"])
async def create_pull_request(
    pr_data: PullRequestCreate,
    client: GitHubClient = Depends(get_client)
):
    """Create a new pull request in a specific repository."""
    try:
        pr = await client.create_pull_request(
            owner=pr_data.owner, 
            repo=pr_data.repo, 
            title=pr_data.title, 
            head=pr_data.head, 
            base=pr_data.base, 
            body=pr_data.body
        )
        return {"message": "Pull request created successfully", "pr_url": pr["html_url"]}
    except GitHubAPIError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Allow port and host to be configurable
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "127.0.0.1")
    uvicorn.run(app, host=host, port=port)
