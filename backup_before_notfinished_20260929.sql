-- MySQL dump 10.13  Distrib 9.7.0, for macos15 (arm64)
--
-- Host: localhost    Database: schedule_ver1
-- ------------------------------------------------------
-- Server version	9.7.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
SET @MYSQLDUMP_TEMP_LOG_BIN = @@SESSION.SQL_LOG_BIN;
SET @@SESSION.SQL_LOG_BIN= 0;

--
-- GTID state at the beginning of the backup 
--

SET @@GLOBAL.GTID_PURGED=/*!80000 '+'*/ 'cf1e9db8-58ca-11f1-a53c-acd62c5b4545:1-274';

--
-- Table structure for table `daily_mission`
--

DROP TABLE IF EXISTS `daily_mission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `daily_mission` (
  `mission_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `mission_date` date NOT NULL,
  `mission_no` int NOT NULL,
  `segment_no` int NOT NULL DEFAULT '1',
  `mission_name` varchar(100) NOT NULL,
  `estimated_hours` decimal(4,2) NOT NULL,
  `start_time` time DEFAULT NULL,
  `end_time` time DEFAULT NULL,
  `actual_hours` decimal(4,2) DEFAULT NULL,
  `is_finished` tinyint DEFAULT NULL,
  `is_auto_closed` tinyint NOT NULL DEFAULT '0',
  `is_long_term` tinyint NOT NULL DEFAULT '0',
  `is_added` tinyint NOT NULL DEFAULT '0',
  `project_id` int DEFAULT NULL,
  `notfinished_mission_id` int DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`mission_id`),
  UNIQUE KEY `uq_daily_mission_slot` (`user_id`,`mission_date`,`mission_no`,`segment_no`),
  KEY `fk_daily_mission_project` (`project_id`),
  KEY `fk_daily_mission_notfinished` (`notfinished_mission_id`),
  KEY `idx_daily_mission_date` (`mission_date`),
  CONSTRAINT `fk_daily_mission_notfinished` FOREIGN KEY (`notfinished_mission_id`) REFERENCES `notfinished_mission` (`notfinished_mission_id`),
  CONSTRAINT `fk_daily_mission_project` FOREIGN KEY (`project_id`) REFERENCES `project` (`project_id`),
  CONSTRAINT `fk_daily_mission_user` FOREIGN KEY (`user_id`) REFERENCES `user_info` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `daily_mission`
--

LOCK TABLES `daily_mission` WRITE;
/*!40000 ALTER TABLE `daily_mission` DISABLE KEYS */;
INSERT INTO `daily_mission` VALUES (1,1,'2026-09-22',1,1,'每日工作紀錄.app 小型模板',5.00,'13:15:00','16:20:00',3.08,1,0,0,0,NULL,NULL,'2026-09-22 07:46:10','2026-09-25 06:21:53'),(2,1,'2026-09-22',2,1,'準備明日的面試',2.00,'17:23:00','18:23:00',1.00,1,0,0,0,NULL,NULL,'2026-09-22 07:46:59','2026-09-25 06:21:53'),(3,1,'2026-09-22',3,1,'整理今日的資料',2.00,'20:25:00','21:26:00',1.02,0,0,0,0,NULL,NULL,'2026-09-22 07:48:07','2026-09-25 06:21:53'),(4,1,'2026-09-22',4,1,'陪貓貓',1.00,'22:07:00','22:07:00',0.00,0,0,0,0,NULL,NULL,'2026-09-22 14:04:44','2026-09-25 06:21:53'),(5,1,'2026-09-24',1,1,'大巨蛋面試',2.00,NULL,NULL,NULL,0,1,0,0,NULL,NULL,'2026-09-22 14:08:28','2026-09-28 04:40:12'),(6,1,'2026-09-26',1,1,'每日工作紀錄.app_預計執行任務_API 修正',3.00,'13:45:00','15:30:00',1.75,1,0,0,0,NULL,NULL,'2026-09-26 05:15:22','2026-09-26 15:49:37'),(7,1,'2026-09-26',2,1,'每日工作紀錄.app_預計執行任務_介面調整',2.25,'16:00:00','18:40:00',2.67,1,0,0,0,NULL,NULL,'2026-09-26 05:16:06','2026-09-26 15:49:39'),(10,1,'2026-09-26',3,1,'每日工作紀錄.app \"任務總結\" API調整',0.00,'17:45:00','19:50:00',2.08,1,0,0,1,NULL,NULL,'2026-09-26 15:46:37','2026-09-26 15:47:16'),(11,1,'2026-09-26',4,1,'每日工作紀錄.app_任務總結_資料測試',1.00,'23:20:00','23:51:00',0.52,1,0,0,0,NULL,NULL,'2026-09-26 15:50:55','2026-09-26 15:51:39'),(12,1,'2026-09-27',1,1,'每日工作紀錄.app_任務總結_長期任務',3.00,NULL,NULL,NULL,0,1,0,0,NULL,NULL,'2026-09-27 09:29:03','2026-09-28 04:40:12'),(13,1,'2026-09-27',2,1,'每日工作紀錄.app_改CSS',1.25,NULL,NULL,NULL,0,1,0,0,NULL,NULL,'2026-09-27 09:30:18','2026-09-28 04:40:12'),(14,1,'2026-09-28',1,1,'每日工作紀錄.app_任務總結_長期任務',1.75,'11:40:00','12:19:00',0.65,1,0,1,0,1,NULL,'2026-09-28 04:05:34','2026-09-28 04:19:41'),(15,1,'2026-09-28',2,1,'每日工作紀錄.app_改CSS',1.50,'13:01:00','15:34:00',2.55,0,0,1,0,1,NULL,'2026-09-28 04:05:56','2026-09-28 07:34:28'),(16,1,'2026-09-29',1,1,'投履歷5封',5.00,NULL,NULL,NULL,NULL,0,0,0,NULL,NULL,'2026-09-29 01:24:58','2026-09-29 01:24:58'),(17,1,'2026-09-29',2,1,'未完成任務可添加至任務安排',4.00,NULL,NULL,NULL,NULL,0,0,0,NULL,NULL,'2026-09-29 03:40:59','2026-09-29 03:46:17'),(18,1,'2026-09-29',3,1,'昨天的CSS!',1.50,'11:08:00','12:07:00',0.98,1,0,1,0,1,NULL,'2026-09-29 03:47:00','2026-09-29 04:07:22');
/*!40000 ALTER TABLE `daily_mission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notfinished_mission`
--

DROP TABLE IF EXISTS `notfinished_mission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notfinished_mission` (
  `notfinished_mission_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `mission_id` int DEFAULT NULL,
  `start_date` date NOT NULL,
  `finish_date` date DEFAULT NULL,
  `is_finished` tinyint NOT NULL DEFAULT '0',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`notfinished_mission_id`),
  KEY `fk_notfinished_user` (`user_id`),
  CONSTRAINT `fk_notfinished_user` FOREIGN KEY (`user_id`) REFERENCES `user_info` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notfinished_mission`
--

LOCK TABLES `notfinished_mission` WRITE;
/*!40000 ALTER TABLE `notfinished_mission` DISABLE KEYS */;
/*!40000 ALTER TABLE `notfinished_mission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `project`
--

DROP TABLE IF EXISTS `project`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `project` (
  `project_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `project_name` varchar(100) NOT NULL,
  `start_date` date NOT NULL,
  `finish_date` date DEFAULT NULL,
  `is_finished` tinyint NOT NULL DEFAULT '0',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`project_id`),
  KEY `fk_project_user` (`user_id`),
  CONSTRAINT `fk_project_user` FOREIGN KEY (`user_id`) REFERENCES `user_info` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project`
--

LOCK TABLES `project` WRITE;
/*!40000 ALTER TABLE `project` DISABLE KEYS */;
INSERT INTO `project` VALUES (1,1,'每日工作紀錄.app','2026-09-28',NULL,0,'2026-09-28 04:19:27','2026-09-28 04:19:27');
/*!40000 ALTER TABLE `project` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_info`
--

DROP TABLE IF EXISTS `user_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_info` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `user_name` varchar(20) NOT NULL,
  `user_email` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `avatar_path` varchar(255) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `user_name` (`user_name`),
  UNIQUE KEY `user_email` (`user_email`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_info`
--

LOCK TABLES `user_info` WRITE;
/*!40000 ALTER TABLE `user_info` DISABLE KEYS */;
INSERT INTO `user_info` VALUES (1,'張嘉嘉','harerisu9@gmail.com','scrypt:32768:8:1$crOmFlDvq6aGRU81$59aa867cf52b9427be7085dbd21dba8d15953176776ec95c426b2b458db2523691b524c02bf56bc90cb1194f8069e87f6e58ea8426786beed9fbe03cdb75bd1b',NULL,'2026-09-25 06:07:31','2026-09-25 07:24:08'),(2,'張喵喵','changemma11@gmail.com','scrypt:32768:8:1$0hZbJfxjunzAg27p$35581c497cd6cb74031b9441b2ca7b18c419af78550d564f697be3349f44c7df81457bbd8edb8ccd5283de7b60171bbf05062a200bf58d58fa89e99a66602a1d','uploads/avatars/Ayaka-1.jpeg','2026-09-25 07:19:53','2026-09-25 07:19:53');
/*!40000 ALTER TABLE `user_info` ENABLE KEYS */;
UNLOCK TABLES;
SET @@SESSION.SQL_LOG_BIN = @MYSQLDUMP_TEMP_LOG_BIN;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-09-29 13:53:58
