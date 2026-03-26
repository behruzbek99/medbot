"""
MiniMed AI Service for Doctor Rayhona - Groq API
"""
import re
from typing import Optional, Dict, List, Any
from groq import AsyncGroq
from loguru import logger

from minimed_prompts import DOCTOR_RAYHONA_SYSTEM_PROMPT, DIAGNOSIS_PROMPT, CHAT_PROMPT, EMERGENCY_PROMPT


class AIService:
    """Service for interacting with Groq API."""
    
    def __init__(self, api_key: str, model: str = "llama-3.1-8b-instant", max_tokens: int = 1024, temperature: float = 0.7):
        self.client = AsyncGroq(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        logger.info(f"AIService initialized with model: {model}")
    
    async def get_diagnosis(self, child_age: str, symptoms: str, duration: Optional[str] = None, severity: Optional[str] = None) -> Dict[str, Any]:
        try:
            prompt = DIAGNOSIS_PROMPT.format(child_age=child_age, symptoms=symptoms, duration=duration or "Noma'lum", severity=severity or "Noma'lum")
            logger.info(f"Sending diagnosis request: age={child_age}, symptoms={symptoms[:50]}...")
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": DOCTOR_RAYHONA_SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                timeout=30,
            )
            
            full_response = response.choices[0].message.content
            parsed = self._parse_diagnosis_response(full_response)
            parsed["full_response"] = full_response
            return parsed
            
        except Exception as e:
            logger.error(f"Diagnosis error: {e}")
            return self._get_fallback_diagnosis()
    
    async def chat(self, message: str, conversation_history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        try:
            history_str = ""
            if conversation_history:
                for msg in conversation_history[-5:]:
                    role = "Foydalanuvchi" if msg["role"] == "user" else "Doktor"
                    history_str += f"{role}: {msg['content']}\n"
            
            prompt = CHAT_PROMPT.format(message=message, conversation_history=history_str or "Yo'q")
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": DOCTOR_RAYHONA_SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                timeout=30,
            )
            
            ai_response = response.choices[0].message.content
            return {"response": ai_response, "risk_level": self._detect_risk_level(ai_response)}
            
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return {"response": "Kechirasiz, texnik muammo yuz berdi.", "risk_level": None}
    
    async def get_emergency_response(self, message: str) -> Dict[str, Any]:
        try:
            prompt = EMERGENCY_PROMPT.format(message=message)
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": DOCTOR_RAYHONA_SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=0.5,
                timeout=30,
            )
            return {"response": response.choices[0].message.content, "risk_level": "HIGH"}
        except Exception as e:
            logger.error(f"Emergency error: {e}")
            return self._get_fallback_emergency()
    
    def _parse_diagnosis_response(self, response: str) -> Dict[str, str]:
        diagnosis, risk_level = "Noma'lum holat", "MEDIUM"
        recommendation = "Batafsil maslahat uchun shifokorga murojaat qiling."
        when_to_see_doctor = "Agar alomatlar kuchaysa yoki 2-3 kun davom etsa."
        
        risk_match = re.search(r'Xavf darajasi:\s*(LOW|MEDIUM|HIGH)', response, re.IGNORECASE)
        if risk_match:
            risk_level = risk_match.group(1).upper()
        
        for pattern in [r'Taxminiy holat:\s*(.+?)(?:\n|$)', r'📋.*?:\s*(.+?)(?:\n\n|\n⚠️)']:
            match = re.search(pattern, response, re.IGNORECASE | re.DOTALL)
            if match:
                diagnosis = match.group(1).strip()
                break
        
        for pattern in [r'Nima qilish kerak:\s*(.+?)(?:\n\n|\n🏥)', r'💡.*?:\s*(.+?)(?:\n\n|\n🏥)']:
            match = re.search(pattern, response, re.IGNORECASE | re.DOTALL)
            if match:
                recommendation = match.group(1).strip()
                break
        
        for pattern in [r'Qachon shifokorga:\s*(.+?)(?:\n\n|\n⚕️)', r'🏥.*?:\s*(.+?)(?:\n\n|\n⚕️)']:
            match = re.search(pattern, response, re.IGNORECASE | re.DOTALL)
            if match:
                when_to_see_doctor = match.group(1).strip()
                break
        
        return {"diagnosis": diagnosis, "risk_level": risk_level, "recommendation": recommendation, "when_to_see_doctor": when_to_see_doctor, "disclaimer": "Bu faqat umumiy maslahat. Shifokorga murojaat qiling."}
    
    def _detect_risk_level(self, response: str) -> Optional[str]:
        if "HIGH" in response.upper(): return "HIGH"
        elif "MEDIUM" in response.upper(): return "MEDIUM"
        elif "LOW" in response.upper(): return "LOW"
        return None
    
    def _get_fallback_diagnosis(self) -> Dict[str, str]:
        return {"diagnosis": "Noma'lum holat", "risk_level": "MEDIUM", "recommendation": "Shifokorga murojaat qiling.", "when_to_see_doctor": "Alomatlar kuchaysa darhol shifokorga.", "disclaimer": "Bu faqat umumiy maslahat. Shifokorga murojaat qiling.", "full_response": "Hozircha javob berolmayapman."}
    
    def _get_fallback_emergency(self) -> Dict[str, Any]:
        return {"response": "🚨 SHOSHILINCH HOLAT\n\n⚠️ Xavf darajasi: HIGH\n\n📞 Darhol 103 ga qo'ng'iroq qiling!", "risk_level": "HIGH"}


ai_service: Optional[AIService] = None


def init_ai_service(api_key: str, model: str = "llama-3.1-8b-instant", max_tokens: int = 1024, temperature: float = 0.7) -> AIService:
    global ai_service
    ai_service = AIService(api_key, model, max_tokens, temperature)
    return ai_service


def get_ai_service() -> AIService:
    if ai_service is None:
        raise RuntimeError("AI service not initialized!")
    return ai_service
