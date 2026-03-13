from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, text, extract
from typing import List, Optional
from datetime import datetime, timedelta
from decimal import Decimal
from database.database import get_db, is_sqlite
from models import models, schemas

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/charge-levels", response_model=List[schemas.ChargeReport])
def get_charge_levels_report(db: Session = Depends(get_db)):
    """Отчет о среднем уровне заряда батарей по оборудованию"""
    time_threshold = datetime.utcnow() - timedelta(hours=24)
    
    if is_sqlite():
        query = text("""
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
            WHERE m.timestamp >= :time_threshold
            GROUP BY e.id, e.name, e.location
            ORDER BY avg_charge_level ASC
        """)
        result = db.execute(query, {"time_threshold": time_threshold})
    else:
        query = text("""
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
            ORDER BY avg_charge_level ASC
        """)
        result = db.execute(query)
    
    reports = []
    for row in result:
        reports.append(schemas.ChargeReport(
            equipment_name=row.equipment_name,
            location=row.location,
            battery_count=row.battery_count or 0,
            avg_charge_level=row.avg_charge_level or Decimal(0),
            min_charge_level=row.min_charge_level or Decimal(0),
            max_charge_level=row.max_charge_level or Decimal(0)
        ))
    
    return reports

@router.get("/temperature-alerts", response_model=List[schemas.TemperatureAlert])
def get_temperature_alerts(db: Session = Depends(get_db)):
    """Поиск батарей с критической температурой"""
    time_threshold = datetime.utcnow() - timedelta(hours=1)
    
    if is_sqlite():
        query = text("""
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
            AND m.timestamp >= :time_threshold
            ORDER BY m.temperature DESC
        """)
        result = db.execute(query, {"time_threshold": time_threshold})
    else:
        query = text("""
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
            ORDER BY m.temperature DESC
        """)
        result = db.execute(query)
    
    alerts = []
    for row in result:
        alerts.append(schemas.TemperatureAlert(
            equipment_name=row.equipment_name,
            serial_number=row.serial_number,
            capacity=row.capacity,
            temperature=row.temperature,
            charge_level=row.charge_level,
            timestamp=row.timestamp,
            alert_level=row.alert_level
        ))
    
    return alerts

@router.get("/incident-stats", response_model=List[schemas.IncidentStats])
def get_incident_stats(months: int = 6, db: Session = Depends(get_db)):
    """Статистика инцидентов по типам и месяцам"""
    from_date = datetime.utcnow() - timedelta(days=30*months)
    
    if is_sqlite():
        query = text("""
            SELECT 
                incident_type,
                strftime('%Y-%m', created_at) AS month,
                COUNT(*) AS incident_count,
                COUNT(CASE WHEN is_resolved THEN 1 END) AS resolved_count,
                COUNT(CASE WHEN severity = 'critical' THEN 1 END) AS critical_count,
                ROUND(AVG(CASE 
                    WHEN resolved_at IS NOT NULL 
                    THEN (julianday(resolved_at) - julianday(created_at)) * 24
                    ELSE (julianday('now') - julianday(created_at)) * 24
                END), 2) AS avg_resolution_hours
            FROM incidents
            WHERE created_at >= :from_date
            GROUP BY incident_type, strftime('%Y-%m', created_at)
            ORDER BY month DESC, incident_count DESC
        """)
        result = db.execute(query, {"from_date": from_date})
    else:
        query = text("""
            SELECT 
                incident_type,
                TO_CHAR(created_at, 'YYYY-MM') AS month,
                COUNT(*) AS incident_count,
                COUNT(CASE WHEN is_resolved THEN 1 END) AS resolved_count,
                COUNT(CASE WHEN severity = 'critical' THEN 1 END) AS critical_count,
                ROUND(AVG(CASE 
                    WHEN resolved_at IS NOT NULL 
                    THEN EXTRACT(EPOCH FROM (resolved_at - created_at))/3600
                    ELSE EXTRACT(EPOCH FROM (NOW() - created_at))/3600
                END), 2) AS avg_resolution_hours
            FROM incidents
            WHERE created_at >= NOW() - (:months || ' months')::interval
            GROUP BY incident_type, TO_CHAR(created_at, 'YYYY-MM')
            ORDER BY month DESC, incident_count DESC
        """)
        result = db.execute(query, {"months": months})
    
    stats = []
    for row in result:
        stats.append(schemas.IncidentStats(
            incident_type=row.incident_type,
            month=row.month,
            incident_count=row.incident_count,
            resolved_count=row.resolved_count,
            critical_count=row.critical_count,
            avg_resolution_hours=float(row.avg_resolution_hours) if row.avg_resolution_hours else None
        ))
    
    return stats

@router.get("/voltage-deviation", response_model=List[schemas.VoltageDeviation])
def get_voltage_deviation_report(db: Session = Depends(get_db)):
    """Отчет об отклонении напряжения от номинала"""
    time_threshold = datetime.utcnow() - timedelta(hours=24)
    
    if is_sqlite():
        query = text("""
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
            WHERE m.timestamp >= :time_threshold
            GROUP BY b.id, b.serial_number, e.name, b.voltage_nominal
            ORDER BY deviation_percent DESC
        """)
        result = db.execute(query, {"time_threshold": time_threshold})
    else:
        query = text("""
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
            ORDER BY deviation_percent DESC
        """)
        result = db.execute(query)
    
    deviations = []
    for row in result:
        deviations.append(schemas.VoltageDeviation(
            id=row.id,
            serial_number=row.serial_number,
            equipment_name=row.equipment_name,
            voltage_nominal=row.voltage_nominal,
            avg_voltage=row.avg_voltage,
            voltage_deviation=row.voltage_deviation,
            deviation_percent=row.deviation_percent,
            status=row.status
        ))
    
    return deviations

@router.get("/equipment-incidents", response_model=List[schemas.EquipmentIncidentSummary])
def get_equipment_incidents_summary(days: int = 30, db: Session = Depends(get_db)):
    """Оборудование с наибольшим количеством инцидентов"""
    time_threshold = datetime.utcnow() - timedelta(days=days)
    
    if is_sqlite():
        query = text("""
            SELECT 
                e.id,
                e.name AS equipment_name,
                e.type AS equipment_type,
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
            WHERE i.created_at >= :time_threshold
            GROUP BY e.id, e.name, e.type, e.location
            ORDER BY total_incidents DESC
            LIMIT 10
        """)
        result = db.execute(query, {"time_threshold": time_threshold})
    else:
        query = text("""
            SELECT 
                e.id,
                e.name AS equipment_name,
                e.type AS equipment_type,
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
            WHERE i.created_at >= NOW() - (:days || ' days')::interval
            GROUP BY e.id, e.name, e.type, e.location
            ORDER BY total_incidents DESC
            LIMIT 10
        """)
        result = db.execute(query, {"days": days})
    
    summaries = []
    for row in result:
        summaries.append(schemas.EquipmentIncidentSummary(
            id=row.id,
            equipment_name=row.equipment_name,
            equipment_type=row.equipment_type,
            location=row.location,
            battery_count=row.battery_count or 0,
            total_incidents=row.total_incidents or 0,
            critical_incidents=row.critical_incidents or 0,
            overheat_count=row.overheat_count or 0,
            low_charge_count=row.low_charge_count or 0,
            last_incident_date=row.last_incident_date
        ))
    
    return summaries

@router.get("/current-stats", response_model=List[schemas.CurrentStats])
def get_current_stats_report(db: Session = Depends(get_db)):
    """Средний ток с группировкой по диапазонам"""
    time_threshold = datetime.utcnow() - timedelta(hours=24)
    
    if is_sqlite():
        query = text("""
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
            WHERE m.timestamp >= :time_threshold
            GROUP BY e.name, b.serial_number
            ORDER BY avg_current DESC
        """)
        result = db.execute(query, {"time_threshold": time_threshold})
    else:
        query = text("""
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
            ORDER BY avg_current DESC
        """)
        result = db.execute(query)
    
    stats = []
    for row in result:
        stats.append(schemas.CurrentStats(
            equipment_name=row.equipment_name,
            serial_number=row.serial_number,
            current_range=row.current_range,
            avg_current=row.avg_current,
            max_current=row.max_current,
            min_current=row.min_current,
            measurement_count=row.measurement_count
        ))
    
    return stats

@router.get("/equipment-measurements", response_model=List[schemas.EquipmentMeasurementStats])
def get_equipment_measurement_stats(days: int = 30, db: Session = Depends(get_db)):
    """Количество измерений по оборудованию с активностью операторов"""
    time_threshold = datetime.utcnow() - timedelta(days=days)
    
    if is_sqlite():
        query = text("""
            SELECT 
                e.id AS equipment_id,
                e.name AS equipment_name,
                e.location,
                COUNT(DISTINCT b.id) AS battery_count,
                COUNT(m.id) AS total_measurements,
                COUNT(DISTINCT strftime('%Y-%m-%d', m.timestamp)) AS days_with_measurements,
                ROUND(CAST(COUNT(m.id) AS REAL) / NULLIF(COUNT(DISTINCT b.id), 0), 1) AS avg_measurements_per_battery,
                COUNT(DISTINCT m.measured_by) AS operator_count,
                GROUP_CONCAT(DISTINCT COALESCE(u.full_name, 'Unknown'), ', ') AS operators,
                MAX(m.timestamp) AS last_measurement
            FROM equipment e
            LEFT JOIN batteries b ON e.id = b.equipment_id
            LEFT JOIN measurements m ON b.id = m.battery_id
            LEFT JOIN users u ON m.measured_by = u.id
            WHERE m.timestamp >= :time_threshold
            GROUP BY e.id, e.name, e.location
            ORDER BY total_measurements DESC
        """)
        result = db.execute(query, {"time_threshold": time_threshold})
    else:
        query = text("""
            SELECT 
                e.id AS equipment_id,
                e.name AS equipment_name,
                e.location,
                COUNT(DISTINCT b.id) AS battery_count,
                COUNT(m.id) AS total_measurements,
                COUNT(DISTINCT TO_CHAR(m.timestamp, 'YYYY-MM-DD')) AS days_with_measurements,
                ROUND((CAST(COUNT(m.id) AS REAL) / NULLIF(COUNT(DISTINCT b.id), 0))::numeric, 1) AS avg_measurements_per_battery,
                COUNT(DISTINCT m.measured_by) AS operator_count,
                STRING_AGG(DISTINCT COALESCE(u.full_name, 'Unknown'), ', ') AS operators,
                MAX(m.timestamp) AS last_measurement
            FROM equipment e
            LEFT JOIN batteries b ON e.id = b.equipment_id
            LEFT JOIN measurements m ON b.id = m.battery_id
            LEFT JOIN users u ON m.measured_by = u.id
            WHERE m.timestamp >= NOW() - (:days || ' days')::interval
            GROUP BY e.id, e.name, e.location
            ORDER BY total_measurements DESC
        """)
        result = db.execute(query, {"days": days})
    
    stats = []
    for row in result:
        stats.append(schemas.EquipmentMeasurementStats(
            equipment_id=row.equipment_id,
            equipment_name=row.equipment_name,
            location=row.location,
            battery_count=row.battery_count or 0,
            total_measurements=row.total_measurements or 0,
            days_with_measurements=row.days_with_measurements or 0,
            avg_measurements_per_battery=float(row.avg_measurements_per_battery) if row.avg_measurements_per_battery else None,
            operator_count=row.operator_count or 0,
            operators=row.operators,
            last_measurement=row.last_measurement
        ))
    
    return stats

@router.get("/battery-discharge/{battery_id}")
def get_battery_discharge_graph(battery_id: int, days: int = 7, db: Session = Depends(get_db)):
    """Данные для графика разряда батареи"""
    battery = db.query(models.Battery).filter(models.Battery.id == battery_id).first()
    if not battery:
        raise HTTPException(status_code=404, detail="Battery not found")
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    measurements = db.query(models.Measurement).filter(
        models.Measurement.battery_id == battery_id,
        models.Measurement.timestamp >= start_date
    ).order_by(models.Measurement.timestamp.asc()).all()
    
    data = []
    for m in measurements:
        data.append({
            "timestamp": m.timestamp.isoformat(),
            "charge_level": float(m.charge_level),
            "voltage": float(m.voltage)
        })
    
    return {
        "battery_id": battery_id,
        "serial_number": battery.serial_number,
        "days": days,
        "data": data
    }

@router.get("/temperature-chart/{battery_id}")
def get_temperature_chart_data(battery_id: int, days: int = 7, db: Session = Depends(get_db)):
    """Данные для температурного графика"""
    battery = db.query(models.Battery).filter(models.Battery.id == battery_id).first()
    if not battery:
        raise HTTPException(status_code=404, detail="Battery not found")
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    if is_sqlite():
        query = text("""
            SELECT 
                strftime('%Y-%m-%d %H:00:00', timestamp) AS hour,
                ROUND(AVG(temperature), 2) AS avg_temp,
                ROUND(MAX(temperature), 2) AS max_temp,
                ROUND(MIN(temperature), 2) AS min_temp
            FROM measurements
            WHERE battery_id = :battery_id
            AND timestamp >= :start_date
            GROUP BY strftime('%Y-%m-%d %H', timestamp)
            ORDER BY hour ASC
        """)
    else:
        query = text("""
            SELECT 
                TO_CHAR(timestamp, 'YYYY-MM-DD HH24:00:00') AS hour,
                ROUND(AVG(temperature), 2) AS avg_temp,
                ROUND(MAX(temperature), 2) AS max_temp,
                ROUND(MIN(temperature), 2) AS min_temp
            FROM measurements
            WHERE battery_id = :battery_id
            AND timestamp >= :start_date
            GROUP BY TO_CHAR(timestamp, 'YYYY-MM-DD HH24:00:00')
            ORDER BY hour ASC
        """)
    
    result = db.execute(query, {"battery_id": battery_id, "start_date": start_date})
    
    data = []
    for row in result:
        data.append({
            "hour": row.hour,
            "avg_temp": float(row.avg_temp) if row.avg_temp else None,
            "max_temp": float(row.max_temp) if row.max_temp else None,
            "min_temp": float(row.min_temp) if row.min_temp else None
        })
    
    return {
        "battery_id": battery_id,
        "serial_number": battery.serial_number,
        "days": days,
        "data": data
    }


@router.get("/ai-analysis")
def get_ai_analysis(db: Session = Depends(get_db)):
    """AI-аналіз стану батарей та обладнання через Google Gemini API"""
    from services.gemini_service import gemini_service
    
    time_threshold = datetime.utcnow() - timedelta(hours=24)
    week_threshold = datetime.utcnow() - timedelta(days=7)
    
    if is_sqlite():
        # Загальна статистика
        stats_query = text("""
            SELECT 
                COUNT(DISTINCT b.id) AS total_batteries,
                COUNT(DISTINCT e.id) AS total_equipment,
                ROUND(AVG(m.charge_level), 2) AS avg_charge,
                ROUND(AVG(m.temperature), 2) AS avg_temp,
                COUNT(CASE WHEN m.temperature > 60 THEN 1 END) AS critical_temp_count,
                COUNT(CASE WHEN m.charge_level < 20 THEN 1 END) AS low_charge_count,
                COUNT(CASE WHEN i.severity = 'critical' AND i.created_at >= :week_threshold THEN 1 END) AS critical_incidents_7d
            FROM batteries b
            JOIN equipment e ON b.equipment_id = e.id
            LEFT JOIN measurements m ON b.id = m.battery_id AND m.timestamp >= :time_threshold
            LEFT JOIN incidents i ON b.id = i.battery_id
        """)
        
        # Проблемні батареї
        problem_query = text("""
            SELECT 
                b.serial_number,
                e.name AS equipment_name,
                ROUND(AVG(m.charge_level), 2) AS avg_charge,
                ROUND(AVG(m.temperature), 2) AS avg_temp,
                COUNT(i.id) AS incident_count,
                CASE 
                    WHEN AVG(m.temperature) > 60 THEN 'Перегрів'
                    WHEN AVG(m.charge_level) < 20 THEN 'Низький заряд'
                    WHEN COUNT(i.id) > 2 THEN 'Часті інциденти'
                    ELSE 'Норма'
                END AS status
            FROM batteries b
            JOIN equipment e ON b.equipment_id = e.id
            JOIN measurements m ON b.id = m.battery_id
            LEFT JOIN incidents i ON b.id = i.battery_id AND i.created_at >= :week_threshold
            WHERE m.timestamp >= :time_threshold
            GROUP BY b.id, b.serial_number, e.name
            HAVING avg_charge < 30 OR avg_temp > 55 OR incident_count > 2
            ORDER BY incident_count DESC, avg_charge ASC
            LIMIT 10
        """)
        
        # Тренди за тиждень
        trends_query = text("""
            SELECT 
                strftime('%Y-%m-%d', timestamp) AS day,
                ROUND(AVG(charge_level), 2) AS avg_charge,
                ROUND(AVG(temperature), 2) AS avg_temp,
                COUNT(CASE WHEN temperature > 60 THEN 1 END) AS temp_alerts,
                COUNT(CASE WHEN charge_level < 20 THEN 1 END) AS charge_alerts
            FROM measurements
            WHERE timestamp >= :week_threshold
            GROUP BY strftime('%Y-%m-%d', timestamp)
            ORDER BY day ASC
        """)
        
        # Статистика інцидентів
        incidents_query = text("""
            SELECT 
                incident_type,
                COUNT(*) as count,
                COUNT(CASE WHEN is_resolved THEN 1 END) as resolved,
                COUNT(CASE WHEN severity = 'critical' THEN 1 END) as critical
            FROM incidents
            WHERE created_at >= :week_threshold
            GROUP BY incident_type
        """)
        
        stats_result = db.execute(stats_query, {"time_threshold": time_threshold, "week_threshold": week_threshold})
        problem_result = db.execute(problem_query, {"time_threshold": time_threshold, "week_threshold": week_threshold})
        trends_result = db.execute(trends_query, {"week_threshold": week_threshold})
        incidents_result = db.execute(incidents_query, {"week_threshold": week_threshold})
    else:
        # PostgreSQL версії запитів
        stats_query = text("""
            SELECT 
                COUNT(DISTINCT b.id) AS total_batteries,
                COUNT(DISTINCT e.id) AS total_equipment,
                ROUND(AVG(m.charge_level), 2) AS avg_charge,
                ROUND(AVG(m.temperature), 2) AS avg_temp,
                COUNT(CASE WHEN m.temperature > 60 THEN 1 END) AS critical_temp_count,
                COUNT(CASE WHEN m.charge_level < 20 THEN 1 END) AS low_charge_count,
                COUNT(CASE WHEN i.severity = 'critical' AND i.created_at >= NOW() - INTERVAL '7 days' THEN 1 END) AS critical_incidents_7d
            FROM batteries b
            JOIN equipment e ON b.equipment_id = e.id
            LEFT JOIN measurements m ON b.id = m.battery_id AND m.timestamp >= NOW() - INTERVAL '24 hours'
            LEFT JOIN incidents i ON b.id = i.battery_id
        """)
        
        problem_query = text("""
            SELECT 
                b.serial_number,
                e.name AS equipment_name,
                ROUND(AVG(m.charge_level), 2) AS avg_charge,
                ROUND(AVG(m.temperature), 2) AS avg_temp,
                COUNT(i.id) AS incident_count,
                CASE 
                    WHEN AVG(m.temperature) > 60 THEN 'Перегрів'
                    WHEN AVG(m.charge_level) < 20 THEN 'Низький заряд'
                    WHEN COUNT(i.id) > 2 THEN 'Часті інциденти'
                    ELSE 'Норма'
                END AS status
            FROM batteries b
            JOIN equipment e ON b.equipment_id = e.id
            JOIN measurements m ON b.id = m.battery_id
            LEFT JOIN incidents i ON b.id = i.battery_id AND i.created_at >= NOW() - INTERVAL '7 days'
            WHERE m.timestamp >= NOW() - INTERVAL '24 hours'
            GROUP BY b.id, b.serial_number, e.name
            HAVING AVG(m.charge_level) < 30 OR AVG(m.temperature) > 55 OR COUNT(i.id) > 2
            ORDER BY COUNT(i.id) DESC, AVG(m.charge_level) ASC
            LIMIT 10
        """)
        
        trends_query = text("""
            SELECT 
                TO_CHAR(timestamp, 'YYYY-MM-DD') AS day,
                ROUND(AVG(charge_level), 2) AS avg_charge,
                ROUND(AVG(temperature), 2) AS avg_temp,
                COUNT(CASE WHEN temperature > 60 THEN 1 END) AS temp_alerts,
                COUNT(CASE WHEN charge_level < 20 THEN 1 END) AS charge_alerts
            FROM measurements
            WHERE timestamp >= NOW() - INTERVAL '7 days'
            GROUP BY TO_CHAR(timestamp, 'YYYY-MM-DD')
            ORDER BY day ASC
        """)
        
        incidents_query = text("""
            SELECT 
                incident_type,
                COUNT(*) as count,
                COUNT(CASE WHEN is_resolved THEN 1 END) as resolved,
                COUNT(CASE WHEN severity = 'critical' THEN 1 END) as critical
            FROM incidents
            WHERE created_at >= NOW() - INTERVAL '7 days'
            GROUP BY incident_type
        """)
        
        stats_result = db.execute(stats_query)
        problem_result = db.execute(problem_query)
        trends_result = db.execute(trends_query)
        incidents_result = db.execute(incidents_query)
    
    # Формування базових даних
    stats_row = stats_result.fetchone()
    battery_stats = {
        "total_batteries": stats_row.total_batteries or 0,
        "total_equipment": stats_row.total_equipment or 0,
        "avg_charge": float(stats_row.avg_charge) if stats_row.avg_charge else 0,
        "avg_temp": float(stats_row.avg_temp) if stats_row.avg_temp else 0,
        "critical_temp_count": stats_row.critical_temp_count or 0,
        "low_charge_count": stats_row.low_charge_count or 0,
        "critical_incidents_7d": stats_row.critical_incidents_7d or 0
    }
    
    # Проблемні батареї
    problem_batteries = []
    for row in problem_result:
        problem_batteries.append({
            "serial_number": row.serial_number,
            "equipment_name": row.equipment_name,
            "avg_charge": float(row.avg_charge) if row.avg_charge else 0,
            "avg_temp": float(row.avg_temp) if row.avg_temp else 0,
            "incident_count": row.incident_count or 0,
            "status": row.status
        })
    
    # Тренди
    trends = []
    for row in trends_result:
        trends.append({
            "day": row.day,
            "avg_charge": float(row.avg_charge) if row.avg_charge else 0,
            "avg_temp": float(row.avg_temp) if row.avg_temp else 0,
            "temp_alerts": row.temp_alerts or 0,
            "charge_alerts": row.charge_alerts or 0
        })
    
    # Статистика інцидентів
    incidents_summary = {}
    for row in incidents_result:
        incidents_summary[row.incident_type] = {
            "count": row.count,
            "resolved": row.resolved,
            "critical": row.critical
        }
    
    # AI аналіз через Gemini
    ai_result = gemini_service.analyze_battery_data(
        battery_stats=battery_stats,
        problem_batteries=problem_batteries,
        trends=trends,
        incidents_summary=incidents_summary
    )
    
    # Додаємо проблемні батареї та тренди до відповіді
    ai_result["problem_batteries"] = problem_batteries
    ai_result["trends"] = trends
    
    return ai_result
