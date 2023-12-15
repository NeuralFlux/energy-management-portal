INSERT INTO ServiceLocations (lid, cid, unit, address, zcode, billing_begin_date, sq_footage, num_bedrooms, num_occupants) VALUES 
(1, 1, 'Unit A', '101 Green Street', 10001, '2022-01-01', 1450, 2, 3),
(2, 1, 'Unit B', '102 Blue Avenue', 10002, '2022-01-15', 1500, 3, 4),
(3, 1, 'Unit C', '103 Yellow Road', 10003, '2022-02-01', 1570, 1, 2);

INSERT INTO AvailableModels (mid, type, model_num, properties) VALUES 
(1, 'Refrigerator', 'RF123', 'Energy Efficient'),
(2, 'Air Conditioner', 'AC456', 'Smart Cooling'),
(3, 'Heater', 'HT789', 'Rapid Heating'),
(4, 'Television', 'TV012', '4K Resolution'),
(5, 'Washing Machine', 'WM345', 'Low Water Use');

-- For each location, at least 3 devices, including a refrigerator
INSERT INTO Devices (dev_id, dev_name, mid, lid) VALUES 
(1, "Ref1", 1, 1), (2, "AC1", 2, 1), (3, "Heat1", 3, 1), -- Location 1
(4, "AC1", 1, 2), (5, "TV1", 4, 2), (6, "Wash1", 5, 2), -- Location 2
(7, "Ref1", 1, 3), (8, "AC1", 2, 3), (9, "Heat1", 3, 3); -- Location 3

-- Events for each device, including various types
INSERT INTO Events (eid, dev_id, label, value, created_at) VALUES 
(1, 2, 'switched on', 0, '2022-08-27 09:00:00'),
(2, 2, 'switched off', 0, '2022-08-27 10:00:00'),
(3, 2, 'energy use', 4, '2022-08-27 09:30:00'),
(4, 2, 'energy use', 7, '2022-08-27 10:30:00'),
(5, 2, 'energy use', 19, '2022-09-27 11:30:00'),
(6, 1, 'door opened', 0, '2022-08-27 09:15:00'),
(7, 1, 'door closed', 0, '2022-08-27 09:55:00'),
(8, 1, 'energy use', 18, '2022-08-27 09:30:00'),
(9, 1, 'energy use', 21, '2022-08-27 10:30:00'),
(10, 1, 'energy use', 21, '2022-09-27 10:30:00'),
(11, 3, 'energy use', 2, '2023-11-29 11:30:00'),
-- Loc 2
(12, 5, 'switched on', 0, '2022-08-27 09:00:00'),
(13, 5, 'switched off', 0, '2022-08-27 10:00:00'),
(14, 5, 'energy use', 14, '2022-08-27 09:30:00'),
(15, 5, 'energy use', 3, '2022-08-27 10:30:00'),
(16, 5, 'energy use', 92, '2022-09-27 11:30:00'),
(17, 4, 'door opened', 0, '2022-08-27 09:15:00'),
(18, 4, 'door closed', 0, '2022-08-27 09:55:00'),
(19, 4, 'energy use', 23, '2022-08-27 09:30:00'),
(20, 4, 'energy use', 45, '2022-08-27 10:30:00'),
(21, 4, 'energy use', 51, '2022-09-27 10:30:00'),
(22, 6, 'energy use', 2, '2023-11-29 11:30:00'),
-- Loc 3
(23, 8, 'switched on', 0, '2022-08-27 09:00:00'),
(24, 8, 'switched off', 0, '2022-08-27 10:00:00'),
(25, 8, 'energy use', 21, '2022-08-27 09:30:00'),
(26, 8, 'energy use', 78, '2022-08-27 10:30:00'),
(27, 8, 'energy use', 99, '2022-09-27 11:30:00'),
(28, 7, 'door opened', 0, '2022-08-27 09:15:00'),
(29, 7, 'door closed', 0, '2022-08-27 09:55:00'),
(30, 7, 'energy use', 1, '2022-08-27 09:30:00'),
(31, 7, 'energy use', 2, '2022-08-27 10:30:00'),
(32, 7, 'energy use', 3, '2022-09-27 10:30:00'),
(33, 9, 'energy use', 4, '2023-11-29 11:30:00');

-- PriceHistory
INSERT INTO PriceHistory (datehour, zcode, price) VALUES 
('2022-08-27 09:00:00', 10001, 0.15),
('2022-08-27 10:00:00', 10001, 0.18),
('2022-09-27 10:00:00', 10001, 0.18),
('2022-09-27 11:00:00', 10001, 0.20),
('2023-11-29 11:00:00', 10001, 0.25),
('2023-11-27 10:00:00', 10002, 0.20),
-- Loc 2
('2022-08-27 09:00:00', 10002, 0.15),
('2022-08-27 10:00:00', 10002, 0.18),
('2022-09-27 10:00:00', 10002, 0.18),
('2022-09-27 11:00:00', 10002, 0.20),
('2023-11-29 11:00:00', 10002, 0.25),
-- Loc 3
('2022-08-27 09:00:00', 10003, 0.15),
('2022-08-27 10:00:00', 10003, 0.18),
('2022-09-27 10:00:00', 10003, 0.18),
('2022-09-27 11:00:00', 10003, 0.20),
('2023-11-29 11:00:00', 10003, 0.25);

-- Q1 Procedure
DELIMITER //

CREATE PROCEDURE GetTotalEnergyConsumption(IN InputCID INT)
BEGIN
    WITH CustFilter(cid) AS (
        SELECT cid
        FROM Customers
        WHERE cid = InputCID
    )

    SELECT
        D.dev_id,
        SUM(E.value) AS TotalEnergyConsumption
    FROM
        CustFilter C
    JOIN ServiceLocations SL ON C.cid = SL.cid
    JOIN Devices D ON SL.lid = D.lid
    JOIN Events E ON D.dev_id = E.dev_id
    WHERE E.label = 'energy use'
        AND E.created_at >= NOW() - INTERVAL 1 DAY
    GROUP BY
        D.dev_id;
END //

DELIMITER ;
