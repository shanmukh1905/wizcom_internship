-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jan 08, 2025 at 07:01 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `stocks_view`
--

-- --------------------------------------------------------

--
-- Table structure for table `active_triggers`
--

CREATE TABLE `active_triggers` (
  `USER_ID` int(11) NOT NULL,
  `TRIGGER_ID` varchar(50) NOT NULL,
  `SYMBOL` varchar(50) NOT NULL,
  `SERIES` varchar(20) NOT NULL,
  `HNI` text DEFAULT NULL,
  `LOP` double DEFAULT NULL,
  `BOP` double DEFAULT NULL,
  `DEVIATION` float NOT NULL,
  `COMMENTS` text DEFAULT NULL,
  `STATUS` enum('ACTIVE','INACTIVE') DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `alerts_table`
--

CREATE TABLE `alerts_table` (
  `USER_ID` int(11) NOT NULL,
  `UNIQUE_ID` varchar(50) NOT NULL,
  `SYMBOL` varchar(50) NOT NULL,
  `SERIES` varchar(20) NOT NULL,
  `HNI` varchar(30) DEFAULT NULL,
  `OPEN_PRICE` double DEFAULT NULL,
  `HIGH_PRICE` double DEFAULT NULL,
  `LOW_PRICE` double DEFAULT NULL,
  `CLOSE_PRICE` double DEFAULT NULL,
  `LOP` double DEFAULT NULL,
  `BOP` double DEFAULT NULL,
  `DEVIATION` float NOT NULL,
  `COMMENTS` text DEFAULT NULL,
  `TRADE_DATE` date DEFAULT NULL,
  `TRIGGER_DATE` date NOT NULL,
  `TYPE` enum('LOP','BOP','BOTH') DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `bhavcopydata`
--

CREATE TABLE `bhavcopydata` (
  `id` bigint(20) NOT NULL,
  `UNIQUE_ID` varchar(50) NOT NULL,
  `SYMBOL` varchar(50) NOT NULL,
  `SERIES` varchar(10) NOT NULL,
  `TRADE_DATE` date NOT NULL,
  `PREV_CLOSE` double DEFAULT NULL,
  `OPEN_PRICE` double NOT NULL,
  `HIGH_PRICE` double NOT NULL,
  `LOW_PRICE` double NOT NULL,
  `LAST_PRICE` double NOT NULL,
  `CLOSE_PRICE` double NOT NULL,
  `AVG_PRICE` double DEFAULT NULL,
  `TTL_TRD_QNTY` double DEFAULT NULL,
  `TURNOVER_LACS` double DEFAULT NULL,
  `NO_OF_TRADES` double DEFAULT NULL,
  `DELIV_QTY` bigint(20) DEFAULT NULL,
  `DELIV_PER` float DEFAULT NULL,
  `ISIN` varchar(20) DEFAULT NULL,
  `COMMENTS` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `custom_triggers`
--

-- --------------------------------------------------------

--
-- Table structure for table `hni_list`
--

CREATE TABLE `hni_list` (
  `SYMBOL` varchar(50) NOT NULL,
  `COMPANY_NAME` varchar(50) NOT NULL,
  `HNI_DETAILS` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `USER_ID` int(11) NOT NULL,
  `USERNAME` varchar(50) NOT NULL,
  `PASSWORD` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `active_triggers`
--
ALTER TABLE `active_triggers`
  ADD PRIMARY KEY (`USER_ID`,`TRIGGER_ID`);

--
-- Indexes for table `alerts_table`
--
ALTER TABLE `alerts_table`
  ADD PRIMARY KEY (`USER_ID`,`UNIQUE_ID`);

--
-- Indexes for table `bhavcopydata`
--
ALTER TABLE `bhavcopydata`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `UNIQUE_ID` (`UNIQUE_ID`);

--
-- Indexes for table `custom_triggers`
--
ALTER TABLE `custom_triggers`
  ADD PRIMARY KEY (`USER_ID`,`UNIQUE_ID`);

--
-- Indexes for table `hni_list`
--
ALTER TABLE `hni_list`
  ADD PRIMARY KEY (`SYMBOL`,`HNI_DETAILS`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`USER_ID`),
  ADD UNIQUE KEY `USERNAME` (`USERNAME`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `bhavcopydata`
--
ALTER TABLE `bhavcopydata`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `USER_ID` int(11) NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
