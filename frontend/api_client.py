"""Unified API client for connecting to the SafeHome backend.

This module provides a combined API client that includes both common
and surveillance API functionality for backward compatibility.
"""

from .common_api_client import CommonAPIClient
from .surveillance_api_client import SurveillanceAPIClient


class APIClient(CommonAPIClient, SurveillanceAPIClient):
    """Unified client for making requests to the SafeHome backend API.

    This class combines CommonAPIClient and SurveillanceAPIClient
    to provide all API methods in a single interface.
    """

    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize the API client with base URL.

        Args:
            base_url: Base URL of the backend server
        """
        CommonAPIClient.__init__(self, base_url)
        SurveillanceAPIClient.__init__(self, base_url)
