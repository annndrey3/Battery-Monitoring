"""Тесты API измерений (Measurements)"""

import pytest


class TestMeasurementsAPI:
    """Тесты операций с измерениями"""
    
    @pytest.fixture
    def battery_id(self, client):
        """Создает тестовую батарею и возвращает ID"""
        # Create equipment first
        equipment_data = {
            "name": "Test Equipment",
            "type": "UPS",
            "location": "Test Room",
            "status": "active"
        }
        equipment_response = client.post("/equipment/", json=equipment_data)
        equipment_id = equipment_response.json()["id"]
        
        # Create battery
        battery_data = {
            "equipment_id": equipment_id,
            "serial_number": "BAT-M001",
            "capacity": 100,
            "voltage_nominal": 12.0,
            "status": "active",
            "install_date": "2024-01-01"
        }
        battery_response = client.post("/batteries/", json=battery_data)
        return battery_response.json()["id"]
    
    def test_create_measurement(self, client, battery_id):
        """Создание измерения"""
        measurement_data = {
            "battery_id": battery_id,
            "voltage": 12.5,
            "current": 5.0,
            "charge_level": 85.0,
            "temperature": 25.0
        }
        response = client.post("/measurements/", json=measurement_data)
        assert response.status_code == 200
        data = response.json()
        assert float(data["voltage"]) == 12.5
        assert float(data["charge_level"]) == 85.0
        assert float(data["temperature"]) == 25.0
    
    def test_create_measurement_invalid_battery(self, client):
        """Создание измерения с несуществующей батареей"""
        measurement_data = {
            "battery_id": 99999,
            "voltage": 12.5,
            "current": 5.0,
            "charge_level": 85.0,
            "temperature": 25.0
        }
        response = client.post("/measurements/", json=measurement_data)
        assert response.status_code == 404
    
    def test_get_measurements_list(self, client, battery_id):
        """Получение списка измерений"""
        # Create measurement
        measurement_data = {
            "battery_id": battery_id,
            "voltage": 12.5,
            "current": 5.0,
            "charge_level": 85.0,
            "temperature": 25.0
        }
        client.post("/measurements/", json=measurement_data)
        
        response = client.get("/measurements/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
    
    def test_get_battery_history(self, client, battery_id):
        """Получение истории измерений батареи"""
        # Create multiple measurements
        for i in range(3):
            measurement_data = {
                "battery_id": battery_id,
                "voltage": 12.0 + i,
                "current": 5.0,
                "charge_level": 80.0 + i,
                "temperature": 25.0 + i
            }
            client.post("/measurements/", json=measurement_data)
        
        response = client.get(f"/measurements/history/{battery_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1  # All 3 measurements grouped by hour
    
    def test_delete_measurement(self, client, battery_id):
        """Удаление измерения"""
        # Create
        measurement_data = {
            "battery_id": battery_id,
            "voltage": 12.5,
            "current": 5.0,
            "charge_level": 85.0,
            "temperature": 25.0
        }
        create_response = client.post("/measurements/", json=measurement_data)
        measurement_id = create_response.json()["id"]
        
        # Delete
        response = client.delete(f"/measurements/{measurement_id}")
        assert response.status_code == 200


class TestMeasurementValidation:
    """Тесты валидации данных измерений"""
    
    @pytest.fixture
    def battery_id(self, client):
        """Создает тестовую батарею"""
        equipment_data = {
            "name": "Test Equipment",
            "type": "UPS",
            "location": "Test Room",
            "status": "active"
        }
        equipment_response = client.post("/equipment/", json=equipment_data)
        equipment_id = equipment_response.json()["id"]
        
        battery_data = {
            "equipment_id": equipment_id,
            "serial_number": "BAT-V001",
            "capacity": 100,
            "voltage_nominal": 12.0,
            "status": "active",
            "install_date": "2024-01-01"
        }
        battery_response = client.post("/batteries/", json=battery_data)
        return battery_response.json()["id"]
    
    def test_temperature_too_high(self, client, battery_id):
        """Температура выше допустимой (> 80)"""
        measurement_data = {
            "battery_id": battery_id,
            "voltage": 12.5,
            "current": 5.0,
            "charge_level": 85.0,
            "temperature": 85.0  # too high
        }
        response = client.post("/measurements/", json=measurement_data)
        assert response.status_code == 422
    
    def test_charge_level_negative(self, client, battery_id):
        """Отрицательный уровень заряда"""
        measurement_data = {
            "battery_id": battery_id,
            "voltage": 12.5,
            "current": 5.0,
            "charge_level": -10.0,  # invalid
            "temperature": 25.0
        }
        response = client.post("/measurements/", json=measurement_data)
        assert response.status_code == 422
    
    def test_charge_level_over_100(self, client, battery_id):
        """Уровень заряда больше 100%"""
        measurement_data = {
            "battery_id": battery_id,
            "voltage": 12.5,
            "current": 5.0,
            "charge_level": 110.0,  # too high
            "temperature": 25.0
        }
        response = client.post("/measurements/", json=measurement_data)
        assert response.status_code == 422
    
    def test_negative_voltage(self, client, battery_id):
        """Отрицательное напряжение"""
        measurement_data = {
            "battery_id": battery_id,
            "voltage": -5.0,  # invalid
            "current": 5.0,
            "charge_level": 85.0,
            "temperature": 25.0
        }
        response = client.post("/measurements/", json=measurement_data)
        assert response.status_code == 422
    
    def test_negative_current(self, client, battery_id):
        """Отрицательный ток"""
        measurement_data = {
            "battery_id": battery_id,
            "voltage": 12.5,
            "current": -5.0,  # invalid
            "charge_level": 85.0,
            "temperature": 25.0
        }
        response = client.post("/measurements/", json=measurement_data)
        assert response.status_code == 422


class TestAutoIncidentCreation:
    """Тесты автоматического создания инцидентов"""
    
    @pytest.fixture
    def battery_id(self, client):
        """Создает тестовую батарею"""
        equipment_data = {
            "name": "Test Equipment",
            "type": "UPS",
            "location": "Test Room",
            "status": "active"
        }
        equipment_response = client.post("/equipment/", json=equipment_data)
        equipment_id = equipment_response.json()["id"]
        
        battery_data = {
            "equipment_id": equipment_id,
            "serial_number": "BAT-AUTO",
            "capacity": 100,
            "voltage_nominal": 12.0,
            "status": "active",
            "install_date": "2024-01-01"
        }
        battery_response = client.post("/batteries/", json=battery_data)
        return battery_response.json()["id"]
    
    def test_critical_temperature_creates_incident(self, client, battery_id):
        """Критическая температура создает инцидент"""
        measurement_data = {
            "battery_id": battery_id,
            "voltage": 12.5,
            "current": 5.0,
            "charge_level": 85.0,
            "temperature": 65.0  # critical (> 60)
        }
        client.post("/measurements/", json=measurement_data)
        
        # Check incident was created
        response = client.get("/incidents/")
        incidents = response.json()
        
        # Should have at least one incident
        assert len(incidents) >= 1
        
        # Find the overheat incident
        overheat_incidents = [i for i in incidents if i["incident_type"] == "overheat"]
        assert len(overheat_incidents) >= 1
    
    def test_low_charge_creates_incident(self, client, battery_id):
        """Низкий заряд создает инцидент"""
        measurement_data = {
            "battery_id": battery_id,
            "voltage": 11.0,
            "current": 2.0,
            "charge_level": 15.0,  # low (< 20)
            "temperature": 25.0
        }
        client.post("/measurements/", json=measurement_data)
        
        # Check incident was created
        response = client.get("/incidents/")
        incidents = response.json()
        
        low_charge_incidents = [i for i in incidents if i["incident_type"] == "low_charge"]
        assert len(low_charge_incidents) >= 1
