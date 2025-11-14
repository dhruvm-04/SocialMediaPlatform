-- MySQL setup and schema inspection for the Django Social Platform
-- Run this file in MySQL 8+ as a privileged user (e.g., root)
-- It creates the database and app user, grants privileges,
-- then switches to the database and prints table/column metadata.
--
-- Notes:
-- - Django manages tables via migrations. After running this, execute
--   `python manage.py migrate` to create/update tables.
-- - Defaults are aligned with your .env (dbmsminiproj / dbmsuser / abcd1234).

-- 1) Create database (utf8mb4 for full Unicode, including emoji)
CREATE DATABASE IF NOT EXISTS `dbmsminiproj`
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- 2) Create application user and grant privileges (localhost scope)
CREATE USER IF NOT EXISTS 'dbmsuser'@'localhost' IDENTIFIED BY 'abcd1234';
GRANT ALL PRIVILEGES ON `dbmsminiproj`.* TO 'dbmsuser'@'localhost';
FLUSH PRIVILEGES;

-- 3) Optional: enforce strict SQL mode globally (requires SUPER or SYSTEM_VARIABLES_ADMIN)
--    Remove PERSIST if you only want it for this session.
-- SET PERSIST sql_mode = 'STRICT_ALL_TABLES';

-- 4) Use the database and show quick info
USE `dbmsminiproj`;

-- Show all tables (will be empty until migrations run)
SHOW FULL TABLES;

-- 5) Compact overview of tables in this schema
SELECT
  TABLE_NAME,
  ENGINE,
  TABLE_ROWS,
  CREATE_TIME,
  UPDATE_TIME
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = DATABASE()
ORDER BY TABLE_NAME;

-- 6) Column-level details for every table
SELECT
  c.TABLE_NAME,
  c.ORDINAL_POSITION AS COL_POS,
  c.COLUMN_NAME,
  c.COLUMN_TYPE,
  c.IS_NULLABLE,
  c.COLUMN_DEFAULT,
  c.COLLATION_NAME,
  c.COLUMN_KEY,
  c.EXTRA
FROM information_schema.COLUMNS c
WHERE c.TABLE_SCHEMA = DATABASE()
ORDER BY c.TABLE_NAME, c.ORDINAL_POSITION;

-- 7) Convenience DESCRIBE statements (uncomment if you want specific tables)
-- DESCRIBE social_user;
-- DESCRIBE social_profile;
-- DESCRIBE social_post;
-- DESCRIBE social_friendship;
-- DESCRIBE social_like;
-- DESCRIBE social_comment;
-- DESCRIBE social_notification;
-- DESCRIBE django_migrations;

-- 8) Optional: quick counts after migrating/seeded
-- SELECT 'social_user' AS table_name, COUNT(*) AS cnt FROM social_user
-- UNION ALL SELECT 'social_profile', COUNT(*) FROM social_profile
-- UNION ALL SELECT 'social_post', COUNT(*) FROM social_post
-- UNION ALL SELECT 'social_friendship', COUNT(*) FROM social_friendship
-- UNION ALL SELECT 'social_like', COUNT(*) FROM social_like
-- UNION ALL SELECT 'social_comment', COUNT(*) FROM social_comment
-- UNION ALL SELECT 'social_notification', COUNT(*) FROM social_notification;
