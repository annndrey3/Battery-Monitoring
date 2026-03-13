"""Тесты API оборудования (Equipment)"""

import pytest


class TestEquipmentAPI:
    """Тесты CRUD операций для оборудования"""
    
    def test_get_empty_equipment_list(self, client):
        """Получение пустого списка оборудования"""
        response = client.get("/equipment/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_create_equipment(self, client):
        """Создание нового оборудования"""
        equipment_data = {
            "name": "Test Server",
            "type": "Server",
            "location": "Room 101",
            "description": "Test equipment",
            "status": "active"
        }
        response = client.post("/equipment/", json=equipment_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == equipment_data["name"]
        assert data["type"] == equipment_data["type"]
        assert data["location"] == equipment_data["location"]
        assert data["status"] == "active"
        assert "id" in data
        assert "created_at" in data
    
    def test_create_equipment_validation_error(self, client):
        """Ошибка валидации при создании (пустое имя)"""
        equipment_data = {
            "name": "",  # invalid
            "type": "Server",
            "location": "Room 101"
        }
        response = client.post("/equipment/", json=equipment_data)
        assert response.status_code == 422
    
    def test_get_equipment_list_with_data(self, client):
        """Получение списка с данными"""
        # Create equipment
        equipment_data = {
            "name": "UPS System",
            "type": "UPS",
            "location": "Server Room",
            "status": "active"
        }
        client.post("/equipment/", json=equipment_data)
        
        # Get list
        response = client.get("/equipment/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "UPS System"
    
    def test_get_equipment_by_id(self, client):
        """Получение оборудования по ID"""
        # Create
        equipment_data = {
            "name": "Battery Rack",
            "type": "Rack",
            "location": "Basement",
            "status": "active"
        }
        create_response = client.post("/equipment/", json=equipment_data)
        created_id = create_response.json()["id"]
        
        # Get by ID
        response = client.get(f"/equipment/{created_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Battery Rack"
        assert data["id"] == created_id
    
    def test_get_nonexistent_equipment(self, client):
        """Получение несуществующего оборудования"""
        response = client.get("/equipment/99999")
        assert response.status_code == 404
    
    def test_update_equipment(self, client):
        """Обновление оборудования"""
        # Create
        equipment_data = {
            "name": "Old Name",
            "type": "Server",
            "location": "Room 1",
            "status": "active"
        }
        create_response = client.post("/equipment/", json=equipment_data)
        created_id = create_response.json()["id"]
        
        # Update
        update_data = {"name": "New Name", "location": "Room 2"}
        response = client.put(f"/equipment/{created_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Name"
        assert data["location"] == "Room 2"
        assert data["type"] == "Server"  # unchanged
    
    def test_update_nonexistent_equipment(self, client):
        """Обновление несуществующего оборудования"""
        update_data = {"name": "New Name"}
        response = client.put("/equipment/99999", json=update_data)
        assert response.status_code == 404
    
    def test_delete_equipment(self, client):
        """Удаление оборудования"""
        # Create
        equipment_data = {
            "name": "To Delete",
            "type": "Temp",
            "location": "Nowhere",
            "status": "active"
        }
        create_response = client.post("/equipment/", json=equipment_data)
        created_id = create_response.json()["id"]
        
        # Delete
        response = client.delete(f"/equipment/{created_id}")
        assert response.status_code == 200
        
        # Verify deleted
        get_response = client.get(f"/equipment/{created_id}")
        assert get_response.status_code == 404
    
    def test_delete_nonexistent_equipment(self, client):
        """Удаление несуществующего оборудования"""
        response = client.delete("/equipment/99999")
        assert response.status_code == 404


class TestEquipmentValidation:
    """Тесты валидации данных оборудования"""
    
    @pytest.mark.parametrize("field,value", [
        ("name", ""),  # empty
        ("name", "a" * 101),  # too long
        ("type", ""),  # empty
        ("location", ""),  # empty
        ("status", "invalid_status"),  # wrong enum
    ])
    def test_field_validation(self, client, field, value):
        """Проверка валидации полей"""
        equipment_data = {
            "name": "Valid Name",
            "type": "Valid Type",
            "location": "Valid Location",
            "status": "active"
        }
        equipment_data[field] = value
        
        response = client.post("/equipment/", json=equipment_data)
        assert response.status_code == 422
