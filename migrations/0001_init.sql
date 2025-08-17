CREATE TABLE IF NOT EXISTS docs (
  doc_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  target TEXT NOT NULL,
  state INT NOT NULL DEFAULT 0,
  msg_id BIGINT NULL,
  flag INT NOT NULL DEFAULT 0,
  title VARCHAR(200) NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uk_target_msg (target(191), msg_id),
  KEY idx_state (state),
  KEY idx_created_at (created_at),
  KEY idx_msg_id (msg_id),
  KEY idx_target (target(191))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;