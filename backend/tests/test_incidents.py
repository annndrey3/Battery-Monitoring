"""Тесты API инцидентов (Incidents)"""

import pytest


class TestIncidentsAPI:
    """Тесты CRUD операций для инцидентов"""
    
    @pytest.fixture
    def setup_data(self, client):
        """Создает тестовые данные"""
        # Equipment
        equipment_data = {
            "name": "Test Equipment",
            "type": "UPS",
            "location": "Test Room",
            "status": "active"
        }
        equipment_response = client.post("/equipment/", json=equipment_data)
        equipment_id = equipment_response.json()["id"]
        
        # Battery
        battery_data = {
            "equipment_id": equipment_id,
            "serial_number": "BAT-I001",
            "capacity": 100,
            "voltage_nominal": 12.0,
            "status": "active",
            "install_date": "2024-01-01"
        }
        battery_response = client.post("/batteries/", json=battery_data)
        battery_id = battery_response.json()["id"]
        
        return {"equipment_id": equipment_id, "battery_id": battery_id}
    
    def test_create_incident(self, client, setup_data):
        """Создание инцидента"""
        battery_id = setup_data["battery_id"]
        
        incident_data = {
            "battery_id": battery_id,
            "incident_type": "warning",
            "description": "Test incident",
            "severity": "medium"
        }
        response = client.post("/incidents/", json=incident_data)
        assert response.status_code == 200
        data = response.json()
        assert data["incident_type"] == "warning"
        assert data["severity"] == "medium"
        assert data["is_resolved"] == False
    
    def test_get_incidents_list(self, client, setup_data):
        """Получение списка инцидентов"""
        battery_id = setup_data["battery_id"]
        
        # Create incident
        incident_data = {
            "battery_id": battery_id,
            "incident_type": "warning",
            "description": "Test incident",
            "severity": "low"
        }
        client.post("/incidents/", json=incident_data)
        
        response = client.get("/incidents/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
    
    def test_get_incidents_by_type(self, client, setup_data):
        """Фильтрация инцидентов по типу"""
        battery_id = setup_data["battery_id"]
        
        # Create incidents of different types
        for incident_type in ["warning", "critical_failure"]:
            incident_data = {
                "battery_id": battery_id,
                "incident_type": incident_type,
                "description": f"Test {incident_type}",
                "severity": "high"
            }
            client.post("/incidents/", json=incident_data)
        
        response = client.get("/incidents/?incident_type=warning")
        assert response.status_code == 200
        data = response.json()
        assert all(i["incident_type"] == "warning" for i in data)
    
    def test_get_incidents_by_severity(self, client, setup_data):
        """Фильтрация инцидентов по серьезности"""
        battery_id = setup_data["battery_id"]
        
        # Create incidents
        incident_data = {
            "battery_id": battery_id,
            "incident_type": "warning",
            "description": "Critical issue",
            "severity": "critical"
        }
        client.post("/incidents/", json=incident_data)
        
        response = client.get("/incidents/?severity=critical")
        assert response.status_code == 200
        data = response.json()
        assert all(i["severity"] == "critical" for i in data)
    
    def test_get_active_incidents(self, client, setup_data):
        """Получение только активных инцидентов"""
        battery_id = setup_data["battery_id"]
        
        # Create active incident
        incident_data = {
            "battery_id": battery_id,
            "incident_type": "warning",
            "description": "Active incident",
            "severity": "medium"
        }
        client.post("/incidents/", json=incident_data)
        
        response = client.get("/incidents/?is_resolved=false")
        assert response.status_code == 200
        data = response.json()
        assert all(i["is_resolved"] == False for i in data)
    
    def test_resolve_incident(self, client, setup_data):
        """Решение инцидента"""
        battery_id = setup_data["battery_id"]
        
        # Create
        incident_data = {
            "battery_id": battery_id,
            "incident_type": "warning",
            "description": "To be resolved",
            "severity": "medium"
        }
        create_response = client.post("/incidents/", json=incident_data)
        incident_id = create_response.json()["id"]
        
        # Resolve
        update_data = {"is_resolved": True, "resolved_by": 1}
        response = client.put(f"/incidents/{incident_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["is_resolved"] == True
    
    def test_update_incident_description(self, client, setup_data):
        """Обновление описания инцидента"""
        battery_id = setup_data["battery_id"]
        
        # Create
        incident_data = {
            "battery_id": battery_id,
            "incident_type": "warning",
            "description": "Original description",
            "severity": "low"
        }
        create_response = client.post("/incidents/", json=incident_data)
        incident_id = create_response.json()["id"]
        
        # Update
        update_data = {"description": "Updated description"}
        response = client.put(f"/incidents/{incident_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated description"
    
    def test_delete_incident(self, client, setup_data):
        """Удаление инцидента"""
        battery_id = setup_data["battery_id"]
        
        # Create
        incident_data = {
            "battery_id": battery_id,
            "incident_type": "warning",
            "description": "To delete",
            "severity": "low"
        }
        create_response = client.post("/incidents/", json=incident_data)
        incident_id = create_response.json()["id"]
        
        # Delete
        response = client.delete(f"/incidents/{incident_id}")
        assert response.status_code == 200
        
        # Verify
        get_response = client.get(f"/incidents/{incident_id}")
        assert get_response.status_code == 404


class TestIncidentValidation:
    """Тесты валидации данных инцидентов"""
    
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
            "serial_number": "BAT-V002",
            "capacity": 100,
            "voltage_nominal": 12.0,
            "status": "active",
            "install_date": "2024-01-01"
        }
        battery_response = client.post("/batteries/", json=battery_data)
        return battery_response.json()["id"]
    
    def test_invalid_severity(self, client, battery_id):
        """Недопустимая серьезность"""
        incident_data = {
            "battery_id": battery_id,
            "incident_type": "warning",
            "description": "Test",
            "severity": "invalid"  # should be low/medium/high/critical
        }
        response = client.post("/incidents/", json=incident_data)
        assert response.status_code == 422
    
    def test_invalid_incident_type(self, client, battery_id):
        """Недопустимый тип инцидента"""
        incident_data = {
            "battery_id": battery_id,
            "incident_type": "unknown_type",
            "description": "Test",
            "severity": "medium"
        }
        response = client.post("/incidents/", json=incident_data)
        assert response.status_code == 422
    
    def test_empty_description(self, client, battery_id):
        """Пустое описание"""
        incident_data = {
            "battery_id": battery_id,
            "incident_type": "warning",
            "description": "",  # empty
            "severity": "medium"
        }
        response = client.post("/incidents/", json=incident_data)
        assert response.status_code == 422
