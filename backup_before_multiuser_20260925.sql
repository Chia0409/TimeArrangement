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

SET @@GLOBAL.GTID_PURGED=/*!80000 '+'*/ 'cf1e9db8-58ca-11f1-a53c-acd62c5b4545:1-218';

--
-- Table structure for table `daily_mission`
--

DROP TABLE IF EXISTS `daily_mission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `daily_mission` (
  `mission_id` int NOT NULL AUTO_INCREMENT,
  `mission_date` date NOT NULL,
  `mission_no` int NOT NULL,
  `segment_no` int NOT NULL DEFAULT '1',
  `mission_name` varchar(100) NOT NULL,
  `estimated_hours` decimal(4,2) NOT NULL,
  `start_time` time DEFAULT NULL,
  `end_time` time DEFAULT NULL,
  `actual_hours` decimal(4,2) DEFAULT NULL,
  `is_finished` tinyint NOT NULL DEFAULT '0',
  `is_long_term` tinyint NOT NULL DEFAULT '0',
  `is_added` tinyint NOT NULL DEFAULT '0',
  `project_id` int DEFAULT NULL,
  `notfinished_mission_id` int DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`mission_id`),
  UNIQUE KEY `uq_daily_mission_slot` (`mission_date`,`mission_no`,`segment_no`),
  KEY `fk_daily_mission_project` (`project_id`),
  KEY `fk_daily_mission_notfinished` (`notfinished_mission_id`),
  KEY `idx_daily_mission_date` (`mission_date`),
  CONSTRAINT `fk_daily_mission_notfinished` FOREIGN KEY (`notfinished_mission_id`) REFERENCES `notfinished_mission` (`notfinished_mission_id`),
  CONSTRAINT `fk_daily_mission_project` FOREIGN KEY (`project_id`) REFERENCES `project` (`project_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `daily_mission`
--

LOCK TABLES `daily_mission` WRITE;
/*!40000 ALTER TABLE `daily_mission` DISABLE KEYS */;
INSERT INTO `daily_mission` VALUES (1,'2026-09-22',1,1,'每日工作紀錄.app 小型模板',5.00,'13:15:00','16:20:00',3.08,1,0,0,NULL,NULL,'2026-09-22 07:46:10','2026-09-22 08:20:32'),(2,'2026-09-22',2,1,'準備明日的面試',2.00,'17:23:00','18:23:00',1.00,1,0,0,NULL,NULL,'2026-09-22 07:46:59','2026-09-22 08:22:13'),(3,'2026-09-22',3,1,'整理今日的資料',2.00,'20:25:00','21:26:00',1.02,0,0,0,NULL,NULL,'2026-09-22 07:48:07','2026-09-22 08:21:33'),(4,'2026-09-22',4,1,'陪貓貓',1.00,'22:07:00','22:07:00',0.00,0,0,0,NULL,NULL,'2026-09-22 14:04:44','2026-09-22 14:07:12'),(5,'2026-09-24',1,1,'大巨蛋面試',2.00,NULL,NULL,NULL,0,0,0,NULL,NULL,'2026-09-22 14:08:28','2026-09-22 14:08:28');
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
  `mission_name` varchar(100) NOT NULL,
  `start_date` date NOT NULL,
  `finish_date` date DEFAULT NULL,
  `is_finished` tinyint NOT NULL DEFAULT '0',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`notfinished_mission_id`)
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
  `project_name` varchar(100) NOT NULL,
  `start_date` date NOT NULL,
  `finish_date` date DEFAULT NULL,
  `is_finished` tinyint NOT NULL DEFAULT '0',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`project_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project`
--

LOCK TABLES `project` WRITE;
/*!40000 ALTER TABLE `project` DISABLE KEYS */;
/*!40000 ALTER TABLE `project` ENABLE KEYS */;
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

-- Dump completed on 2026-09-25 13:51:16
