import time

import httpx

from app.config import settings

TDX_AUTH_URL = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
TDX_BASE_URL = "https://tdx.transportdata.tw/api/basic"


class TDXClient:
    def __init__(self):
        self._token: str | None = None
        self._token_expires_at: float = 0
        self._client = httpx.AsyncClient(timeout=30.0)

    async def _ensure_token(self):
        if self._token and time.time() < self._token_expires_at - 60:
            return
        resp = await self._client.post(
            TDX_AUTH_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": settings.TDX_CLIENT_ID,
                "client_secret": settings.TDX_CLIENT_SECRET,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        self._token = data["access_token"]
        self._token_expires_at = time.time() + data.get("expires_in", 3600)

    async def _get(self, path: str, params: dict | None = None) -> dict | list:
        await self._ensure_token()
        resp = await self._client.get(
            f"{TDX_BASE_URL}{path}",
            headers={
                "Authorization": f"Bearer {self._token}",
                "Accept-Language": "zh-TW",
            },
            params=params,
        )
        resp.raise_for_status()
        return resp.json()

    async def get_live_delays(self) -> list[dict]:
        """Get real-time delay info for all running trains."""
        return await self._get("/v2/Rail/TRA/LiveTrainDelay", params={"$format": "JSON"})

    async def get_alerts(self) -> list[dict]:
        """Get service alerts (cancellations, disruptions)."""
        return await self._get("/v2/Rail/TRA/Alert", params={"$format": "JSON"})

    async def get_daily_timetable(self, train_date: str) -> list[dict]:
        """Get full timetable for a specific date (YYYY-MM-DD)."""
        return await self._get(
            f"/v2/Rail/TRA/DailyTimetable/TrainDate/{train_date}",
            params={"$format": "JSON"},
        )

    async def get_daily_timetable_by_train(self, train_no: str) -> list[dict]:
        """Get today's timetable for a specific train number."""
        return await self._get(
            f"/v2/Rail/TRA/DailyTimetable/TrainNo/{train_no}/Today",
            params={"$format": "JSON"},
        )

    async def get_stations(self) -> list[dict]:
        """Get all TRA stations."""
        return await self._get("/v2/Rail/TRA/Station", params={"$format": "JSON"})

    async def get_train_types(self) -> list[dict]:
        """Get all train type codes."""
        return await self._get("/v2/Rail/TRA/TrainType", params={"$format": "JSON"})

    async def close(self):
        await self._client.aclose()


tdx_client = TDXClient()
