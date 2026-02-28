-- MySQL dump 10.13  Distrib 8.0.43, for macos15 (arm64)
--
-- Host: localhost    Database: gsas_demo
-- ------------------------------------------------------
-- Server version	9.4.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `applicant`
--

DROP TABLE IF EXISTS `applicant`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `applicant` (
  `applicant_id` varchar(20) NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `middle_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `applicant_status` enum('applying','rejected','enrolled','deferred') NOT NULL,
  `email` varchar(100) NOT NULL,
  `contact_number` varchar(20) NOT NULL,
  `notes` text,
  PRIMARY KEY (`applicant_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `applicant`
--

LOCK TABLES `applicant` WRITE;
/*!40000 ALTER TABLE `applicant` DISABLE KEYS */;
/*!40000 ALTER TABLE `applicant` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `application`
--

DROP TABLE IF EXISTS `application`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `application` (
  `application_id` varchar(20) NOT NULL,
  `applicant_id` varchar(20) NOT NULL,
  `application_status` enum('processing','accepted','rejected') NOT NULL,
  `date_applied` date NOT NULL,
  `program` enum('PhD CS','MS CS','MS Bioinfo') NOT NULL,
  `folder_link` varchar(255) NOT NULL,
  `study_load` enum('Full-Time','Part-Time') NOT NULL,
  PRIMARY KEY (`application_id`),
  KEY `applicant_id` (`applicant_id`),
  CONSTRAINT `application_ibfk_1` FOREIGN KEY (`applicant_id`) REFERENCES `applicant` (`applicant_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `application`
--

LOCK TABLES `application` WRITE;
/*!40000 ALTER TABLE `application` DISABLE KEYS */;
/*!40000 ALTER TABLE `application` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `course`
--

DROP TABLE IF EXISTS `course`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `course` (
  `course_id` varchar(20) NOT NULL,
  `program_id` varchar(20) NOT NULL,
  `course_code` varchar(20) NOT NULL,
  `course_name` varchar(50) NOT NULL,
  `units` tinyint NOT NULL,
  `description` varchar(200) NOT NULL,
  PRIMARY KEY (`course_id`),
  KEY `program_id` (`program_id`),
  CONSTRAINT `course_ibfk_1` FOREIGN KEY (`program_id`) REFERENCES `program` (`program_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `course`
--

LOCK TABLES `course` WRITE;
/*!40000 ALTER TABLE `course` DISABLE KEYS */;
/*!40000 ALTER TABLE `course` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `enrolled`
--

-- DROP TABLE IF EXISTS `enrolled`;
-- /*!40101 SET @saved_cs_client     = @@character_set_client */;
-- /*!50503 SET character_set_client = utf8mb4 */;
-- CREATE TABLE `enrolled` (
--   `enrolled_id` varchar(20) NOT NULL,
--   `applicant_id` varchar(20) NOT NULL,
--   `course_id` varchar(20) NOT NULL,
--   PRIMARY KEY (`enrolled_id`),
--   KEY `applicant_id` (`applicant_id`),
--   KEY `course_id` (`course_id`),
--   CONSTRAINT `enrolled_ibfk_1` FOREIGN KEY (`applicant_id`) REFERENCES `applicant` (`applicant_id`),
--   CONSTRAINT `enrolled_ibfk_2` FOREIGN KEY (`course_id`) REFERENCES `course` (`course_id`)
-- ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
-- /*!40101 SET character_set_client = @saved_cs_client */;

-- --
-- -- Dumping data for table `enrolled`
-- --

-- LOCK TABLES `enrolled` WRITE;
-- /*!40000 ALTER TABLE `enrolled` DISABLE KEYS */;
-- /*!40000 ALTER TABLE `enrolled` ENABLE KEYS */;
-- UNLOCK TABLES;

--
-- Table structure for table `equivalence_group_map`
--

DROP TABLE IF EXISTS `equivalence_group_map`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `equivalence_group_map` (
  `map_id` varchar(20) NOT NULL,
  `group_id` varchar(20) NOT NULL,
  `course_id` varchar(20) NOT NULL,
  PRIMARY KEY (`map_id`),
  KEY `group_id` (`group_id`),
  KEY `course_id` (`course_id`),
  CONSTRAINT `equivalence_group_map_ibfk_1` FOREIGN KEY (`group_id`) REFERENCES `equivalence_groups` (`group_id`),
  CONSTRAINT `equivalence_group_map_ibfk_2` FOREIGN KEY (`course_id`) REFERENCES `course` (`course_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `equivalence_group_map`
--

LOCK TABLES `equivalence_group_map` WRITE;
/*!40000 ALTER TABLE `equivalence_group_map` DISABLE KEYS */;
/*!40000 ALTER TABLE `equivalence_group_map` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `equivalence_groups`
--

DROP TABLE IF EXISTS `equivalence_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `equivalence_groups` (
  `group_id` varchar(20) NOT NULL,
  `course_id` varchar(20) NOT NULL,
  PRIMARY KEY (`group_id`),
  KEY `course_id` (`course_id`),
  CONSTRAINT `equivalence_groups_ibfk_1` FOREIGN KEY (`course_id`) REFERENCES `course` (`course_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `equivalence_groups`
--

LOCK TABLES `equivalence_groups` WRITE;
/*!40000 ALTER TABLE `equivalence_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `equivalence_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `prerequisite`
--

DROP TABLE IF EXISTS `prerequisite`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `prerequisite` (
  `prereq_entry_id` varchar(20) NOT NULL,
  `course_id` varchar(20) NOT NULL,
  `prereq_id` varchar(20) NOT NULL,
  PRIMARY KEY (`prereq_entry_id`),
  KEY `course_id` (`course_id`),
  KEY `prereq_id` (`prereq_id`),
  CONSTRAINT `prerequisite_ibfk_1` FOREIGN KEY (`course_id`) REFERENCES `course` (`course_id`),
  CONSTRAINT `prerequisite_ibfk_2` FOREIGN KEY (`prereq_id`) REFERENCES `course` (`course_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `prerequisite`
--

LOCK TABLES `prerequisite` WRITE;
/*!40000 ALTER TABLE `prerequisite` DISABLE KEYS */;
/*!40000 ALTER TABLE `prerequisite` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `program`
--

DROP TABLE IF EXISTS `program`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `program` (
  `program_id` varchar(20) NOT NULL,
  `school_id` varchar(20) NOT NULL,
  `program_name` varchar(50) NOT NULL,
  `description` varchar(200) NOT NULL,
  PRIMARY KEY (`program_id`),
  KEY `school_id` (`school_id`),
  CONSTRAINT `program_ibfk_1` FOREIGN KEY (`school_id`) REFERENCES `school` (`school_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `program`
--

LOCK TABLES `program` WRITE;
/*!40000 ALTER TABLE `program` DISABLE KEYS */;
/*!40000 ALTER TABLE `program` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `school`
--

DROP TABLE IF EXISTS `school`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `school` (
  `school_id` varchar(20) NOT NULL,
  `school_name` varchar(100) NOT NULL,
  PRIMARY KEY (`school_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `school`
--

LOCK TABLES `school` WRITE;
/*!40000 ALTER TABLE `school` DISABLE KEYS */;
/*!40000 ALTER TABLE `school` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `application_transcript`
--

DROP TABLE IF EXISTS `application_transcript`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `application_transcript` (
  `transcript_id` varchar(20) NOT NULL,
  `application_id` varchar(20) NOT NULL,
  `course_id` varchar(20) NOT NULL,
  `academic_year` varchar(10) NOT NULL,
  `semester` enum('1st','2nd','3rd') NOT NULL,
  `grade` enum('1.00','1.25','1.50','1.75','2.00','2.25','2.50','2.75','3.00','4.00','5.00','INC','DROP') NOT NULL,
  PRIMARY KEY (`transcript_id`),
  KEY `application_id` (`application_id`),
  KEY `course_id` (`course_id`),
  CONSTRAINT `application_transcript_ibfk_1` FOREIGN KEY (`application_id`) REFERENCES `application` (`application_id`),
  CONSTRAINT `application_transcript_ibfk_2` FOREIGN KEY (`course_id`) REFERENCES `course` (`course_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `application_transcript`
--

LOCK TABLES `application_transcript` WRITE;
/*!40000 ALTER TABLE `application_transcript` DISABLE KEYS */;
/*!40000 ALTER TABLE `application_transcript` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-02-11 12:23:27
