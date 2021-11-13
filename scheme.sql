/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

CREATE TABLE IF NOT EXISTS `emojis` (
  `id` bigint(20) NOT NULL COMMENT 'Emoji Snowflake ID',
  `name` varchar(32) NOT NULL COMMENT 'Emoji Name',
  `animated` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'Emoji is Animated or Static (boolean)',
  `nsfw` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'Emoji is NSFW or SFW (boolean)',
  `created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Emoji Upload Date',
  `author_id` bigint(20) NOT NULL COMMENT 'Emoji Uploader Snowflake ID',
  `guild_id` bigint(20) NOT NULL COMMENT 'Emoji Bot Guild ID',
  PRIMARY KEY (`id`),
  KEY `GUILD ID` (`guild_id`),
  CONSTRAINT `GUILD` FOREIGN KEY (`guild_id`) REFERENCES `guilds` (`guild_id`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Storage of emojis from Bot''s guilds.';

CREATE TABLE IF NOT EXISTS `guilds` (
  `number` tinyint(4) NOT NULL COMMENT 'Guild Sort Number',
  `guild_id` bigint(20) NOT NULL COMMENT 'Guild Snowflake ID',
  `usage_static` tinyint(3) NOT NULL DEFAULT '0' COMMENT 'Guild Static Emoji Usage',
  `usage_animated` tinyint(3) NOT NULL DEFAULT '0' COMMENT 'Guild Animated Emoji Usage',
  PRIMARY KEY (`guild_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Storage of Discord Guilds for uploading emojis.';

/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;