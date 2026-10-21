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

SET @@GLOBAL.GTID_PURGED=/*!80000 '+'*/ 'cf1e9db8-58ca-11f1-a53c-acd62c5b4545:1-524';

--
-- Table structure for table `daily_mission`
--

DROP TABLE IF EXISTS `daily_mission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `daily_mission` (
  `mission_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `mission_start_date` date NOT NULL,
  `mission_finish_date` date DEFAULT NULL,
  `status` varchar(20) NOT NULL DEFAULT 'default',
  `category` varchar(50) DEFAULT NULL,
  `project_stage_id` int DEFAULT NULL,
  `mission_no` int NOT NULL,
  `mission_name` varchar(100) NOT NULL,
  `estimated_hours` decimal(4,2) NOT NULL,
  `start_time` time DEFAULT NULL,
  `end_time` time DEFAULT NULL,
  `actual_hours` decimal(4,2) DEFAULT NULL,
  `is_auto_closed` tinyint NOT NULL DEFAULT '0',
  `is_ONTime_finished` tinyint DEFAULT NULL,
  `is_added` tinyint NOT NULL DEFAULT '0',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`mission_id`),
  UNIQUE KEY `uq_daily_mission_slot` (`user_id`,`mission_start_date`,`mission_no`),
  KEY `idx_daily_mission_date` (`mission_start_date`),
  KEY `fk_daily_mission_stage` (`project_stage_id`),
  CONSTRAINT `fk_daily_mission_stage` FOREIGN KEY (`project_stage_id`) REFERENCES `project_stage` (`project_stage_id`),
  CONSTRAINT `fk_daily_mission_user` FOREIGN KEY (`user_id`) REFERENCES `user_info` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=49 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `daily_mission`
--

LOCK TABLES `daily_mission` WRITE;
/*!40000 ALTER TABLE `daily_mission` DISABLE KEYS */;
INSERT INTO `daily_mission` VALUES (1,1,'2026-09-22','2026-10-12','finished',NULL,NULL,1,'每日工作紀錄.app 小型模板',5.00,'13:15:00','16:20:00',3.08,0,1,0,'2026-09-22 07:46:10','2026-10-12 01:46:42'),(2,1,'2026-09-22','2026-10-12','finished',NULL,NULL,2,'準備明日的面試',2.00,'17:23:00','18:23:00',1.00,0,1,0,'2026-09-22 07:46:59','2026-10-12 01:46:42'),(3,1,'2026-10-18',NULL,'unfinished',NULL,NULL,36,'整理今日的資料',2.00,NULL,NULL,NULL,0,NULL,0,'2026-09-22 07:48:07','2026-10-18 13:58:53'),(4,1,'2026-10-18','2026-10-18','finished',NULL,NULL,42,'陪貓貓',1.00,'22:38:00','23:40:00',1.03,0,0,0,'2026-09-22 14:04:44','2026-10-18 14:59:26'),(5,1,'2026-10-18','2026-10-18','finished',NULL,NULL,43,'大巨蛋面試',1.00,'15:00:00','16:00:00',1.00,0,0,0,'2026-09-22 14:08:28','2026-10-18 15:01:02'),(6,1,'2026-09-26','2026-10-12','finished',NULL,NULL,1,'每日工作紀錄.app_預計執行任務_API 修正',3.00,'13:45:00','15:30:00',1.75,0,1,0,'2026-09-26 05:15:22','2026-10-12 01:46:42'),(7,1,'2026-09-26','2026-10-12','finished',NULL,NULL,2,'每日工作紀錄.app_預計執行任務_介面調整',2.25,'16:00:00','18:40:00',2.67,0,1,0,'2026-09-26 05:16:06','2026-10-12 01:46:42'),(10,1,'2026-09-26','2026-10-12','finished',NULL,NULL,3,'每日工作紀錄.app \"任務總結\" API調整',0.00,'17:45:00','19:50:00',2.08,0,1,1,'2026-09-26 15:46:37','2026-10-12 01:46:42'),(11,1,'2026-09-26','2026-10-12','finished',NULL,NULL,4,'每日工作紀錄.app_任務總結_資料測試',1.00,'23:20:00','23:51:00',0.52,0,1,0,'2026-09-26 15:50:55','2026-10-12 01:46:42'),(12,1,'2026-09-27','2026-10-16','finished',NULL,1,1,'每日工作紀錄.app_任務總結_長期任務',3.00,NULL,NULL,NULL,1,0,0,'2026-09-27 09:29:03','2026-10-16 02:06:52'),(13,1,'2026-09-27','2026-10-16','finished',NULL,1,2,'每日工作紀錄.app_改CSS',1.25,NULL,NULL,NULL,1,0,0,'2026-09-27 09:30:18','2026-10-16 02:06:52'),(14,1,'2026-09-28','2026-10-12','finished',NULL,1,1,'每日工作紀錄.app_任務總結_長期任務',1.75,'11:40:00','12:19:00',0.65,0,1,0,'2026-09-28 04:05:34','2026-10-12 01:46:42'),(15,1,'2026-09-28','2026-10-16','finished',NULL,1,2,'每日工作紀錄.app_改CSS',1.50,'13:01:00','15:34:00',2.55,0,0,0,'2026-09-28 04:05:56','2026-10-16 02:06:52'),(16,1,'2026-09-29','2026-10-12','finished',NULL,2,1,'投履歷5封',5.00,'09:13:00','17:07:00',7.90,0,1,0,'2026-09-29 01:24:58','2026-10-12 01:46:42'),(17,1,'2026-09-29','2026-10-16','finished',NULL,1,2,'未完成任務可添加至任務安排',4.00,'12:16:00','14:17:00',2.02,0,0,0,'2026-09-29 03:40:59','2026-10-16 02:06:52'),(18,1,'2026-09-29','2026-10-12','finished',NULL,1,3,'昨天的CSS!',1.50,'11:08:00','12:07:00',0.98,0,1,0,'2026-09-29 03:47:00','2026-10-12 01:46:42'),(19,1,'2026-10-19',NULL,'default',NULL,NULL,4,'測試：不回報任務，看任務是否進入未完成',0.08,NULL,NULL,NULL,0,NULL,0,'2026-09-29 06:18:18','2026-10-19 05:46:41'),(20,1,'2026-10-19','2026-10-19','finished',NULL,20,1,'測試：回報任務(未完成)，看任務是否進入未完成',1.00,'12:51:00','13:51:00',1.00,0,0,0,'2026-09-29 07:49:04','2026-10-19 05:11:31'),(21,1,'2026-09-30','2026-10-16','finished',NULL,1,1,'未完成任務轉換成專案＿可以轉換為已有專案',1.00,'09:53:00',NULL,NULL,0,0,0,'2026-09-30 01:51:41','2026-10-16 02:06:52'),(22,1,'2026-09-30','2026-10-16','finished',NULL,1,2,'未完成任務轉換成專案＿有個頁面篩選器',1.00,NULL,NULL,NULL,0,0,0,'2026-09-30 01:52:46','2026-10-16 02:06:52'),(23,1,'2026-10-18',NULL,'unfinished',NULL,2,45,'投履歷3份',2.00,NULL,NULL,NULL,0,NULL,0,'2026-09-30 01:53:40','2026-10-19 04:52:14'),(24,1,'2026-10-01','2026-10-12','finished',NULL,2,1,'外商＿英文自我介紹',4.00,'20:10:00','22:10:00',2.00,0,1,0,'2026-10-01 14:08:57','2026-10-12 01:46:42'),(25,1,'2026-10-18',NULL,'unfinished',NULL,2,29,'其他三題（power bi, strength and weakness, why i want to be here）',2.00,NULL,NULL,NULL,0,NULL,0,'2026-10-01 14:09:50','2026-10-18 13:58:32'),(26,1,'2026-10-02','2026-10-12','finished',NULL,2,1,'外商英文面試',1.00,'10:00:00','10:50:00',0.83,0,1,0,'2026-10-02 03:19:15','2026-10-12 01:46:42'),(27,1,'2026-10-02','2026-10-12','finished',NULL,2,2,'英文履歷',1.50,'12:15:00','13:21:00',1.10,0,1,0,'2026-10-02 03:21:49','2026-10-12 01:46:42'),(28,1,'2026-10-03','2026-10-12','finished',NULL,NULL,1,'與師父出門',8.00,'07:40:00','17:30:00',9.83,0,1,0,'2026-10-02 14:17:53','2026-10-12 01:46:42'),(29,1,'2026-10-18','2026-10-19','finished',NULL,NULL,30,'測試＿當日任務未完成不會進入到未完成區塊',1.00,NULL,NULL,NULL,0,0,0,'2026-10-02 14:55:00','2026-10-19 04:50:47'),(31,1,'2026-10-02','2026-10-12','finished',NULL,1,4,'修改未完成任務頁面的功能缺陷、介面問題、使用者按鈕提醒',1.50,'22:46:00','23:46:00',1.00,0,1,0,'2026-10-02 15:46:07','2026-10-12 01:46:42'),(32,1,'2026-10-18',NULL,'unfinished',NULL,NULL,31,'任務標籤',2.00,NULL,NULL,NULL,0,NULL,0,'2026-10-02 15:47:11','2026-10-18 13:58:37'),(33,1,'2026-10-18',NULL,'unfinished',NULL,NULL,32,'長期任務＿未完成任務狀態調整',2.00,NULL,NULL,NULL,0,NULL,0,'2026-10-02 15:47:45','2026-10-18 13:58:44'),(34,1,'2026-10-05','2026-10-16','finished',NULL,1,1,'未完成任務可添加至任務安排',1.00,NULL,NULL,NULL,0,0,0,'2026-10-05 03:33:36','2026-10-16 02:06:52'),(35,1,'2026-10-05','2026-10-16','finished',NULL,1,2,'長期任務＿未完成任務狀態調整',1.00,NULL,NULL,NULL,0,0,0,'2026-10-05 03:56:00','2026-10-16 02:06:52'),(36,1,'2026-10-05','2026-10-12','finished',NULL,3,3,'測試長期任務資料流向',2.00,'12:18:00','12:18:00',0.00,0,1,0,'2026-10-05 04:18:02','2026-10-12 01:46:42'),(38,1,'2026-10-06','2026-10-16','finished',NULL,1,1,'改好資料流',5.00,'09:54:00','14:54:00',5.00,0,0,0,'2026-10-06 06:31:42','2026-10-16 02:06:52'),(40,1,'2026-10-06','2026-10-16','finished',NULL,NULL,2,'test',0.75,NULL,NULL,NULL,1,0,0,'2026-10-06 07:02:52','2026-10-16 00:30:04'),(41,1,'2026-10-18',NULL,'unfinished',NULL,NULL,33,'整個資料流構想一次',6.00,NULL,NULL,NULL,0,NULL,0,'2026-10-08 08:22:50','2026-10-18 13:58:46'),(42,1,'2026-10-18',NULL,'unfinished',NULL,NULL,34,'資料模擬',3.00,NULL,NULL,NULL,0,NULL,0,'2026-10-08 08:24:05','2026-10-18 13:58:49'),(44,1,'2026-10-18',NULL,'unfinished',NULL,NULL,35,'資料庫：修建資料階層邏輯，頁面：確認修正成功',4.00,NULL,NULL,NULL,0,NULL,0,'2026-10-14 03:02:09','2026-10-18 13:58:51'),(45,1,'2026-10-14','2026-10-14','finished',NULL,NULL,2,'資料階層plan.py & summary.py測試（）',0.25,NULL,NULL,NULL,0,0,0,'2026-10-14 03:22:32','2026-10-14 03:22:48'),(47,1,'2026-10-19',NULL,'default',NULL,21,2,'Error fix: Table Unfinished_mission error in \"sequence exist\"',1.00,'12:54:00','13:54:00',NULL,0,NULL,0,'2026-10-19 04:55:08','2026-10-19 04:56:53'),(48,1,'2026-10-19',NULL,'default',NULL,22,3,'Error fix: User interface of mission arrangement',1.00,'12:56:00','13:56:00',NULL,0,NULL,0,'2026-10-19 04:56:52','2026-10-19 04:56:52');
/*!40000 ALTER TABLE `daily_mission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notfinished_mission_backup_do_not_use`
--

DROP TABLE IF EXISTS `notfinished_mission_backup_do_not_use`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notfinished_mission_backup_do_not_use` (
  `notfinished_mission_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `mission_id` int DEFAULT NULL,
  `status` varchar(20) NOT NULL DEFAULT 'open',
  `start_date` date NOT NULL,
  `finish_date` date DEFAULT NULL,
  `delayed_reason` varchar(255) DEFAULT NULL,
  `closed_reason` varchar(255) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`notfinished_mission_id`),
  KEY `fk_notfinished_user` (`user_id`),
  KEY `fk_notfinished_source_mission` (`mission_id`),
  CONSTRAINT `fk_notfinished_source_mission` FOREIGN KEY (`mission_id`) REFERENCES `daily_mission` (`mission_id`),
  CONSTRAINT `fk_notfinished_user` FOREIGN KEY (`user_id`) REFERENCES `user_info` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notfinished_mission_backup_do_not_use`
--

LOCK TABLES `notfinished_mission_backup_do_not_use` WRITE;
/*!40000 ALTER TABLE `notfinished_mission_backup_do_not_use` DISABLE KEYS */;
INSERT INTO `notfinished_mission_backup_do_not_use` VALUES (1,1,3,'closed','2026-09-22','2026-09-30',NULL,'其他事項','2026-09-29 06:00:38','2026-09-30 01:48:56'),(2,1,4,'closed','2026-09-22','2026-09-30',NULL,NULL,'2026-09-29 06:00:38','2026-09-30 03:35:31'),(3,1,5,'closed','2026-09-24','2026-09-30','日期放置錯誤','日期放置錯誤','2026-09-29 06:00:38','2026-09-30 03:35:15'),(4,1,12,'converted','2026-09-27','2026-09-30',NULL,NULL,'2026-09-29 06:00:38','2026-09-30 03:37:30'),(5,1,13,'converted','2026-09-27','2026-09-30',NULL,NULL,'2026-09-29 06:00:38','2026-09-30 03:36:59'),(6,1,15,'converted','2026-09-28','2026-09-30',NULL,NULL,'2026-09-29 06:00:38','2026-09-30 03:37:01'),(8,1,17,'open','2026-09-29',NULL,NULL,NULL,'2026-09-29 06:16:16','2026-10-02 14:51:56'),(9,1,20,'closed','2026-09-29','2026-10-02',NULL,'專案資料測試（成功）','2026-09-29 09:07:55','2026-10-02 14:52:44'),(10,1,19,'closed','2026-09-29','2026-10-02',NULL,'專案資料測試（成功）','2026-09-30 01:47:45','2026-10-02 14:52:41'),(11,1,21,'converted','2026-09-30','2026-10-02',NULL,NULL,'2026-09-30 01:54:19','2026-10-02 14:25:12'),(12,1,22,'converted','2026-09-30','2026-10-02',NULL,NULL,'2026-09-30 01:55:19','2026-10-02 14:25:11'),(13,1,23,'converted','2026-09-30','2026-10-03',NULL,'準備後續的英文面試與英文履歷','2026-10-01 14:09:57','2026-10-02 16:31:35'),(14,1,25,'converted','2026-10-01','2026-10-02',NULL,NULL,'2026-10-02 04:57:57','2026-10-02 14:27:08'),(15,1,29,'closed','2026-10-02','2026-10-03',NULL,'任務資料測試（成功）','2026-10-02 14:55:30','2026-10-02 16:30:06'),(16,1,32,'open','2026-10-02',NULL,NULL,NULL,'2026-10-02 16:29:16','2026-10-02 16:29:16'),(17,1,33,'open','2026-10-02',NULL,NULL,NULL,'2026-10-02 16:29:16','2026-10-02 16:29:16'),(19,1,34,'open','2026-10-05',NULL,NULL,NULL,'2026-10-05 15:26:24','2026-10-05 15:26:24'),(20,1,35,'open','2026-10-05',NULL,NULL,NULL,'2026-10-05 15:26:27','2026-10-05 15:26:27'),(21,1,38,'resolved','2026-10-06','2026-10-06',NULL,NULL,'2026-10-06 06:54:55','2026-10-06 06:57:22'),(22,1,40,'open','2026-10-06',NULL,NULL,NULL,'2026-10-08 08:22:26','2026-10-08 08:22:26');
/*!40000 ALTER TABLE `notfinished_mission_backup_do_not_use` ENABLE KEYS */;
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
  `category` varchar(50) DEFAULT NULL,
  `estimate_days` int DEFAULT NULL,
  `stage_amount` int NOT NULL DEFAULT '0',
  `start_date` date NOT NULL,
  `actual_finish_date` date DEFAULT NULL,
  `estimated_finish_date` date DEFAULT NULL,
  `status` varchar(20) NOT NULL DEFAULT 'ongoing',
  `is_ONTime_finished` tinyint DEFAULT NULL,
  `delay_reason` varchar(255) DEFAULT NULL,
  `closed_reason` varchar(255) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`project_id`),
  KEY `fk_project_user` (`user_id`),
  CONSTRAINT `fk_project_user` FOREIGN KEY (`user_id`) REFERENCES `user_info` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project`
--

LOCK TABLES `project` WRITE;
/*!40000 ALTER TABLE `project` DISABLE KEYS */;
INSERT INTO `project` VALUES (1,1,'每日工作紀錄.app',NULL,14,1,'2026-09-28','2026-10-16',NULL,'stopped',NULL,NULL,'新功能取代此專案','2026-09-28 04:19:27','2026-10-16 02:06:52'),(2,1,'工作應徵iii',NULL,13,1,'2026-09-29',NULL,NULL,'ongoing',NULL,NULL,NULL,'2026-09-29 09:07:42','2026-10-12 01:45:35'),(3,1,'測試用',NULL,0,1,'2026-10-05','2026-10-05',NULL,'resolved',NULL,NULL,NULL,'2026-10-05 04:18:27','2026-10-12 01:45:35'),(8,1,'每日時間紀錄_app','life',16,4,'2026-10-16',NULL,'2026-10-31','ongoing',NULL,NULL,NULL,'2026-10-16 02:05:57','2026-10-16 02:05:57');
/*!40000 ALTER TABLE `project` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `project_stage`
--

DROP TABLE IF EXISTS `project_stage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `project_stage` (
  `project_stage_id` int NOT NULL AUTO_INCREMENT,
  `project_id` int NOT NULL,
  `user_id` int NOT NULL,
  `stage_no` int NOT NULL,
  `stage_name` varchar(100) NOT NULL,
  `status` varchar(20) NOT NULL DEFAULT 'ongoing',
  `estimate_days` int NOT NULL,
  `start_date` date NOT NULL,
  `estimated_finish_date` date DEFAULT NULL,
  `actual_finish_date` date DEFAULT NULL,
  `is_ONTime_finished` tinyint DEFAULT NULL,
  `delay_reason` varchar(255) DEFAULT NULL,
  `closed_reason` varchar(255) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`project_stage_id`),
  KEY `fk_stage_project` (`project_id`),
  KEY `fk_stage_user` (`user_id`),
  CONSTRAINT `fk_stage_project` FOREIGN KEY (`project_id`) REFERENCES `project` (`project_id`),
  CONSTRAINT `fk_stage_user` FOREIGN KEY (`user_id`) REFERENCES `user_info` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project_stage`
--

LOCK TABLES `project_stage` WRITE;
/*!40000 ALTER TABLE `project_stage` DISABLE KEYS */;
INSERT INTO `project_stage` VALUES (1,1,1,1,'既有任務（系統自動建立）','stopped',14,'2026-09-28',NULL,'2026-10-16',NULL,NULL,'專案關閉','2026-10-12 01:45:33','2026-10-16 02:06:52'),(2,2,1,1,'既有任務（系統自動建立）','ongoing',13,'2026-09-29',NULL,NULL,NULL,NULL,NULL,'2026-10-12 01:45:33','2026-10-12 01:45:33'),(3,3,1,1,'既有任務（系統自動建立）','resolved',0,'2026-10-05',NULL,'2026-10-05',NULL,NULL,NULL,'2026-10-12 01:45:33','2026-10-12 01:45:33'),(20,8,1,1,'1. Design of User interface flow & Derivation of data flow','ongoing',3,'2026-10-16','2026-10-18',NULL,NULL,NULL,NULL,'2026-10-16 02:05:57','2026-10-16 02:05:57'),(21,8,1,2,'2. DataBase & Apparchitecture_design with data testing','ongoing',5,'2026-10-19','2026-10-23',NULL,NULL,NULL,NULL,'2026-10-16 02:05:57','2026-10-16 02:05:57'),(22,8,1,3,'3. Interface and other minor feature adjustments','ongoing',5,'2026-10-24','2026-10-28',NULL,NULL,NULL,NULL,'2026-10-16 02:05:57','2026-10-16 02:05:57'),(23,8,1,4,'4. User Testing','ongoing',3,'2026-10-29','2026-10-31',NULL,NULL,NULL,NULL,'2026-10-16 02:05:57','2026-10-16 02:05:57');
/*!40000 ALTER TABLE `project_stage` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `project_stage_mission`
--

DROP TABLE IF EXISTS `project_stage_mission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `project_stage_mission` (
  `stage_mission_id` int NOT NULL AUTO_INCREMENT,
  `project_stage_id` int NOT NULL,
  `mission_id` int NOT NULL,
  `unfinished_id` int DEFAULT NULL,
  `status` varchar(20) NOT NULL,
  `is_operatable` tinyint NOT NULL DEFAULT '1',
  `update_date` date NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`stage_mission_id`),
  UNIQUE KEY `uq_stagemission_mission` (`project_stage_id`,`mission_id`),
  KEY `fk_stagemission_mission` (`mission_id`),
  KEY `fk_stagemission_unfinished` (`unfinished_id`),
  CONSTRAINT `fk_stagemission_mission` FOREIGN KEY (`mission_id`) REFERENCES `daily_mission` (`mission_id`),
  CONSTRAINT `fk_stagemission_stage` FOREIGN KEY (`project_stage_id`) REFERENCES `project_stage` (`project_stage_id`),
  CONSTRAINT `fk_stagemission_unfinished` FOREIGN KEY (`unfinished_id`) REFERENCES `unfinished_mission` (`unfinished_id`)
) ENGINE=InnoDB AUTO_INCREMENT=58 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project_stage_mission`
--

LOCK TABLES `project_stage_mission` WRITE;
/*!40000 ALTER TABLE `project_stage_mission` DISABLE KEYS */;
INSERT INTO `project_stage_mission` VALUES (1,1,12,4,'resolved',0,'2026-10-16','2026-10-12 01:53:10','2026-10-16 02:06:52'),(2,1,13,5,'resolved',0,'2026-10-16','2026-10-12 01:53:10','2026-10-16 02:06:52'),(3,1,14,NULL,'resolved',0,'2026-09-28','2026-10-12 01:53:10','2026-10-12 01:53:10'),(4,1,15,6,'resolved',0,'2026-10-16','2026-10-12 01:53:10','2026-10-16 02:06:52'),(5,2,16,NULL,'resolved',0,'2026-09-29','2026-10-12 01:53:10','2026-10-12 01:53:10'),(6,1,17,7,'closed',0,'2026-10-16','2026-10-12 01:53:10','2026-10-16 02:06:52'),(7,1,18,NULL,'resolved',0,'2026-09-29','2026-10-12 01:53:10','2026-10-12 01:53:10'),(8,1,21,10,'resolved',0,'2026-10-16','2026-10-12 01:53:10','2026-10-16 02:06:52'),(9,1,22,11,'resolved',0,'2026-10-16','2026-10-12 01:53:10','2026-10-16 02:06:52'),(10,2,23,57,'open',1,'2026-10-19','2026-10-12 01:53:10','2026-10-19 04:52:14'),(11,2,24,NULL,'resolved',0,'2026-10-01','2026-10-12 01:53:10','2026-10-12 01:53:10'),(12,2,25,58,'open',1,'2026-10-18','2026-10-12 01:53:10','2026-10-18 13:58:32'),(13,2,26,NULL,'resolved',0,'2026-10-02','2026-10-12 01:53:10','2026-10-12 01:53:10'),(14,2,27,NULL,'resolved',0,'2026-10-02','2026-10-12 01:53:10','2026-10-12 01:53:10'),(15,1,31,NULL,'resolved',0,'2026-10-02','2026-10-12 01:53:10','2026-10-12 01:53:10'),(16,1,34,17,'closed',0,'2026-10-16','2026-10-12 01:53:10','2026-10-16 02:06:52'),(17,1,35,18,'closed',0,'2026-10-16','2026-10-12 01:53:10','2026-10-16 02:06:52'),(18,3,36,NULL,'resolved',0,'2026-10-05','2026-10-12 01:53:10','2026-10-12 01:53:10'),(19,1,38,19,'resolved',0,'2026-10-16','2026-10-12 01:53:10','2026-10-16 02:06:52'),(49,20,20,56,'open',1,'2026-10-19','2026-10-19 04:51:30','2026-10-19 05:11:31'),(53,20,47,NULL,'arrangement',1,'2026-10-19','2026-10-19 04:55:17','2026-10-19 04:55:17'),(54,22,48,NULL,'arrangement',1,'2026-10-19','2026-10-19 04:56:52','2026-10-19 04:56:52'),(55,21,47,NULL,'arrangement',1,'2026-10-19','2026-10-19 04:56:53','2026-10-19 04:56:53');
/*!40000 ALTER TABLE `project_stage_mission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `unfinished_mission`
--

DROP TABLE IF EXISTS `unfinished_mission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `unfinished_mission` (
  `unfinished_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `mission_id` int NOT NULL,
  `status` varchar(20) NOT NULL DEFAULT 'open',
  `is_operatable` tinyint NOT NULL DEFAULT '1',
  `sequence_exit` tinyint NOT NULL DEFAULT '0',
  `follower_id` int DEFAULT NULL,
  `update_date` date NOT NULL,
  `start_time` time DEFAULT NULL,
  `end_time` time DEFAULT NULL,
  `actual_hours` decimal(4,2) DEFAULT NULL,
  `delay_reason` varchar(255) DEFAULT NULL,
  `closed_reason` varchar(255) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`unfinished_id`),
  KEY `fk_unfinished_user` (`user_id`),
  KEY `fk_unfinished_mission` (`mission_id`),
  KEY `fk_unfinished_follower` (`follower_id`),
  CONSTRAINT `fk_unfinished_follower` FOREIGN KEY (`follower_id`) REFERENCES `unfinished_mission` (`unfinished_id`),
  CONSTRAINT `fk_unfinished_mission` FOREIGN KEY (`mission_id`) REFERENCES `daily_mission` (`mission_id`),
  CONSTRAINT `fk_unfinished_user` FOREIGN KEY (`user_id`) REFERENCES `user_info` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=69 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `unfinished_mission`
--

LOCK TABLES `unfinished_mission` WRITE;
/*!40000 ALTER TABLE `unfinished_mission` DISABLE KEYS */;
INSERT INTO `unfinished_mission` VALUES (1,1,3,'closed',0,0,NULL,'2026-09-30',NULL,NULL,NULL,NULL,'其他事項','2026-09-29 06:00:38','2026-09-30 01:48:56'),(2,1,4,'closed',0,0,NULL,'2026-09-30',NULL,NULL,NULL,NULL,NULL,'2026-09-29 06:00:38','2026-09-30 03:35:31'),(3,1,5,'closed',0,0,NULL,'2026-09-30',NULL,NULL,NULL,'日期放置錯誤','日期放置錯誤','2026-09-29 06:00:38','2026-09-30 03:35:15'),(4,1,12,'resolved',0,0,NULL,'2026-09-30',NULL,NULL,NULL,NULL,NULL,'2026-09-29 06:00:38','2026-09-30 03:37:30'),(5,1,13,'resolved',0,0,NULL,'2026-09-30',NULL,NULL,NULL,NULL,NULL,'2026-09-29 06:00:38','2026-09-30 03:36:59'),(6,1,15,'resolved',0,0,NULL,'2026-09-30',NULL,NULL,NULL,NULL,NULL,'2026-09-29 06:00:38','2026-09-30 03:37:01'),(7,1,17,'closed',0,0,NULL,'2026-10-02',NULL,NULL,NULL,NULL,'專案關閉','2026-09-29 06:16:16','2026-10-16 02:06:52'),(8,1,20,'closed',0,0,NULL,'2026-10-02',NULL,NULL,NULL,NULL,'專案資料測試（成功）','2026-09-29 09:07:55','2026-10-02 14:52:44'),(9,1,19,'closed',0,0,NULL,'2026-10-02',NULL,NULL,NULL,NULL,'專案資料測試（成功）','2026-09-30 01:47:45','2026-10-02 14:52:41'),(10,1,21,'resolved',0,0,NULL,'2026-10-02',NULL,NULL,NULL,NULL,NULL,'2026-09-30 01:54:19','2026-10-02 14:25:12'),(11,1,22,'resolved',0,0,NULL,'2026-10-02',NULL,NULL,NULL,NULL,NULL,'2026-09-30 01:55:19','2026-10-02 14:25:11'),(12,1,23,'resolved',0,0,NULL,'2026-10-03',NULL,NULL,NULL,NULL,'準備後續的英文面試與英文履歷','2026-10-01 14:09:57','2026-10-02 16:31:35'),(13,1,25,'resolved',0,0,NULL,'2026-10-02',NULL,NULL,NULL,NULL,NULL,'2026-10-02 04:57:57','2026-10-02 14:27:08'),(14,1,29,'closed',0,0,NULL,'2026-10-03',NULL,NULL,NULL,NULL,'任務資料測試（成功）','2026-10-02 14:55:30','2026-10-02 16:30:06'),(15,1,32,'open',0,1,NULL,'2026-10-03',NULL,NULL,NULL,NULL,NULL,'2026-10-02 16:29:16','2026-10-18 07:29:16'),(16,1,33,'open',0,1,NULL,'2026-10-03',NULL,NULL,NULL,NULL,NULL,'2026-10-02 16:29:16','2026-10-18 07:30:12'),(17,1,34,'closed',0,0,NULL,'2026-10-05',NULL,NULL,NULL,NULL,'專案關閉','2026-10-05 15:26:24','2026-10-16 02:06:52'),(18,1,35,'closed',0,0,NULL,'2026-10-05',NULL,NULL,NULL,NULL,'專案關閉','2026-10-05 15:26:27','2026-10-16 02:06:52'),(19,1,38,'resolved',0,0,NULL,'2026-10-06',NULL,NULL,NULL,NULL,NULL,'2026-10-06 06:54:55','2026-10-06 06:57:22'),(20,1,40,'open',0,1,NULL,'2026-10-08',NULL,NULL,NULL,NULL,NULL,'2026-10-08 08:22:26','2026-10-16 00:30:04'),(32,1,41,'open',0,1,NULL,'2026-10-08',NULL,NULL,NULL,NULL,NULL,'2026-10-14 05:20:33','2026-10-18 07:32:13'),(33,1,42,'open',0,1,NULL,'2026-10-08',NULL,NULL,NULL,NULL,NULL,'2026-10-14 05:20:33','2026-10-18 07:35:33'),(35,1,40,'closed',0,0,20,'2026-10-16',NULL,NULL,NULL,NULL,'test completed','2026-10-16 00:30:04','2026-10-16 00:30:04'),(36,1,44,'open',0,1,NULL,'2026-10-14',NULL,NULL,NULL,NULL,NULL,'2026-10-16 02:24:44','2026-10-18 07:35:43'),(37,1,3,'open',0,1,NULL,'2026-09-22',NULL,NULL,NULL,NULL,NULL,'2026-10-18 07:27:29','2026-10-18 07:28:32'),(38,1,4,'open',0,1,NULL,'2026-09-22',NULL,NULL,NULL,NULL,NULL,'2026-10-18 07:27:29','2026-10-18 07:28:35'),(39,1,5,'open',0,1,NULL,'2026-09-24',NULL,NULL,NULL,NULL,NULL,'2026-10-18 07:27:29','2026-10-18 07:28:36'),(40,1,19,'open',0,1,NULL,'2026-09-29',NULL,NULL,NULL,NULL,NULL,'2026-10-18 07:27:29','2026-10-18 07:28:37'),(41,1,20,'open',0,1,NULL,'2026-09-29',NULL,NULL,NULL,NULL,NULL,'2026-10-18 07:27:29','2026-10-18 07:28:38'),(42,1,23,'open',0,1,NULL,'2026-09-30',NULL,NULL,NULL,NULL,NULL,'2026-10-18 07:27:29','2026-10-18 07:28:40'),(43,1,25,'open',0,1,NULL,'2026-10-01',NULL,NULL,NULL,NULL,NULL,'2026-10-18 07:27:29','2026-10-18 07:28:40'),(44,1,29,'open',0,1,NULL,'2026-10-02',NULL,NULL,NULL,NULL,NULL,'2026-10-18 07:27:29','2026-10-18 07:29:05'),(52,1,3,'open',0,1,37,'2026-10-18',NULL,NULL,NULL,NULL,NULL,'2026-10-18 07:28:32','2026-10-18 13:16:18'),(53,1,4,'open',0,1,38,'2026-10-18',NULL,NULL,NULL,NULL,NULL,'2026-10-18 07:28:35','2026-10-18 13:16:36'),(54,1,5,'open',0,1,39,'2026-10-18',NULL,NULL,NULL,NULL,NULL,'2026-10-18 07:28:36','2026-10-18 14:59:50'),(55,1,19,'open',0,1,40,'2026-10-18',NULL,NULL,NULL,NULL,NULL,'2026-10-18 07:28:37','2026-10-18 15:11:44'),(56,1,20,'open',0,1,41,'2026-10-18',NULL,NULL,NULL,NULL,NULL,'2026-10-18 07:28:38','2026-10-19 04:51:30'),(57,1,23,'open',1,0,42,'2026-10-18',NULL,NULL,NULL,NULL,NULL,'2026-10-18 07:28:40','2026-10-19 04:52:14'),(58,1,25,'open',1,0,43,'2026-10-18',NULL,NULL,NULL,NULL,NULL,'2026-10-18 07:28:40','2026-10-18 13:58:32'),(59,1,29,'open',0,1,44,'2026-10-18',NULL,NULL,NULL,NULL,NULL,'2026-10-18 07:29:05','2026-10-19 04:50:47'),(60,1,32,'open',1,0,15,'2026-10-18',NULL,NULL,NULL,NULL,NULL,'2026-10-18 07:29:16','2026-10-18 13:58:37'),(61,1,33,'open',1,0,16,'2026-10-18',NULL,NULL,NULL,NULL,NULL,'2026-10-18 07:30:12','2026-10-18 13:58:44'),(62,1,41,'open',1,0,32,'2026-10-18',NULL,NULL,NULL,NULL,NULL,'2026-10-18 07:32:13','2026-10-18 13:58:46'),(63,1,42,'open',1,0,33,'2026-10-18',NULL,NULL,NULL,NULL,NULL,'2026-10-18 07:35:33','2026-10-18 13:58:49'),(64,1,44,'open',1,0,36,'2026-10-18',NULL,NULL,NULL,NULL,NULL,'2026-10-18 07:35:43','2026-10-18 13:58:51'),(65,1,3,'open',1,0,52,'2026-10-18',NULL,NULL,NULL,NULL,NULL,'2026-10-18 13:16:18','2026-10-18 13:58:53'),(66,1,4,'open',0,1,53,'2026-10-18',NULL,NULL,NULL,NULL,NULL,'2026-10-18 13:16:36','2026-10-18 14:37:41'),(67,1,19,'open',0,1,NULL,'2026-10-18',NULL,NULL,NULL,NULL,NULL,'2026-10-18 15:12:25','2026-10-19 05:46:41'),(68,1,29,'closed',0,0,59,'2026-10-19',NULL,NULL,NULL,NULL,'已有相似任務名稱','2026-10-19 04:50:47','2026-10-19 04:50:47');
/*!40000 ALTER TABLE `unfinished_mission` ENABLE KEYS */;
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

-- Dump completed on 2026-10-19 14:57:41
