-- 10 сложных SQL запросов для аналитики

-- 1. Средний уровень заряда батарей по оборудованию
SELECT 
    e.name AS equipment_name,
    e.location,
    COUNT(DISTINCT b.id) AS battery_count,
    ROUND(AVG(m.charge_level), 2) AS avg_charge_level,
    ROUND(MIN(m.charge_level), 2) AS min_charge_level,
    ROUND(MAX(m.charge_level), 2) AS max_charge_level
FROM equipment e
LEFT JOIN batteries b ON e.id = b.equipment_id
LEFT JOIN measurements m ON b.id = m.battery_id
WHERE m.timestamp >= NOW() - INTERVAL '24 hours'
GROUP BY e.id, e.name, e.location
ORDER BY avg_charge_level ASC;

-- 2. Поиск батарей с критической температурой (>60°C)
SELECT 
    e.name AS equipment_name,
    b.serial_number,
    b.capacity,
    m.temperature,
    m.charge_level,
    m.timestamp,
    CASE 
        WHEN m.temperature > 70 THEN 'КРИТИЧЕСКАЯ'
        ELSE 'Высокая'
    END AS alert_level
FROM measurements m
JOIN batteries b ON m.battery_id = b.id
JOIN equipment e ON b.equipment_id = e.id
WHERE m.temperature > 60
AND m.timestamp >= NOW() - INTERVAL '1 hour'
ORDER BY m.temperature DESC;

-- 3. История измерений батареи с агрегацией по часам
SELECT 
    DATE_TRUNC('hour', m.timestamp) AS hour,
    b.serial_number,
    ROUND(AVG(m.voltage), 3) AS avg_voltage,
    ROUND(AVG(m.current), 3) AS avg_current,
    ROUND(AVG(m.charge_level), 2) AS avg_charge,
    ROUND(AVG(m.temperature), 2) AS avg_temp,
    COUNT(*) AS measurement_count
FROM measurements m
JOIN batteries b ON m.battery_id = b.id
WHERE b.id = :battery_id
AND m.timestamp >= NOW() - INTERVAL '7 days'
GROUP BY DATE_TRUNC('hour', m.timestamp), b.serial_number
ORDER BY hour DESC;

-- 4. Статистика инцидентов по типам и месяцам
SELECT 
    incident_type,
    TO_CHAR(created_at, 'YYYY-MM') AS month,
    COUNT(*) AS incident_count,
    COUNT(CASE WHEN is_resolved THEN 1 END) AS resolved_count,
    COUNT(CASE WHEN severity = 'critical' THEN 1 END) AS critical_count,
    ROUND(AVG(EXTRACT(EPOCH FROM (COALESCE(resolved_at, NOW()) - created_at))/3600), 2) AS avg_resolution_hours
FROM incidents
WHERE created_at >= NOW() - INTERVAL '6 months'
GROUP BY incident_type, TO_CHAR(created_at, 'YYYY-MM')
ORDER BY month DESC, incident_count DESC;

-- 5. Средняя напряжение батарей с отклонением от номинала
SELECT 
    b.id,
    b.serial_number,
    e.name AS equipment_name,
    b.voltage_nominal,
    ROUND(AVG(m.voltage), 3) AS avg_voltage,
    ROUND(AVG(m.voltage) - b.voltage_nominal, 3) AS voltage_deviation,
    ROUND(ABS(AVG(m.voltage) - b.voltage_nominal) / b.voltage_nominal * 100, 2) AS deviation_percent,
    CASE 
        WHEN ABS(AVG(m.voltage) - b.voltage_nominal) / b.voltage_nominal > 0.1 THEN 'ТРЕВОГА'
        WHEN ABS(AVG(m.voltage) - b.voltage_nominal) / b.voltage_nominal > 0.05 THEN 'ВНИМАНИЕ'
        ELSE 'НОРМА'
    END AS status
FROM batteries b
JOIN equipment e ON b.equipment_id = e.id
JOIN measurements m ON b.id = m.battery_id
WHERE m.timestamp >= NOW() - INTERVAL '24 hours'
GROUP BY b.id, b.serial_number, e.name, b.voltage_nominal
ORDER BY deviation_percent DESC;

-- 6. Оборудование с наибольшим количеством инцидентов
SELECT 
    e.id,
    e.name AS equipment_name,
    e.type,
    e.location,
    COUNT(DISTINCT b.id) AS battery_count,
    COUNT(i.id) AS total_incidents,
    COUNT(CASE WHEN i.severity = 'critical' THEN 1 END) AS critical_incidents,
    COUNT(CASE WHEN i.incident_type = 'overheat' THEN 1 END) AS overheat_count,
    COUNT(CASE WHEN i.incident_type = 'low_charge' THEN 1 END) AS low_charge_count,
    MAX(i.created_at) AS last_incident_date
FROM equipment e
JOIN batteries b ON e.id = b.equipment_id
LEFT JOIN incidents i ON b.id = i.battery_id
WHERE i.created_at >= NOW() - INTERVAL '30 days'
GROUP BY e.id, e.name, e.type, e.location
ORDER BY total_incidents DESC
LIMIT 10;

-- 7. Максимальная температура батареи с детализацией
SELECT 
    b.serial_number,
    e.name AS equipment_name,
    MAX(m.temperature) AS max_temp,
    MIN(m.temperature) AS min_temp,
    ROUND(AVG(m.temperature), 2) AS avg_temp,
    m_max.timestamp AS max_temp_time,
    COUNT(CASE WHEN m.temperature > 60 THEN 1 END) AS overheat_count
FROM batteries b
JOIN equipment e ON b.equipment_id = e.id
JOIN measurements m ON b.id = m.battery_id
JOIN (
    SELECT battery_id, temperature, timestamp
    FROM measurements m1
    WHERE (battery_id, temperature) IN (
        SELECT battery_id, MAX(temperature)
        FROM measurements
        WHERE timestamp >= NOW() - INTERVAL '7 days'
        GROUP BY battery_id
    )
) m_max ON b.id = m_max.battery_id
WHERE m.timestamp >= NOW() - INTERVAL '7 days'
GROUP BY b.id, b.serial_number, e.name, m_max.timestamp
ORDER BY max_temp DESC;

-- 8. Минимальный уровень заряда с прогнозом разряда
SELECT 
    b.id,
    b.serial_number,
    e.name AS equipment_name,
    MIN(m.charge_level) AS min_charge,
    MAX(m.charge_level) AS max_charge,
    ROUND(AVG(m.charge_level), 2) AS avg_charge,
    m_min.timestamp AS min_charge_time,
    -- Прогноз времени до полного разряда (если тренд сохранится)
    CASE 
        WHEN (MAX(m.charge_level) - MIN(m.charge_level)) > 0 
        THEN ROUND(
            MIN(m.charge_level) / 
            NULLIF((MAX(m.charge_level) - MIN(m.charge_level)) / 
            NULLIF(EXTRACT(EPOCH FROM (MAX(m.timestamp) - MIN(m.timestamp)))/3600, 0), 0)
        , 2)
        ELSE NULL
    END AS estimated_hours_to_empty
FROM batteries b
JOIN equipment e ON b.equipment_id = e.id
JOIN measurements m ON b.id = m.battery_id
JOIN (
    SELECT battery_id, charge_level, timestamp
    FROM measurements m1
    WHERE (battery_id, charge_level) IN (
        SELECT battery_id, MIN(charge_level)
        FROM measurements
        WHERE timestamp >= NOW() - INTERVAL '24 hours'
        GROUP BY battery_id
    )
) m_min ON b.id = m_min.battery_id
WHERE m.timestamp >= NOW() - INTERVAL '24 hours'
GROUP BY b.id, b.serial_number, e.name, m_min.timestamp
ORDER BY min_charge ASC;

-- 9. Средний ток с группировкой по диапазонам
SELECT 
    e.name AS equipment_name,
    b.serial_number,
    CASE 
        WHEN AVG(m.current) < 1 THEN 'Низкий (<1A)'
        WHEN AVG(m.current) < 5 THEN 'Средний (1-5A)'
        WHEN AVG(m.current) < 10 THEN 'Высокий (5-10A)'
        ELSE 'Критический (>10A)'
    END AS current_range,
    ROUND(AVG(m.current), 3) AS avg_current,
    ROUND(MAX(m.current), 3) AS max_current,
    ROUND(MIN(m.current), 3) AS min_current,
    COUNT(*) AS measurement_count
FROM measurements m
JOIN batteries b ON m.battery_id = b.id
JOIN equipment e ON b.equipment_id = e.id
WHERE m.timestamp >= NOW() - INTERVAL '24 hours'
GROUP BY e.name, b.serial_number
ORDER BY avg_current DESC;

-- 10. Количество измерений по оборудованию с активностью операторов
SELECT 
    e.id AS equipment_id,
    e.name AS equipment_name,
    e.location,
    COUNT(DISTINCT b.id) AS battery_count,
    COUNT(m.id) AS total_measurements,
    COUNT(DISTINCT DATE(m.timestamp)) AS days_with_measurements,
    ROUND(COUNT(m.id)::DECIMAL / NULLIF(COUNT(DISTINCT b.id), 0), 1) AS avg_measurements_per_battery,
    COUNT(DISTINCT m.measured_by) AS operator_count,
    STRING_AGG(DISTINCT u.full_name, ', ') AS operators,
    MAX(m.timestamp) AS last_measurement
FROM equipment e
LEFT JOIN batteries b ON e.id = b.equipment_id
LEFT JOIN measurements m ON b.id = m.battery_id
LEFT JOIN users u ON m.measured_by = u.id
WHERE m.timestamp >= NOW() - INTERVAL '30 days'
GROUP BY e.id, e.name, e.location
ORDER BY total_measurements DESC;
