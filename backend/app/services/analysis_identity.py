from .redis_state import get_analysis_state
from .results import get_analysis

def resolve_database_id(analysis_id: str) -> int | None:
    state = get_analysis_state(analysis_id)

    if state:
        database_id = state.get("database_id")

        if database_id is not None:
            return int(database_id)

    try:
        database_id = int(analysis_id)
    except (TypeError, ValueError):
        return None

    analysis = get_analysis(database_id)

    if analysis is None:
        return None

    return database_id