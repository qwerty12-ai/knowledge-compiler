from ..database import get_database_connection

def get_analysis_claims(analysis_id: int) -> list[dict]:
    connection = get_database_connection()

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                id,
                statement,
                status,
                confidence,
                created_at
            FROM claims
            WHERE analysis_id = %s
            ORDER BY id ASC
            """,
            (analysis_id,)
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()

def get_claim_with_evidence(claim_id: int) -> dict | None:
    connection = get_database_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                c.id,
                c.analysis_id,
                c.statement,
                c.status,
                c.confidence,
                c.created_at
            FROM claims c
            WHERE c.id = %s
            """,
            (claim_id,),
        )

        claim = cursor.fetchone()

        if claim is None:
            return None

        cursor.execute(
            """
            SELECT
                e.id,
                e.source,
                e.kind,
                e.description,
                e.language,
                e.line_start,
                e.line_end,
                e.content,
                e.created_at
            FROM evidence e
            INNER JOIN claim_evidence ce
                ON ce.evidence_id = e.id
            WHERE ce.claim_id = %s
            ORDER BY e.id ASC
            """,
            (claim_id,),
        )

        claim["evidence"] = cursor.fetchall()

        return claim

    finally:
        cursor.close()
        connection.close()

def get_analysis_evidence(analysis_id: int) -> list[dict]:
    connection = get_database_connection()

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                id,
                source,
                kind,
                description,
                language,
                line_start,
                line_end,
                created_at
            FROM evidence
            WHERE analysis_id = %s
            ORDER BY id ASC
            """,
            (analysis_id,)
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()

def get_recent_analyses(limit: int = 10) -> list[dict]:
    connection = get_database_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                a.id,
                a.repository_path,
                a.schema_version,
                a.files_discovered,
                a.with_ai,
                a.analysis_limit,
                a.created_at,
                (
                    SELECT COUNT(*)
                    FROM claims c
                    WHERE c.analysis_id = a.id
                ) AS claims_count,
                (
                    SELECT COUNT(*)
                    FROM evidence e
                    WHERE e.analysis_id = a.id
                ) AS evidence_count
            FROM analyses a
            ORDER BY a.id DESC
            LIMIT %s
            """,
            (limit,)
        )

        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()

def get_analysis(analysis_id: int) -> dict | None:
    connection = get_database_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                id,
                repository_path,
                schema_version,
                files_discovered,
                with_ai,
                analysis_limit,
                created_at
            FROM analyses
            WHERE id = %s
            """,
            (analysis_id,)
        )

        return cursor.fetchone()
    finally:
        cursor.close()
        connection.close()