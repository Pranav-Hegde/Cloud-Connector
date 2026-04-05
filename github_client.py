import httpx
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class GitHubAPIError(Exception):
    """Custom exception to handle GitHub API errors with status codes."""
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(self.message)

class GitHubClient:
    BASE_URL = "https://api.github.com"

    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }

    async def _request(self, method: str, path: str, **kwargs) -> Any:
        url = f"{self.BASE_URL}{path}"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(method, url, headers=self.headers, **kwargs)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
                raise GitHubAPIError(e.response.status_code, f"GitHub API error: {e.response.status_code} {e.response.text}")
            except httpx.RequestError as e:
                logger.error(f"Request error occurred while requesting {e.request.url!r}.")
                raise GitHubAPIError(503, "Network error while connecting to GitHub")

    async def get_user_repos(self, identifier: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch repositories for the authenticated user, another user, or an organization."""
        if not identifier:
            return await self._request("GET", "/user/repos")
        
        # GitHub uses different endpoints for users and orgs.
        # We first try fetching as a user, and if it's a 404, we try as an organization.
        try:
            return await self._request("GET", f"/users/{identifier}/repos")
        except GitHubAPIError as e:
            if e.status_code == 404:
                return await self._request("GET", f"/orgs/{identifier}/repos")
            raise

    async def list_issues(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """List issues from a specific repository."""
        path = f"/repos/{owner}/{repo}/issues"
        return await self._request("GET", path)

    async def create_issue(self, owner: str, repo: str, title: str, body: Optional[str] = None) -> Dict[str, Any]:
        """Create a new issue in a specific repository."""
        path = f"/repos/{owner}/{repo}/issues"
        data = {"title": title, "body": body}
        return await self._request("POST", path, json=data)

    async def get_commits(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """Fetch commits from a repository."""
        path = f"/repos/{owner}/{repo}/commits"
        return await self._request("GET", path)

    async def create_pull_request(self, owner: str, repo: str, title: str, head: str, base: str, body: Optional[str] = None) -> Dict[Dict[str, Any], Any]:
        """Create a new pull request."""
        path = f"/repos/{owner}/{repo}/pulls"
        data = {"title": title, "head": head, "base": base, "body": body}
        return await self._request("POST", path, json=data)
