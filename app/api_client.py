"""CivicPulse API Client
Handles all HTTP communication between the Streamlit frontend and the FastAPI backend.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
import requests
from requests.exceptions import ConnectionError, HTTPError, RequestException, Timeout

from app.config import API_TIMEOUT_SECONDS, CIVICPULSE_API_URL


class CivicPulseClient:
    """Client for interacting with the CivicPulse FastAPI backend."""

    def __init__(self, base_url: str = CIVICPULSE_API_URL, timeout: int = API_TIMEOUT_SECONDS):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    # -------------------------------------------------------------------------
    # Internal Request Helper
    # -------------------------------------------------------------------------
    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None
    ) -> Tuple[Optional[Any], Optional[str]]:
        """Executes HTTP request and returns (result_json, error_message)."""
        url = f"{self.base_url}{path}"
        try:
            response = requests.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                timeout=self.timeout
            )
            if response.status_code in (200, 201):
                try:
                    return response.json(), None
                except ValueError:
                    return response.text, None
            else:
                detail = f"Status {response.status_code}"
                try:
                    res_json = response.json()
                    if isinstance(res_json, dict) and "detail" in res_json:
                        detail = str(res_json["detail"])
                except Exception:
                    detail = response.text or detail
                return None, f"API Error ({response.status_code}): {detail}"
        except ConnectionError:
            return None, f"Could not connect to CivicPulse backend at {self.base_url}. Ensure uvicorn is running."
        except Timeout:
            return None, f"Request to {url} timed out after {self.timeout}s."
        except RequestException as e:
            return None, f"Network error communicating with CivicPulse backend: {str(e)}"

    # -------------------------------------------------------------------------
    # Health & System
    # -------------------------------------------------------------------------
    def health_check(self) -> Tuple[bool, str]:
        """Checks if backend service is live and reachable."""
        data, err = self._request("GET", "/health")
        if err is None and data and data.get("status") == "healthy":
            return True, "Online"
        # Fallback to root endpoint check
        data, err = self._request("GET", "/")
        if err is None and data and "CivicPulse" in str(data):
            return True, "Online"
        return False, err or "Backend unreachable"

    # -------------------------------------------------------------------------
    # Complaints Core
    # -------------------------------------------------------------------------
    def create_complaint(
        self,
        citizen_id: int,
        description: str,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        skip_ai: bool = False
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Submits a new grievance (POST /complaints)."""
        payload = {
            "citizen_id": citizen_id,
            "description": description,
            "latitude": latitude,
            "longitude": longitude
        }
        params = {"skip_ai": skip_ai}
        return self._request("POST", "/complaints", params=params, json_data=payload)

    def get_complaint(
        self,
        complaint_identifier: Union[int, str]
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Retrieves comprehensive details for a complaint by ID or complaint number."""
        ident = str(complaint_identifier).strip()
        return self._request("GET", f"/complaints/{ident}")

    def list_complaints(
        self,
        department_id: Optional[int] = None,
        ward_id: Optional[int] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        category: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 200,
        skip: int = 0
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Lists complaints matching filter criteria."""
        params: Dict[str, Any] = {"limit": limit, "skip": skip}
        if department_id:
            params["department_id"] = department_id
        if ward_id:
            params["ward_id"] = ward_id
        if status and status.upper() != "ALL":
            params["status"] = status
        if priority and priority.upper() != "ALL":
            params["priority"] = priority
        if category and category.upper() != "ALL":
            params["category"] = category
        if search:
            params["search"] = search

        return self._request("GET", "/complaints", params=params)

    def update_status(
        self,
        complaint_id: int,
        new_status: str,
        performed_by: str = "Officer",
        remarks: str = ""
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Transitions complaint status (POST /complaints/{id}/status)."""
        payload = {
            "new_status": new_status,
            "performed_by": performed_by,
            "remarks": remarks
        }
        return self._request("POST", f"/complaints/{complaint_id}/status", json_data=payload)

    def submit_feedback(
        self,
        complaint_id: int,
        rating: int,
        comments: Optional[str] = None,
        resolution_accepted: bool = True
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Submits citizen satisfaction rating (POST /complaints/{id}/feedback)."""
        payload = {
            "rating": rating,
            "comments": comments,
            "resolution_accepted": resolution_accepted
        }
        return self._request("POST", f"/complaints/{complaint_id}/feedback", json_data=payload)

    # -------------------------------------------------------------------------
    # Metadata & Lookups
    # -------------------------------------------------------------------------
    def get_departments(self) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """Fetches list of municipal departments."""
        data, err = self._request("GET", "/departments")
        return (data or []), err

    def get_wards(self) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """Fetches list of municipal wards."""
        data, err = self._request("GET", "/wards")
        return (data or []), err

    def get_officers(self) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """Fetches municipal officers."""
        data, err = self._request("GET", "/officers")
        return (data or []), err

    def get_citizens(self) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """Fetches registered citizens."""
        data, err = self._request("GET", "/citizens")
        return (data or []), err

    def get_analytics_summary(self) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Fetches high-level executive analytics summary."""
        return self._request("GET", "/analytics/summary")

    # -------------------------------------------------------------------------
    # Autonomous Agents & Automation Endpoints
    # -------------------------------------------------------------------------
    def process_complaint(
        self,
        complaint_id: int
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Runs the LangGraph multi-agent orchestration for a grievance."""
        payload = {"complaint_id": complaint_id}
        return self._request("POST", "/automation/process-complaint", json_data=payload)

    def check_sla(
        self,
        complaint_id: int
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Checks SLA status for a complaint."""
        payload = {"complaint_id": complaint_id}
        return self._request("POST", "/automation/sla-check", json_data=payload)

    def monitor_sla(
        self,
        complaint_id: int
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Triggers SLA monitoring agent for a complaint."""
        payload = {"complaint_id": complaint_id}
        return self._request("POST", "/automation/sla-monitor", json_data=payload)

    def escalate_complaint(
        self,
        complaint_id: int,
        reason: str
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Triggers escalation of a complaint."""
        payload = {"complaint_id": complaint_id, "reason": reason}
        return self._request("POST", "/automation/escalate", json_data=payload)

    def send_notification(
        self,
        complaint_id: int,
        notification_type: str
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Dispatches an automated notification."""
        payload = {"complaint_id": complaint_id, "notification_type": notification_type}
        return self._request("POST", "/automation/notify", json_data=payload)

    def query_policy(
        self,
        query: str
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Queries the RAG Policy agent with synthetic municipal bylaws."""
        payload = {"query": query}
        return self._request("POST", "/automation/policy-query", json_data=payload)

    def get_active_complaints(self) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Retrieves active complaints with live SLA monitoring flags."""
        return self._request("GET", "/automation/active-complaints")


# Shared singleton instance
api_client = CivicPulseClient()
