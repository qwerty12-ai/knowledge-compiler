CREATE DATABASE IF NOT EXISTS knowledge_compiler;

USE knowledge_compiler;

CREATE TABLE analyses (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    repository_path VARCHAR(1024) NOT NULL,
    schema_version VARCHAR(20) NOT NULL DEFAULT '1.0',
    files_discovered INT UNSIGNED NOT NULL DEFAULT 0,
    with_ai BOOLEAN NOT NULL DEFAULT FALSE,
    analysis_limit INT UNSIGNED NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE evidence (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    analysis_id BIGINT UNSIGNED NOT NULL,
    source VARCHAR(1024) NOT NULL,
    kind VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    language VARCHAR(50) NULL,
    line_start INT UNSIGNED NULL,
    line_end INT UNSIGNED NULL,
    content MEDIUMTEXT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_evidence_analysis FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE
);

CREATE TABLE claims (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    analysis_id BIGINT UNSIGNED NOT NULL,
    statement VARCHAR(1024) NOT NULL,
    status VARCHAR(50) NOT NULL,
    confidence DECIMAL(4,3) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_claims_analysis FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE
);

CREATE TABLE claim_evidence (
    claim_id BIGINT UNSIGNED NOT NULL,
    evidence_id BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY (claim_id, evidence_id),
    CONSTRAINT fk_claim_evidence_claim FOREIGN KEY (claim_id) REFERENCES claims(id) ON DELETE CASCADE,
    CONSTRAINT fk_claim_evidence_evidence FOREIGN KEY (evidence_id) REFERENCES evidence(id) ON DELETE CASCADE
);