from app.tools.info_retrieval import InfoRetrievalTool


def test_is_retrieval_query_for_weather_and_air():
    tool = InfoRetrievalTool()
    assert tool.is_retrieval_query("今天下午适合散步吗？") is True
    assert tool.is_retrieval_query("外面空气质量怎么样") is True


def test_is_not_retrieval_query_for_emotional_or_reminiscence():
    tool = InfoRetrievalTool()
    assert tool.is_retrieval_query("我今天有点孤单") is False
    assert tool.is_retrieval_query("我年轻时喜欢听粤剧") is False
    assert tool.is_retrieval_query("每天早上8点提醒我吃药") is False


def test_outdoor_word_alone_does_not_trigger():
    # Companionship / reminiscence about walking must NOT retrieve; only a
    # walking question with a time/weather context does.
    tool = InfoRetrievalTool()
    assert tool.is_retrieval_query("我喜欢散步") is False
    assert tool.is_retrieval_query("我年轻时每天散步") is False
    assert tool.is_retrieval_query("出去走走对身体好") is False
    assert tool.is_retrieval_query("今天下午适合散步吗") is True
    assert tool.is_retrieval_query("现在出门要带伞吗") is True


def test_retrieve_weather():
    result = InfoRetrievalTool().retrieve("今天下午适合散步吗？")
    assert result.found is True
    assert result.query_kind == "weather"
    assert result.source == "mock_weather"
    assert result.mock is True


def test_retrieve_air_quality():
    result = InfoRetrievalTool().retrieve("今天空气质量怎么样")
    assert result.query_kind == "air_quality"


def test_retrieve_generic_not_found():
    result = InfoRetrievalTool().retrieve("你好呀")
    assert result.found is False


# --- real provider (Open-Meteo); the HTTP call is stubbed (no real network) ---


def test_real_provider_gated_by_demo_mode():
    # DEMO_MODE stays offline (mock) even if a real provider is named.
    result = InfoRetrievalTool("open_meteo", demo_mode=True).retrieve("今天天气怎么样")
    assert result.mock is True
    assert result.source == "mock_weather"


def test_real_provider_weather_when_configured(monkeypatch):
    tool = InfoRetrievalTool("open_meteo", demo_mode=False, location="测试城")
    monkeypatch.setattr(
        tool,
        "_get",
        lambda url, params: {
            "current": {
                "temperature_2m": 21.4,
                "apparent_temperature": 22.0,
                "precipitation": 0,
                "weather_code": 2,
                "wind_speed_10m": 9,
            }
        },
    )
    result = tool.retrieve("今天下午适合散步吗")
    assert result.mock is False
    assert result.source == "open_meteo_weather"
    assert "测试城" in result.summary and "21" in result.summary


def test_real_provider_air_quality_when_configured(monkeypatch):
    tool = InfoRetrievalTool("open_meteo", demo_mode=False, location="测试城")
    monkeypatch.setattr(
        tool, "_get", lambda url, params: {"current": {"pm2_5": 12, "us_aqi": 42}}
    )
    result = tool.retrieve("今天空气质量怎么样")
    assert result.mock is False
    assert result.source == "open_meteo_air_quality"
    assert "优" in result.summary


def test_real_provider_falls_back_to_mock_on_error(monkeypatch):
    tool = InfoRetrievalTool("open_meteo", demo_mode=False)

    def boom(url, params):
        raise RuntimeError("network down")

    monkeypatch.setattr(tool, "_get", boom)
    result = tool.retrieve("今天天气怎么样")
    assert result.mock is True  # degraded to the offline mock, turn not broken
    assert result.source == "mock_weather"
