from backend.app.services import analysis_identity


def test_resolve_database_id_from_redis(monkeypatch):
    monkeypatch.setattr(
        analysis_identity,
        "get_analysis_state",
        lambda analysis_id: {"database_id": "42"},
    )

    result = analysis_identity.resolve_database_id("redis-analysis-id")

    assert result == 42


def test_resolve_database_id_from_analysis_id(monkeypatch):
    monkeypatch.setattr(
        analysis_identity,
        "get_analysis_state",
        lambda analysis_id: {},
    )
    monkeypatch.setattr(
        analysis_identity,
        "get_analysis",
        lambda database_id: {"id": database_id},
    )

    result = analysis_identity.resolve_database_id("42")

    assert result == 42


def test_resolve_database_id_invalid_analysis_id(monkeypatch):
    monkeypatch.setattr(
        analysis_identity,
        "get_analysis_state",
        lambda analysis_id: {},
    )

    result = analysis_identity.resolve_database_id("not-a-number")

    assert result is None


def test_resolve_database_id_analysis_not_found(monkeypatch):
    monkeypatch.setattr(
        analysis_identity,
        "get_analysis_state",
        lambda analysis_id: {},
    )
    monkeypatch.setattr(
        analysis_identity,
        "get_analysis",
        lambda database_id: None,
    )

    result = analysis_identity.resolve_database_id("42")

    assert result is None