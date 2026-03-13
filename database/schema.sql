-- Схема базы данных для системы мониторинга батарей
-- Нормализация: 3NF

-- Удаление таблиц если существуют
DROP TABLE IF EXISTS incidents CASCADE;
DROP TABLE IF EXISTS measurements CASCADE;
DROP TABLE IF EXISTS batteries CASCADE;
DROP TABLE IF EXISTS equipment CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Таблица пользователей
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('operator', 'engineer', 'admin')),
    full_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица оборудования
CREATE TABLE equipment (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    location VARCHAR(100) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'maintenance')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица батарей
CREATE TABLE batteries (
    id SERIAL PRIMARY KEY,
    equipment_id INTEGER NOT NULL REFERENCES equipment(id) ON DELETE CASCADE,
    serial_number VARCHAR(50) UNIQUE NOT NULL,
    capacity DECIMAL(10,2) NOT NULL, -- емкость в Ah
    voltage_nominal DECIMAL(5,2) NOT NULL, -- номинальное напряжение
    install_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'maintenance', 'decommissioned')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица измерений
CREATE TABLE measurements (
    id SERIAL PRIMARY KEY,
    battery_id INTEGER NOT NULL REFERENCES batteries(id) ON DELETE CASCADE,
    voltage DECIMAL(6,3) NOT NULL CHECK (voltage > 0), -- напряжение в В
    current DECIMAL(8,3) NOT NULL CHECK (current >= 0), -- ток в А
    charge_level DECIMAL(5,2) NOT NULL CHECK (charge_level >= 0 AND charge_level <= 100), -- уровень заряда %
    temperature DECIMAL(5,2) NOT NULL CHECK (temperature <= 80), -- температура в °C
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    measured_by INTEGER REFERENCES users(id)
);

-- Таблица инцидентов
CREATE TABLE incidents (
    id SERIAL PRIMARY KEY,
    measurement_id INTEGER REFERENCES measurements(id) ON DELETE SET NULL,
    battery_id INTEGER REFERENCES batteries(id) ON DELETE CASCADE,
    incident_type VARCHAR(50) NOT NULL CHECK (incident_type IN ('overheat', 'low_charge', 'voltage_spike', 'current_surge', 'critical_failure', 'warning')),
    description TEXT NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    is_resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP,
    resolved_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для оптимизации запросов
CREATE INDEX idx_batteries_equipment_id ON batteries(equipment_id);
CREATE INDEX idx_measurements_battery_id ON measurements(battery_id);
CREATE INDEX idx_measurements_timestamp ON measurements(timestamp);
CREATE INDEX idx_incidents_battery_id ON incidents(battery_id);
CREATE INDEX idx_incidents_incident_type ON incidents(incident_type);
CREATE INDEX idx_incidents_created_at ON incidents(created_at);

-- Триггер для автоматического обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_equipment_updated_at BEFORE UPDATE ON equipment
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_batteries_updated_at BEFORE UPDATE ON batteries
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Функция для автоматического создания инцидентов при критических значениях
CREATE OR REPLACE FUNCTION check_critical_values()
RETURNS TRIGGER AS $$
BEGIN
    -- Проверка перегрева
    IF NEW.temperature > 60 THEN
        INSERT INTO incidents (measurement_id, battery_id, incident_type, description, severity)
        VALUES (NEW.id, NEW.battery_id, 'overheat', 
                'Критическая температура: ' || NEW.temperature || '°C', 
                CASE WHEN NEW.temperature > 70 THEN 'critical' ELSE 'high' END);
    END IF;

    -- Проверка низкого заряда
    IF NEW.charge_level < 20 THEN
        INSERT INTO incidents (measurement_id, battery_id, incident_type, description, severity)
        VALUES (NEW.id, NEW.battery_id, 'low_charge', 
                'Низкий уровень заряда: ' || NEW.charge_level || '%', 
                CASE WHEN NEW.charge_level < 10 THEN 'critical' ELSE 'high' END);
    END IF;

    -- Проверка напряжения
    IF NEW.voltage > 15 OR NEW.voltage < 10 THEN
        INSERT INTO incidents (measurement_id, battery_id, incident_type, description, severity)
        VALUES (NEW.id, NEW.battery_id, 'voltage_spike', 
                'Аномальное напряжение: ' || NEW.voltage || 'V', 'high');
    END IF;

    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER check_measurements AFTER INSERT ON measurements
    FOR EACH ROW EXECUTE FUNCTION check_critical_values();
