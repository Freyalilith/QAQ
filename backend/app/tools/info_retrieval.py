"""InfoRetrievalTool — controlled external retrieval (issue #13).

"Default no web" means: do not call web search / browser / external retrieval
unless the turn needs a time-sensitive external fact (weather, air quality, …).
It does NOT mean "no LLM" — companion language generation still uses the LLM
provider.

In DEMO_MODE this returns deterministic mock facts (offline, no network). With
``DEMO_MODE=false`` + ``RETRIEVAL_PROVIDER=open_meteo`` it fetches **real**
weather / air quality from Open-Meteo (free, no API key) for the configured
location, and falls back to the mock if the call fails — so the turn never
breaks.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import httpx

logger = logging.getLogger(__name__)

# Strong, standalone weather/air signals.
_WEATHER_KW = (
    "天气", "气温", "下雨", "会不会下雨", "出太阳", "紫外线", "冷不冷",
    "热不热", "要不要带伞",
)
_AIR_KW = ("空气质量", "空气好", "雾霾", "pm2.5", "pm2", "污染", "aqi")
# Outdoor-activity words count as a weather query ONLY with a time/weather
# context, so companionship / reminiscence ("我喜欢散步" / "我年轻时每天散步")
# do not trigger retrieval, while "今天下午适合散步吗" still does.
_OUTDOOR_KW = ("散步", "出门", "出去", "走走", "遛弯")
_OUTDOOR_CONTEXT = (
    "今天", "明天", "下午", "上午", "早上", "晚上", "现在", "适合", "天气",
    "外面", "会不会", "气温",
)

# Provider names that select the real Open-Meteo retrieval.
_REAL_PROVIDER_NAMES = {"open_meteo", "openmeteo", "open-meteo", "real"}

# WMO weather codes → short zh descriptions (Open-Meteo `weather_code`).
_WMO_CODES = {
    0: "晴", 1: "大致晴朗", 2: "多云", 3: "阴",
    45: "有雾", 48: "有雾",
    51: "小毛毛雨", 53: "毛毛雨", 55: "较大毛毛雨", 56: "冻毛毛雨", 57: "冻毛毛雨",
    61: "小雨", 63: "中雨", 65: "大雨", 66: "冻雨", 67: "冻雨",
    71: "小雪", 73: "中雪", 75: "大雪", 77: "雪粒",
    80: "小阵雨", 81: "阵雨", 82: "强阵雨", 85: "小阵雪", 86: "阵雪",
    95: "雷阵雨", 96: "雷阵雨伴冰雹", 99: "强雷阵雨伴冰雹",
}


def _query_kind(text: str) -> str:
    haystack = text or ""
    if any(k in haystack for k in _AIR_KW):
        return "air_quality"
    if any(k in haystack for k in _WEATHER_KW):
        return "weather"
    if any(o in haystack for o in _OUTDOOR_KW) and any(
        c in haystack for c in _OUTDOOR_CONTEXT
    ):
        return "weather"
    return "generic"


def _aqi_label(aqi: float) -> str:
    if aqi <= 50:
        return "优"
    if aqi <= 100:
        return "良"
    if aqi <= 150:
        return "轻度污染"
    if aqi <= 200:
        return "中度污染"
    if aqi <= 300:
        return "重度污染"
    return "严重污染"


@dataclass
class RetrievalResult:
    found: bool
    summary: str
    source: str
    mock: bool
    query_kind: str


class InfoRetrievalTool:
    name = "InfoRetrievalTool"

    def __init__(
        self,
        provider: str = "mock",
        *,
        demo_mode: bool = True,
        lat: float = 22.3193,
        lon: float = 114.1694,
        location: str = "香港",
        timeout: float = 10.0,
    ):
        self.provider = provider
        self._demo_mode = demo_mode
        self._lat = lat
        self._lon = lon
        self._location = location
        self._timeout = timeout

    @staticmethod
    def is_retrieval_query(text: str) -> bool:
        """True only for time-sensitive external facts (weather / air quality).

        Emotional disclosure, reminiscence, reminders, and memory chat are NOT
        retrieval queries — an outdoor word alone (散步/出门) does not count.
        """
        return _query_kind(text) != "generic"

    def _use_real(self) -> bool:
        # DEMO_MODE always stays offline (mock), like the LLM/voice providers.
        return not self._demo_mode and self.provider.strip().lower() in _REAL_PROVIDER_NAMES

    def retrieve(self, query: str) -> RetrievalResult:
        kind = _query_kind(query)
        if kind == "generic":
            return RetrievalResult(
                found=False,
                summary="暂时没有查到相关的实时信息。",
                source="none",
                mock=not self._use_real(),
                query_kind="generic",
            )
        if self._use_real():
            try:
                return self._fetch_real(kind)
            except Exception:
                logger.warning(
                    "retrieval provider %r failed; falling back to the mock fact.",
                    self.provider,
                )
        return self._mock(kind)

    # --- real (Open-Meteo) ---------------------------------------------------

    def _fetch_real(self, kind: str) -> RetrievalResult:
        if kind == "air_quality":
            data = self._get(
                "https://air-quality-api.open-meteo.com/v1/air-quality",
                {"latitude": self._lat, "longitude": self._lon,
                 "current": "pm2_5,us_aqi", "timezone": "auto"},
            )
            cur = data["current"]
            aqi = round(cur["us_aqi"])
            pm25 = round(cur["pm2_5"])
            return RetrievalResult(
                found=True,
                summary=(
                    f"{self._location}现在空气质量{_aqi_label(aqi)}"
                    f"（AQI 约 {aqi}，PM2.5 约 {pm25}）。"
                ),
                source="open_meteo_air_quality",
                mock=False,
                query_kind="air_quality",
            )
        # weather
        data = self._get(
            "https://api.open-meteo.com/v1/forecast",
            {"latitude": self._lat, "longitude": self._lon,
             "current": "temperature_2m,apparent_temperature,precipitation,"
             "weather_code,wind_speed_10m", "timezone": "auto"},
        )
        cur = data["current"]
        desc = _WMO_CODES.get(int(cur["weather_code"]), "天气一般")
        temp = round(cur["temperature_2m"])
        feels = round(cur["apparent_temperature"])
        wind = round(cur["wind_speed_10m"])
        rain = cur.get("precipitation", 0) or 0
        rain_note = "有降雨，出门记得带伞。" if rain > 0 else "目前没有降雨。"
        return RetrievalResult(
            found=True,
            summary=(
                f"{self._location}现在{desc}，气温约 {temp}°C（体感 {feels}°C），"
                f"风速约 {wind} km/h，{rain_note}"
            ),
            source="open_meteo_weather",
            mock=False,
            query_kind="weather",
        )

    def _get(self, url: str, params: dict) -> dict:
        response = httpx.get(url, params=params, timeout=self._timeout)
        response.raise_for_status()
        return response.json()

    # --- mock (offline) ------------------------------------------------------

    def _mock(self, kind: str) -> RetrievalResult:
        if kind == "air_quality":
            return RetrievalResult(
                found=True,
                summary="今天空气质量良好（AQI 约 60），适合短时间户外活动。",
                source="mock_air_quality",
                mock=True,
                query_kind="air_quality",
            )
        return RetrievalResult(
            found=True,
            summary="今天下午多云，气温约 22°C，微风，没有降雨，比较适合出门走走。",
            source="mock_weather",
            mock=True,
            query_kind="weather",
        )
