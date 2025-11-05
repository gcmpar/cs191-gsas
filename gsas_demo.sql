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
-- Table structure for table `student`
--

DROP TABLE IF EXISTS `student`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student` (
  `student_no` varchar(20) NOT NULL,
  `full_name` varchar(100) NOT NULL,
  `ay_entry` varchar(15) DEFAULT NULL,
  `ay_latest` varchar(15) DEFAULT NULL,
  `degree` enum('PhD CS','MS CS','MS Bioinfo') DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `contact_number` varchar(20) DEFAULT NULL,
  `study_load` enum('Full-Time','Part-Time') DEFAULT NULL,
  `scholarship` varchar(50) DEFAULT NULL,
  `progress_status` enum('Probationary','Pre-proposal','Thesis Proposal','Thesis Defense','Candidacy','Qualifying Exam','Dissertation Proposal','Dissertation Defense','Graduate','Discontinued Program') DEFAULT NULL,
  `year_graduation` year DEFAULT NULL,
  `progress_link` varchar(255) DEFAULT NULL,
  `adviser_lab` varchar(100) DEFAULT NULL,
  `folder_link` varchar(255) DEFAULT NULL,
  `notes` text,
  PRIMARY KEY (`student_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student`
--

LOCK TABLES `student` WRITE;
/*!40000 ALTER TABLE `student` DISABLE KEYS */;
INSERT INTO `student` VALUES ('2019-00006','Jose Lim','2019-2020','2022-2023','MS Bioinfo','jose.lim@example.com','09401234572','Part-Time','None','Discontinued Program',NULL,'https://drive.google.com/jose','Dr. Tan / BioLab','https://drive.google.com/folder6','Dropped after proposal'),('2020-00002','Glenn Paragas','2020-2021','2023-2024','MS CS','glenn.paragas@example.com','09181234568','Full-Time','None','Graduate',2024,'https://drive.google.com/glenn','Dr. Cruz / DataLab','https://drive.google.com/folder2','Graduated with distinction'),('2021-00001','Lara Carrillo','2021-2022','2025-2026','PhD CS','lara.carrillo@example.com','09171234567','Full-Time','DOST','Thesis Proposal',NULL,'https://drive.google.com/lara','Dr. Santos / AI Lab','https://drive.google.com/folder1','On schedule for defense'),('2021-00004','Juancho Coronel','2021-2022','2024-2025','MS CS','juancho.coronel@example.com','09201234570','Full-Time','None','Thesis Defense',2025,'https://drive.google.com/juancho','Dr. Uy / SysLab','https://drive.google.com/folder4','Ready for defense'),('2022-00003','Jerwyn Angchua','2022-2023','2025-2026','MS Bioinfo','jerwyn.angchua@example.com','09191234569','Part-Time','University Grant','Pre-proposal',NULL,'https://drive.google.com/jerwyn','Dr. Tan / BioLab','https://drive.google.com/folder3','Delayed due to schedule'),('2023-00005','Kevin Atienza','2023-2024','2025-2026','PhD CS','kevin.atienza@example.com','09301234571','Full-Time','DOST','Candidacy',NULL,'https://drive.google.com/kevin','Dr. Reyes / NLP Lab','https://drive.google.com/folder5','Passed qualifying exam');
/*!40000 ALTER TABLE `student` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-11-05 13:29:50
