import os
import json
import google.generativeai as genai
from typing import Dict, List, Any
from datetime import datetime

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


class GeminiService:
    """Service for AI analysis using Google Gemini API"""
    
    def __init__(self):
        self.model = None
        if GEMINI_API_KEY:
            try:
                self.model = genai.GenerativeModel('gemini-2.5-flash-lite')
            except Exception as e:
                print(f"Error initializing Gemini model: {e}")
    
    def is_available(self) -> bool:
        """Check if Gemini API is configured and available"""
        return self.model is not None and GEMINI_API_KEY != ""
    
    def analyze_battery_data(self, battery_stats: Dict, problem_batteries: List[Dict], 
                              trends: List[Dict], incidents_summary: Dict) -> Dict[str, Any]:
        """
        Analyze battery monitoring data using Gemini AI
        
        Returns AI-generated analysis with health score, recommendations, and insights
        """
        if not self.is_available():
            return self._fallback_analysis(battery_stats, problem_batteries, trends, incidents_summary)
        
        # Prepare data for AI analysis
        data_summary = {
            "total_batteries": battery_stats.get("total_batteries", 0),
            "total_equipment": battery_stats.get("total_equipment", 0),
            "average_charge_level": battery_stats.get("avg_charge", 0),
            "average_temperature": battery_stats.get("avg_temp", 0),
            "critical_temperature_count": battery_stats.get("critical_temp_count", 0),
            "low_charge_count": battery_stats.get("low_charge_count", 0),
            "critical_incidents_7d": battery_stats.get("critical_incidents_7d", 0),
            "problem_batteries_count": len(problem_batteries),
            "problem_batteries_details": problem_batteries[:5],  # Top 5 for context
            "trends_days": len(trends),
            "latest_trend": trends[-1] if trends else None
        }
        
        # Create prompt for Gemini
        prompt = f"""You are an expert battery monitoring and maintenance AI assistant. 
Analyze the following battery monitoring data and provide a comprehensive analysis in Ukrainian language.

DATA SUMMARY:
{json.dumps(data_summary, indent=2, ensure_ascii=False)}

Provide a JSON response with the following structure:
{{
    "health_score": <number 0-100>,
    "health_score_reasoning": "<brief explanation of the score>",
    "recommendations": [
        "<recommendation 1>",
        "<recommendation 2>",
        ...
    ],
    "critical_issues": [
        "<critical issue 1>",
        ...
    ],
    "maintenance_priority": "<high/medium/low>",
    "predicted_issues": [
        "<potential future issue 1>",
        ...
    ],
    "suggested_actions": [
        "<specific action 1>",
        "<specific action 2>",
        ...
    ]
}}

Guidelines:
- Health score: 90-100 = excellent, 70-89 = good, 50-69 = fair, 30-49 = poor, 0-29 = critical
- Temperature > 60°C is critical, > 50°C is concerning
- Charge level < 20% is critical, < 30% is concerning
- Provide 3-5 specific, actionable recommendations
- Critical issues should highlight immediate problems
- Suggested actions should be specific maintenance tasks
- All text should be in Ukrainian language"""

        try:
            response = self.model.generate_content(prompt)
            ai_response_text = response.text
            
            # Extract JSON from response
            try:
                # Try to find JSON block in response
                json_start = ai_response_text.find('{')
                json_end = ai_response_text.rfind('}')
                if json_start >= 0 and json_end > json_start:
                    json_str = ai_response_text[json_start:json_end+1]
                    ai_result = json.loads(json_str)
                else:
                    ai_result = json.loads(ai_response_text)
                
                return {
                    "stats": {
                        "total_batteries": data_summary["total_batteries"],
                        "total_equipment": data_summary["total_equipment"],
                        "avg_charge": data_summary["average_charge_level"],
                        "avg_temp": data_summary["average_temperature"],
                        "critical_temp_count": data_summary["critical_temperature_count"],
                        "low_charge_count": data_summary["low_charge_count"],
                        "critical_incidents_7d": data_summary["critical_incidents_7d"],
                        "health_score": ai_result.get("health_score", 50),
                        "health_score_reasoning": ai_result.get("health_score_reasoning", "")
                    },
                    "recommendations": ai_result.get("recommendations", []),
                    "critical_issues": ai_result.get("critical_issues", []),
                    "maintenance_priority": ai_result.get("maintenance_priority", "medium"),
                    "predicted_issues": ai_result.get("predicted_issues", []),
                    "suggested_actions": ai_result.get("suggested_actions", []),
                    "ai_analysis": True,
                    "analysis_timestamp": datetime.utcnow().isoformat()
                }
                
            except json.JSONDecodeError as e:
                print(f"Error parsing Gemini response: {e}")
                return self._fallback_analysis(battery_stats, problem_batteries, trends, incidents_summary)
                
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            return self._fallback_analysis(battery_stats, problem_batteries, trends, incidents_summary)
    
    def _fallback_analysis(self, battery_stats: Dict, problem_batteries: List[Dict],
                          trends: List[Dict], incidents_summary: Dict) -> Dict[str, Any]:
        """Fallback analysis when Gemini API is not available"""
        stats = {
            "total_batteries": battery_stats.get("total_batteries", 0),
            "total_equipment": battery_stats.get("total_equipment", 0),
            "avg_charge": battery_stats.get("avg_charge", 0),
            "avg_temp": battery_stats.get("avg_temp", 0),
            "critical_temp_count": battery_stats.get("critical_temp_count", 0),
            "low_charge_count": battery_stats.get("low_charge_count", 0),
            "critical_incidents_7d": battery_stats.get("critical_incidents_7d", 0),
            "health_score": 0
        }
        
        # Calculate local health score
        if stats["total_batteries"] > 0:
            health_factors = [
                stats["avg_charge"] * 0.4,
                max(0, 100 - stats["avg_temp"]) * 0.3,
                max(0, 100 - (stats["critical_temp_count"] + stats["low_charge_count"]) * 5) * 0.2,
                max(0, 100 - stats["critical_incidents_7d"] * 10) * 0.1
            ]
            stats["health_score"] = round(sum(health_factors), 1)
        
        # Generate fallback recommendations
        recommendations = []
        critical_issues = []
        
        if stats["critical_temp_count"] > 0:
            critical_issues.append(f"{stats['critical_temp_count']} батарей мають критичну температуру (>60°C)")
            recommendations.append(f"Увага! {stats['critical_temp_count']} батарей мають критичну температуру. Рекомендується негайне обслуговування.")
        
        if stats["low_charge_count"] > 0:
            critical_issues.append(f"{stats['low_charge_count']} батарей мають критично низький заряд (<20%)")
            recommendations.append(f"{stats['low_charge_count']} батарей мають критично низький заряд. Перевірте зарядні пристрої.")
        
        if stats["avg_charge"] < 50:
            recommendations.append("Середній рівень заряду нижче 50%. Рекомендується планова зарядка обладнання.")
        
        if stats["avg_temp"] > 45:
            recommendations.append("Середня температура батарей вище норми. Перевірте системи охолодження.")
        
        if stats["critical_incidents_7d"] > 3:
            recommendations.append(f"Висока кількість критичних інцидентів за тиждень. Потрібен детальний аудит.")
        
        if not recommendations:
            recommendations.append("Система працює в нормальному режимі. Продовжуйте регулярний моніторинг.")
        
        return {
            "stats": stats,
            "recommendations": recommendations,
            "critical_issues": critical_issues,
            "maintenance_priority": "high" if critical_issues else ("medium" if stats["health_score"] < 70 else "low"),
            "predicted_issues": [],
            "suggested_actions": [],
            "ai_analysis": False,
            "analysis_timestamp": datetime.utcnow().isoformat()
        }


# Singleton instance
gemini_service = GeminiService()
