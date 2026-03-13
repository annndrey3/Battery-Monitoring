"""Тесты API батарей (Batteries)"""

import pytest
from datetime import date


class TestBatteriesAPI:
    """Тесты CRUD операций для батарей"""
    
    @pytest.fixture
    def equipment_id(self, client):
        """Создает тестовое оборудование и возвращает ID"""
        equipment_data = {
            "name": "Test Equipment",
            "type": "UPS",
            "location": "Test Room",
            "status": "active"
        }
        response = client.post("/equipment/", json=equipment_data)
        return response.json()["id"]
    
    def test_create_battery(self, client, equipment_id):
        """Создание батареи"""
        battery_data = {
            "equipment_id": equipment_id,
            "serial_number": "BAT-001",
            "capacity": 100,
            "voltage_nominal": 12.0,
            "install_date": str(date.today()),
            "status": "active"
        }
        response = client.post("/batteries/", json=battery_data)
        assert response.status_code == 200
        data = response.json()
        assert data["serial_number"] == "BAT-001"
        assert data["equipment_id"] == equipment_id
        assert data["status"] == "active"
    
    def test_create_battery_invalid_equipment(self, client):
        """Создание батареи с несуществующим оборудованием"""
        battery_data = {
            "equipment_id": 99999,
            "serial_number": "BAT-002",
            "capacity": 100,
            "voltage_nominal": 12.0,
            "status": "active"
        }
        # Expect validation error (422) for non-existent equipment
        response = client.post("/batteries/", json=battery_data)
        assert response.status_code == 422
    
    def test_create_duplicate_serial(self, client, equipment_id):
        """Создание батареи с дублирующимся серийным номером"""
        battery_data = {
            "equipment_id": equipment_id,
            "serial_number": "UNIQUE-001",
            "capacity": 100,
            "voltage_nominal": 12.0,
            "status": "active"
        }
        # First creation
        client.post("/batteries/", json=battery_data)
        # Duplicate
        response = client.post("/batteries/", json=battery_data)
        assert response.status_code == 422
    
    def test_get_batteries_list(self, client, equipment_id):
        """Получение списка батарей"""
        # Create battery
        battery_data = {
            "equipment_id": equipment_id,
            "serial_number": "BAT-003",
            "capacity": 50,
            "voltage_nominal": 24.0,
            "install_date": "2024-01-01",
            "status": "active"
        }
        client.post("/batteries/", json=battery_data)
        
        response = client.get("/batteries/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
    
    def test_get_batteries_by_equipment(self, client, equipment_id):
        """Фильтрация батарей по оборудованию"""
        # Create battery
        battery_data = {
            "equipment_id": equipment_id,
            "serial_number": "BAT-M001",
            "capacity": 100,
            "voltage_nominal": 12.0,
            "install_date": "2024-01-01",
            "status": "active"
        }
        client.post("/batteries/", json=battery_data)
        
        response = client.get(f"/batteries/?equipment_id={equipment_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["equipment_id"] == equipment_id
        
        # Create battery
        battery_data = {
            "equipment_id": equipment_id,
            "serial_number": "BAT-R001",
            "capacity": 100,
            "voltage_nominal": 12.0,
            "install_date": "2024-01-01",
            "status": "active"
        }
        battery_response = client.post("/batteries/", json=battery_data)
        batteries = [battery_response.json()["id"]]
        
        battery_data2 = {
            "equipment_id": equipment_id,
            "serial_number": "BAT-R002",
            "capacity": 150,
            "voltage_nominal": 24.0,
            "install_date": "2024-01-01",
            "status": "active"
        }
        battery_response2 = client.post("/batteries/", json=battery_data2)
        batteries.append(battery_response2.json()["id"])
        
        # Update
        update_data = {"capacity": 150, "status": "maintenance"}
        response = client.put(f"/batteries/{batteries[0]}", json=update_data)
        assert response.status_code == 200
    
    def test_update_battery(self, client, equipment_id):
        """Обновление батареи"""
        # Create
        battery_data = {
            "equipment_id": equipment_id,
            "serial_number": "BAT-005",
            "capacity": 100,
            "voltage_nominal": 12.0,
            "install_date": str(date.today()),
            "status": "active"
        }
        create_response = client.post("/batteries/", json=battery_data)
        battery_id = create_response.json()["id"]
        
        # Update
        update_data = {"capacity": 150, "status": "maintenance"}
        response = client.put(f"/batteries/{battery_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["capacity"] == 150 or data["capacity"] == "150.00"
        assert data["status"] == "maintenance"
    
    def test_delete_battery(self, client, equipment_id):
        """Удаление батареи"""
        # Create
        battery_data = {
            "equipment_id": equipment_id,
            "serial_number": "BAT-006",
            "capacity": 100,
            "voltage_nominal": 12.0,
            "install_date": "2024-01-01",
            "status": "active"
        }
        create_response = client.post("/batteries/", json=battery_data)
        battery_id = create_response.json()["id"]
        
        # Delete
        response = client.delete(f"/batteries/{battery_id}")
        assert response.status_code == 200
        
        # Verify
        get_response = client.get(f"/batteries/{battery_id}")
        assert get_response.status_code == 404


class TestBatteryValidation:
    """Тесты валидации данных батарей"""
    
    @pytest.fixture
    def equipment_id(self, client):
        """Создает тестовое оборудование и возвращает ID"""
        equipment_data = {
            "name": "Test Equipment",
            "type": "UPS",
            "location": "Test Room",
            "status": "active"
        }
        response = client.post("/equipment/", json=equipment_data)
        return response.json()["id"]
    
    def test_invalid_voltage(self, client, equipment_id):
        """Недопустимое напряжение (0)"""
        battery_data = {
            "equipment_id": equipment_id,
            "serial_number": "BAT-V001",
            "capacity": 100,
            "voltage_nominal": 0,  # invalid
            "status": "active"
        }
        response = client.post("/batteries/", json=battery_data)
        assert response.status_code == 422
    
    def test_invalid_capacity(self, client, equipment_id):
        """Недопустимая емкость (0)"""
        battery_data = {
            "equipment_id": equipment_id,
            "serial_number": "BAT-C001",
            "capacity": 0,  # invalid
            "voltage_nominal": 12.0,
            "status": "active"
        }
        response = client.post("/batteries/", json=battery_data)
        assert response.status_code == 422
    
    def test_empty_serial(self, client, equipment_id):
        """Пустой серийный номер"""
        battery_data = {
            "equipment_id": equipment_id,
            "serial_number": "",  # invalid
            "capacity": 100,
            "voltage_nominal": 12.0,
            "status": "active"
        }
        response = client.post("/batteries/", json=battery_data)
        assert response.status_code == 422
