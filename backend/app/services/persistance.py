from knowledge_compiler.output import AnalysisResult
from knowledge_compiler.models import Evidence, Claim
from ..database import get_database_connection

def save_analysis(result: AnalysisResult) -> int:
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
        connection.commit()

        return cursor.lastrowid
    finally:
        cursor.close()
        connection.close()

def save_evidence(analysis_id: int, evidence: list[Evidence]) -> list[int]:
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

        connection.commit()
        return evidence_ids
    finally:
        cursor.close()
        connection.close()
    
def save_claims(analysis_id: int, claims: list[Claim]) -> list[int]:
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
    
            connection.commit()
            return claim_ids
    finally:
        cursor.close()
        connection.close()

def save_claim_evidence(claim_id: int, evidence_ids: list[int]) -> None:
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
        connection.commit()

    finally:
        cursor.close()
        connection.close()

def persist_analysis(result: AnalysisResult) -> int:
    analysis_id = save_analysis(result)
    evidence_ids = save_evidence(analysis_id,list(result.evidence))
    claim_ids = save_claims(analysis_id, list(result.claims))

    evidence_id_map = {
        evidence.id: database_id for evidence, database_id in zip(result.evidence, evidence_ids)
    }
    for claim, claim_id in zip(result.claims, claim_ids):
        database_evidence_ids = [
            evidence_id_map[evidence_id] for evidence_id in claim.evidence_ids if evidence_id in evidence_id_map
        ]
        save_claim_evidence(claim_id, database_evidence_ids)

    return analysis_id