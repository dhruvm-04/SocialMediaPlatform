-- Project SQL bundle: DDL, sample inserts, triggers, procedures/functions,
-- and example nested/join/aggregate queries for the Social Platform.
-- Tested on MySQL 8.x

-- Ensure correct schema is selected (adjust if needed)
USE `dbmsminiproj`;

/* =============================================================
   DDL: Tables (aligned to Django models; simplified for clarity)
   ============================================================= */

CREATE TABLE IF NOT EXISTS social_user (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  password VARCHAR(128) NOT NULL,
  last_login DATETIME(6) NULL,
  is_superuser TINYINT(1) NOT NULL DEFAULT 0,
  username VARCHAR(150) NOT NULL UNIQUE,
  first_name VARCHAR(150) NOT NULL DEFAULT '',
  last_name VARCHAR(150) NOT NULL DEFAULT '',
  email VARCHAR(254) NOT NULL DEFAULT '',
  is_staff TINYINT(1) NOT NULL DEFAULT 0,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  date_joined DATETIME(6) NOT NULL,
  dob DATE NULL,
  gender CHAR(1) NULL,
  CHECK (gender IN ('M','F','O') OR gender IS NULL)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS social_profile (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id BIGINT NOT NULL UNIQUE,
  bio VARCHAR(160) NOT NULL DEFAULT '',
  CONSTRAINT fk_profile_user FOREIGN KEY (user_id)
    REFERENCES social_user(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS social_post (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id BIGINT NOT NULL,
  content TEXT NOT NULL,
  created_at DATETIME(6) NOT NULL,
  updated_at DATETIME(6) NOT NULL,
  KEY idx_post_user (user_id),
  KEY idx_post_created (created_at),
  CONSTRAINT fk_post_user FOREIGN KEY (user_id)
    REFERENCES social_user(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS social_friendship (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user1_id BIGINT NOT NULL,
  user2_id BIGINT NOT NULL,
  status ENUM('pending','accepted','declined','blocked') NOT NULL DEFAULT 'pending',
  created_at DATETIME(6) NOT NULL,
  CONSTRAINT chk_friendship_no_self CHECK (user1_id <> user2_id),
  CONSTRAINT uq_friend_pair UNIQUE (user1_id, user2_id),
  CONSTRAINT fk_friend_u1 FOREIGN KEY (user1_id) REFERENCES social_user(id) ON DELETE CASCADE,
  CONSTRAINT fk_friend_u2 FOREIGN KEY (user2_id) REFERENCES social_user(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS social_like (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id BIGINT NOT NULL,
  post_id BIGINT NOT NULL,
  created_at DATETIME(6) NOT NULL,
  CONSTRAINT uq_like UNIQUE (user_id, post_id),
  CONSTRAINT fk_like_user FOREIGN KEY (user_id) REFERENCES social_user(id) ON DELETE CASCADE,
  CONSTRAINT fk_like_post FOREIGN KEY (post_id) REFERENCES social_post(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS social_comment (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id BIGINT NOT NULL,
  post_id BIGINT NOT NULL,
  content TEXT NOT NULL,
  created_at DATETIME(6) NOT NULL,
  KEY idx_comment_post (post_id),
  CONSTRAINT fk_comment_user FOREIGN KEY (user_id) REFERENCES social_user(id) ON DELETE CASCADE,
  CONSTRAINT fk_comment_post FOREIGN KEY (post_id) REFERENCES social_post(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS social_notification (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id BIGINT NOT NULL,
  message VARCHAR(255) NOT NULL,
  created_at DATETIME(6) NOT NULL,
  `read` TINYINT(1) NOT NULL DEFAULT 0,
  CONSTRAINT fk_notif_user FOREIGN KEY (user_id) REFERENCES social_user(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

/* =============================================================
   SAMPLE INSERTS (optional; normally Django management commands seed)
   ============================================================= */
-- INSERT INTO social_user(username, email, password, is_active, is_staff, is_superuser, date_joined)
-- VALUES ('super','super@example.com','<hash>',1,1,1,NOW(6));

/* =============================================================
   TRIGGERS
   ============================================================= */
DELIMITER $$

-- Normalize friendship order so (user1_id < user2_id)
CREATE TRIGGER IF NOT EXISTS trg_friendship_normalize
BEFORE INSERT ON social_friendship
FOR EACH ROW
BEGIN
  IF NEW.user1_id > NEW.user2_id THEN
    SET @tmp := NEW.user1_id;
    SET NEW.user1_id := NEW.user2_id;
    SET NEW.user2_id := @tmp;
  END IF;
END$$

-- Notify post owner on new like
CREATE TRIGGER IF NOT EXISTS trg_like_notify
AFTER INSERT ON social_like
FOR EACH ROW
BEGIN
  DECLARE v_owner BIGINT;
  SELECT user_id INTO v_owner FROM social_post WHERE id = NEW.post_id;
  IF v_owner IS NOT NULL AND v_owner <> NEW.user_id THEN
    INSERT INTO social_notification(user_id, message, created_at, `read`)
    VALUES (v_owner, CONCAT('Your post ', NEW.post_id, ' received a like'), NOW(6), 0);
  END IF;
END$$

-- Notify post owner on new comment
CREATE TRIGGER IF NOT EXISTS trg_comment_notify
AFTER INSERT ON social_comment
FOR EACH ROW
BEGIN
  DECLARE v_owner BIGINT;
  SELECT user_id INTO v_owner FROM social_post WHERE id = NEW.post_id;
  IF v_owner IS NOT NULL AND v_owner <> NEW.user_id THEN
    INSERT INTO social_notification(user_id, message, created_at, `read`)
    VALUES (v_owner, CONCAT('New comment on post ', NEW.post_id), NOW(6), 0);
  END IF;
END$$

DELIMITER ;

/* =============================================================
   STORED FUNCTIONS & PROCEDURES
   ============================================================= */
DELIMITER $$

-- Function: count accepted friends of a user
CREATE FUNCTION IF NOT EXISTS fn_friends_count(p_user_id BIGINT)
RETURNS INT DETERMINISTIC
BEGIN
  RETURN (
    SELECT COUNT(*) FROM (
      SELECT CASE WHEN f.user1_id = p_user_id THEN f.user2_id ELSE f.user1_id END AS friend_id
      FROM social_friendship f
      WHERE f.status = 'accepted' AND (f.user1_id = p_user_id OR f.user2_id = p_user_id)
    ) AS t
  );
END$$

-- Procedure: feed = self posts + accepted friends posts
CREATE PROCEDURE IF NOT EXISTS sp_get_user_feed(IN p_user BIGINT, IN p_limit INT)
BEGIN
  SELECT p.id, p.user_id, p.content, p.created_at
  FROM social_post p
  WHERE p.user_id = p_user
     OR p.user_id IN (
       SELECT CASE WHEN f.user1_id = p_user THEN f.user2_id ELSE f.user1_id END
       FROM social_friendship f
       WHERE f.status='accepted' AND (f.user1_id=p_user OR f.user2_id=p_user)
     )
  ORDER BY p.created_at DESC
  LIMIT p_limit;
END$$

-- Procedure: aggregate stats for a user
CREATE PROCEDURE IF NOT EXISTS sp_get_user_stats(IN p_user BIGINT)
BEGIN
  SELECT
    (SELECT COUNT(*) FROM social_post     WHERE user_id = p_user) AS posts,
    (SELECT COUNT(*) FROM social_like     WHERE user_id = p_user) AS likes_given,
    (SELECT COUNT(*) FROM social_like l   JOIN social_post p ON p.id=l.post_id WHERE p.user_id=p_user) AS likes_received,
    (SELECT COUNT(*) FROM social_comment  WHERE user_id = p_user) AS comments_given,
    (SELECT COUNT(*) FROM social_comment c JOIN social_post p ON p.id=c.post_id WHERE p.user_id=p_user) AS comments_received,
    fn_friends_count(p_user) AS friends_count;
END$$

-- Procedure: mutual friends list
CREATE PROCEDURE IF NOT EXISTS sp_mutual_friends(IN p_u1 BIGINT, IN p_u2 BIGINT)
BEGIN
  SELECT t.friend_id AS mutual_friend_id
  FROM (
    SELECT CASE WHEN f.user1_id = p_u1 THEN f.user2_id ELSE f.user1_id END AS friend_id
    FROM social_friendship f
    WHERE f.status='accepted' AND (f.user1_id=p_u1 OR f.user2_id=p_u1)
  ) t
  INNER JOIN (
    SELECT CASE WHEN f.user1_id = p_u2 THEN f.user2_id ELSE f.user1_id END AS friend_id
    FROM social_friendship f
    WHERE f.status='accepted' AND (f.user1_id=p_u2 OR f.user2_id=p_u2)
  ) s ON s.friend_id = t.friend_id;
END$$

DELIMITER ;

/* =============================================================
   EXAMPLE QUERIES: Nested, Join, Aggregate
   ============================================================= */

-- Join: comments with commenter and post owner
SELECT c.id AS comment_id, cu.username AS commenter, pu.username AS post_owner, c.created_at
FROM social_comment c
JOIN social_user cu ON cu.id = c.user_id
JOIN social_post p  ON p.id = c.post_id
JOIN social_user pu ON pu.id = p.user_id
ORDER BY c.created_at DESC
LIMIT 20;

-- Aggregate: total likes each user has received on their posts
SELECT u.username, COUNT(l.id) AS likes_received
FROM social_user u
LEFT JOIN social_post p ON p.user_id = u.id
LEFT JOIN social_like l ON l.post_id = p.id
GROUP BY u.id, u.username
ORDER BY likes_received DESC;

-- Nested: posts with above-average like counts
SELECT p.id, p.user_id, p.created_at
FROM social_post p
WHERE (
  SELECT COUNT(*) FROM social_like l WHERE l.post_id = p.id
) > (
  SELECT AVG(t.cnt) FROM (
    SELECT COUNT(*) AS cnt FROM social_like GROUP BY post_id
  ) t
);

/* =============================================================
   CALL EXAMPLES
   ============================================================= */
-- CALL sp_get_user_feed(1, 20);
-- CALL sp_get_user_stats(1);
-- CALL sp_mutual_friends(1, 2);
