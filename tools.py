from langchain.tools import tool


@tool
def get_recent_alerts() -> str:
    """Return recent infrastructure and third-party service alerts."""
    return """
Recent alerts:
- 10:04 UTC: Authentication provider latency increased sharply.
- 10:06 UTC: OAuth callback requests returning intermittent 503 errors.
- 10:07 UTC: New user sign-in completion rate dropped by 38%.
"""


@tool
def search_recent_deployments() -> str:
    """Return recent application deployments related to onboarding."""
    return """
Recent deployments:
- 09:42 UTC: web-onboarding v1.18.2 deployed.
- Change: invite acceptance route migrated from /accept-invite to /join.
- Known symptom: old email invite links may redirect to a missing route.
"""


@tool
def get_customer_reports() -> str:
    """Return recent customer complaints related to onboarding."""
    return """
Recent customer reports:
- Existing users can log in normally.
- Some invited users see a blank page after clicking invite links.
- Some new users report login timing out after accepting an invite.
"""


def agent_tools():
    return [
        get_recent_alerts,
        search_recent_deployments,
        get_customer_reports,
    ]
