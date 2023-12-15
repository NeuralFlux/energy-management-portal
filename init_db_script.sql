CREATE TABLE `Customers` (
  `cid` INT AUTO_INCREMENT,
  `username` VARCHAR(50) NOT NULL,
  `email` VARCHAR(100) NOT NULL,
  `hashed_password` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`cid`)
);

CREATE TABLE `ServiceLocations` (
  `lid` integer PRIMARY KEY AUTO_INCREMENT,
  `cid` integer,
  `unit` varchar(255),
  `address` varchar(255),
  `zcode` integer,
  `billing_begin_date` date,
  `sq_footage` numeric,
  `num_bedrooms` smallint,
  `num_occupants` smallint
);

CREATE TABLE `AvailableModels` (
  `mid` integer PRIMARY KEY AUTO_INCREMENT,
  `type` varchar(255),
  `model_num` varchar(255),
  `properties` varchar(255)
);

CREATE TABLE `Devices` (
  `dev_id` integer PRIMARY KEY AUTO_INCREMENT,
  `dev_name` varchar(50) NOT NULL,
  `mid` integer,
  `lid` integer
);

CREATE TABLE `Events` (
  `eid` integer PRIMARY KEY AUTO_INCREMENT,
  `dev_id` integer,
  `label` varchar(255),
  `value` numeric,
  `created_at` timestamp
);

CREATE TABLE `PriceHistory` (
  `datehour` timestamp,
  `zcode` integer,
  `price` numeric(8,4),
  PRIMARY KEY (`datehour`, `zcode`)
);

ALTER TABLE `ServiceLocations` ADD FOREIGN KEY (`cid`) REFERENCES `Customers` (`cid`);

ALTER TABLE `Devices` ADD FOREIGN KEY (`mid`) REFERENCES `AvailableModels` (`mid`);

ALTER TABLE `Devices` ADD FOREIGN KEY (`lid`) REFERENCES `ServiceLocations` (`lid`);

ALTER TABLE `Events` ADD FOREIGN KEY (`dev_id`) REFERENCES `Devices` (`dev_id`);
