from knowledge_compiler.output import AnalysisResult
from knowledge_compiler.models import Evidence, Claim
from ..database import get_database_connection


def save_analysis(
    result: AnalysisResult,
    connection=None,
) -> int:
    owns_connection = connection is None

    if owns_connection:
        connection = get_database_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO analyses (
                repository_path,
                schema_version,
                files_discovered,
                with_ai,
                analysis_limit
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                result.repository,
                result.schema_version,
                result.files_discovered,
                result.with_ai,
                result.limit
            )
        )

        if owns_connection:
            connection.commit()

        return cursor.lastrowid

    finally:
        cursor.close()

        if owns_connection:
            connection.close()


def save_evidence(
    analysis_id: int,
    evidence: list[Evidence],
    connection=None,
) -> list[int]:
    owns_connection = connection is None

    if owns_connection:
        connection = get_database_connection()

    try:
        cursor = connection.cursor()

        evidence_ids = []

        for item in evidence:
            cursor.execute(
                """
                INSERT INTO evidence (
                    analysis_id,
                    source,
                    kind,
                    description,
                    language,
                    line_start,
                    line_end,
                    content
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    analysis_id,
                    str(item.source),
                    item.kind,
                    item.description,
                    item.language,
                    item.line_start,
                    item.line_end,
                    item.content
                )
            )

            evidence_ids.append(cursor.lastrowid)

        if owns_connection:
            connection.commit()

        return evidence_ids

    finally:
        cursor.close()

        if owns_connection:
            connection.close()


def save_claims(
    analysis_id: int,
    claims: list[Claim],
    connection=None,
) -> list[int]:
    owns_connection = connection is None

    if owns_connection:
        connection = get_database_connection()

    try:
        cursor = connection.cursor()

        claim_ids = []

        for claim in claims:
            cursor.execute(
                """
                INSERT INTO claims (
                    analysis_id,
                    statement,
                    status,
                    confidence
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    analysis_id,
                    claim.statement,
                    claim.status,
                    claim.confidence
                )
            )

            claim_ids.append(cursor.lastrowid)

        if owns_connection:
            connection.commit()

        return claim_ids

    finally:
        cursor.close()

        if owns_connection:
            connection.close()


def save_claim_evidence(
    claim_id: int,
    evidence_ids: list[int],
    connection=None,
) -> None:
    owns_connection = connection is None

    if owns_connection:
        connection = get_database_connection()

    try:
        cursor = connection.cursor()

        for evidence_id in evidence_ids:
            cursor.execute(
                """
                INSERT INTO claim_evidence (
                    claim_id,
                    evidence_id
                )
                VALUES (%s, %s)
                """,
                (
                    claim_id,
                    evidence_id
                )
            )

        if owns_connection:
            connection.commit()

    finally:
        cursor.close()

        if owns_connection:
            connection.close()


def persist_analysis(result: AnalysisResult) -> int:
    connection = get_database_connection()

    try:
        analysis_id = save_analysis(
            result,
            connection,
        )

        evidence_ids = save_evidence(
            analysis_id,
            list(result.evidence),
            connection,
        )

        claim_ids = save_claims(
            analysis_id,
            list(result.claims),
            connection,
        )

        evidence_id_map = {
            evidence.id: database_id
            for evidence, database_id
            in zip(result.evidence, evidence_ids)
        }

        for claim, claim_id in zip(result.claims, claim_ids):
            database_evidence_ids = [
                evidence_id_map[evidence_id]
                for evidence_id in claim.evidence_ids
                if evidence_id in evidence_id_map
            ]

            save_claim_evidence(
                claim_id,
                database_evidence_ids,
                connection,
            )

        connection.commit()

        return analysis_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()