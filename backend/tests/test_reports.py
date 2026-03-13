"""Тесты API отчетов (Reports)"""

import pytest


class TestReportsAPI:
    """Тесты аналитических отчетов"""
    
    @pytest.fixture
    def setup_data(self, client):
        """Создает полный набор тестовых данных"""
        # Equipment
        equipment_data = {
            "name": "Server Rack A",
            "type": "Server",
            "location": "DC1",
            "status": "active"
        }
        equipment_response = client.post("/equipment/", json=equipment_data)
        equipment_id = equipment_response.json()["id"]
        
        # Batteries
        batteries = []
        for i, (serial, cap, volt) in enumerate([
            ("BAT-R001", 100, 12.0),
            ("BAT-R002", 150, 24.0),
        ]):
            battery_data = {
                "equipment_id": equipment_id,
                "serial_number": serial,
                "capacity": cap,
                "voltage_nominal": volt,
                "status": "active",
                "install_date": "2024-01-01"
            }
            response = client.post("/batteries/", json=battery_data)
            batteries.append(response.json()["id"])
        
        # Measurements
        for i, battery_id in enumerate(batteries):
            for j in range(3):
                measurement_data = {
                    "battery_id": battery_id,
                    "voltage": 12.0 + j * 0.5,
                    "current": 5.0 + j,
                    "charge_level": 80.0 - j * 10,
                    "temperature": 25.0 + j * 5
                }
                client.post("/measurements/", json=measurement_data)
        
        return {"equipment_id": equipment_id, "battery_ids": batteries}
    
    def test_charge_levels_report(self, client, setup_data):
        """Отчет по уровням заряда"""
        response = client.get("/reports/charge-levels")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should contain equipment data
        assert len(data) >= 1
        if len(data) > 0:
            assert "equipment_name" in data[0]
            assert "avg_charge_level" in data[0]
            assert "battery_count" in data[0]
    
    def test_temperature_alerts_report(self, client, setup_data):
        """Отчет по критическим температурам"""
        # Add high temperature measurement
        battery_id = setup_data["battery_ids"][0]
        measurement_data = {
            "battery_id": battery_id,
            "voltage": 12.0,
            "current": 5.0,
            "charge_level": 80.0,
            "temperature": 65.0  # Critical
        }
        client.post("/measurements/", json=measurement_data)
        
        response = client.get("/reports/temperature-alerts")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should contain the high temp record
        high_temps = [d for d in data if float(d["temperature"]) >= 60]
        assert len(high_temps) >= 1
    
    def test_voltage_deviation_report(self, client, setup_data):
        """Отчет по отклонению напряжения"""
        response = client.get("/reports/voltage-deviation")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "serial_number" in data[0]
            assert "voltage_nominal" in data[0]
            assert "avg_voltage" in data[0]
            assert "deviation_percent" in data[0]
    
    def test_incident_stats_report(self, client, setup_data):
        """Отчет по статистике инцидентов"""
        # Create some incidents
        battery_id = setup_data["battery_ids"][0]
        for incident_type in ["warning", "overheat"]:
            incident_data = {
                "battery_id": battery_id,
                "incident_type": incident_type,
                "description": f"Test {incident_type}",
                "severity": "medium"
            }
            client.post("/incidents/", json=incident_data)
        
        response = client.get("/reports/incident-stats")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "incident_type" in data[0]
            assert "incident_count" in data[0]
    
    def test_equipment_incidents_report(self, client, setup_data):
        """Отчет по инцидентам оборудования"""
        # Create incidents
        battery_id = setup_data["battery_ids"][0]
        incident_data = {
            "battery_id": battery_id,
            "incident_type": "warning",
            "description": "Equipment issue",
            "severity": "high"
        }
        client.post("/incidents/", json=incident_data)
        
        response = client.get("/reports/equipment-incidents")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_battery_discharge_report(self, client, setup_data):
        """Отчет по разряду батареи"""
        battery_id = setup_data["battery_ids"][0]
        
        response = client.get(f"/reports/battery-discharge/{battery_id}?days=7")
        assert response.status_code == 200
        data = response.json()
        assert "battery_id" in data
        assert "serial_number" in data
        assert "data" in data
    
    def test_temperature_chart_report(self, client, setup_data):
        """Температурный график"""
        battery_id = setup_data["battery_ids"][0]
        
        # Add temperature measurements
        for temp in [20.0, 25.0, 30.0, 22.0]:
            measurement_data = {
                "battery_id": battery_id,
                "voltage": 12.0,
                "current": 5.0,
                "charge_level": 80.0,
                "temperature": temp
            }
            client.post("/measurements/", json=measurement_data)
        
        response = client.get(f"/reports/temperature-chart/{battery_id}?days=7")
        assert response.status_code == 200
        data = response.json()
        assert "battery_id" in data
        assert "data" in data
    
    def test_current_stats_report(self, client, setup_data):
        """Отчет по статистике тока"""
        response = client.get("/reports/current-stats")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_equipment_measurements_report(self, client, setup_data):
        """Отчет по измерениям оборудования"""
        response = client.get("/reports/equipment-measurements")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestReportsEdgeCases:
    """Тесты граничных случаев отчетов"""
    
    def test_reports_with_no_data(self, client):
        """Отчеты при отсутствии данных"""
        # All reports should handle empty database gracefully
        endpoints = [
            "/reports/charge-levels",
            "/reports/temperature-alerts",
            "/reports/voltage-deviation",
            "/reports/incident-stats",
            "/reports/equipment-incidents",
            "/reports/current-stats",
            "/reports/equipment-measurements"
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200, f"Failed: {endpoint}"
            data = response.json()
            assert isinstance(data, list)
    
    def test_battery_discharge_nonexistent_battery(self, client):
        """Отчет разряда для несуществующей батареи"""
        response = client.get("/reports/battery-discharge/99999?days=7")
        assert response.status_code == 404
    
    def test_temperature_chart_nonexistent_battery(self, client):
        """Температурный график для несуществующей батареи"""
        response = client.get("/reports/temperature-chart/99999?days=7")
        assert response.status_code == 404
