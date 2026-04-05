import pytest
from fastapi.testclient import TestClient
from main import app
from github_client import GitHubClient, GitHubAPIError
import unittest.mock as mock

client = TestClient(app)

@pytest.fixture
def mock_github_client():
    with mock.patch("main.GitHubClient") as mocked:
        yield mocked

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "GitHub Cloud Connector is running" in response.json()["message"]

def test_repos_endpoint_no_token():
    # Should fail with 401 if no token provided in env or header
    with mock.patch("main.GITHUB_TOKEN", None):
        response = client.get("/repos")
        assert response.status_code == 401
        assert "GitHub token is required" in response.json()["detail"]

def test_repos_endpoint_with_header_token(mock_github_client):
    mock_instance = mock_github_client.return_value
    mock_instance.get_user_repos = mock.AsyncMock(return_value=[
        {"name": "repo1", "full_name": "user/repo1", "html_url": "http://github.com/user/repo1", "language": "Python"}
    ])
    
    response = client.get("/repos", headers={"token": "fake-token"})
    assert response.status_code == 200
    assert response.json()[0]["name"] == "repo1"
    mock_github_client.assert_called_with("fake-token")

def test_repos_endpoint_organization(mock_github_client):
    mock_instance = mock_github_client.return_value
    mock_instance.get_user_repos = mock.AsyncMock(return_value=[
        {"name": "org-repo", "full_name": "org/org-repo", "html_url": "http://github.com/org/org-repo", "language": "JS"}
    ])
    
    response = client.get("/repos?username=google", headers={"token": "fake-token"})
    assert response.status_code == 200
    assert response.json()[0]["name"] == "org-repo"
    mock_instance.get_user_repos.assert_called_with("google")

def test_create_issue_endpoint(mock_github_client):
    mock_instance = mock_github_client.return_value
    mock_instance.create_issue = mock.AsyncMock(return_value={
        "html_url": "http://github.com/user/repo/issues/1"
    })
    
    payload = {
        "owner": "user",
        "repo": "repo",
        "title": "Test Issue",
        "body": "Test Body"
    }
    response = client.post("/create-issue", json=payload, headers={"token": "fake-token"})
    assert response.status_code == 200
    assert "Issue created successfully" in response.json()["message"]
    mock_instance.create_issue.assert_called_with(
        owner="user", repo="repo", title="Test Issue", body="Test Body"
    )

def test_error_handling_propagation(mock_github_client):
    mock_instance = mock_github_client.return_value
    mock_instance.get_commits = mock.AsyncMock(side_effect=GitHubAPIError(404, "Repository not found"))
    
    response = client.get("/commits?owner=user&repo=nonexistent", headers={"token": "fake-token"})
    assert response.status_code == 404
    assert "Repository not found" in response.json()["detail"]

def test_create_pr_bonus_feature(mock_github_client):
    mock_instance = mock_github_client.return_value
    mock_instance.create_pull_request = mock.AsyncMock(return_value={
        "html_url": "http://github.com/user/repo/pull/1"
    })
    
    payload = {
        "owner": "user",
        "repo": "repo",
        "title": "Test PR",
        "head": "feature",
        "base": "main",
        "body": "Test Body"
    }
    response = client.post("/create-pr", json=payload, headers={"token": "fake-token"})
    assert response.status_code == 200
    assert "Pull request created successfully" in response.json()["message"]
