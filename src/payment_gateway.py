import hashlib
import hmac
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from decimal import Decimal
import aiohttp
from pydantic import BaseModel, ValidationError, validator

class D17PaymentConfig(BaseModel):
    merchant_id: str
    api_key: str
    secret_key: str
    api_url: str = "https://d17.tn/api/v3"
    timeout: int = 30
    max_retries: int = 3

class EscrowReleaseConditions(BaseModel):
    min_rating: float = 4.0
    max_days: int = 30
    required_documents: List[str] = []
    verification_required: bool = True

class AdvancedD17PaymentGateway:
    """نظام دفع متقدم مع دعم الإسكرو والتحقق المتعدد"""

    def __init__(self, config: D17PaymentConfig):
        self.config = config
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.config.timeout))

    async def create_escrow_payment(self,
                                  amount: Decimal,
                                  user_id: str,
                                  company_id: str,
                                  service_type: str,
                                  release_conditions: EscrowReleaseConditions) -> Dict:
        """إنشاء معاملة إسكرو آمنة مع شروط متقدمة"""

        # التحقق المسبق من البيانات
        self._validate_payment_parameters(amount, user_id, company_id)

        order_id = self._generate_order_id(user_id, service_type)

        payment_data = {
            "merchant_id": self.config.merchant_id,
            "amount": float(amount),
            "currency": "TND",
            "order_id": order_id,
            "description": f"خدمة {service_type} - الحارس الذكي",
            "customer_info": {
                "user_id": user_id,
                "country": "TN",
                "ip_address": self._get_client_ip()
            },
            "escrow_settings": {
                "enabled": True,
                "release_conditions": release_conditions.dict(),
                "auto_release_days": release_conditions.max_days,
                "dispute_resolution": {
                    "enabled": True,
                    "arbitrator": "guard_smart_system"
                }
            },
            "metadata": {
                "service_type": service_type,
                "company_id": company_id,
                "user_id": user_id,
                "created_at": datetime.utcnow().isoformat()
            },
            "return_url": "https://guard-smart.tn/payment/success",
            "cancel_url": "https://guard-smart.tn/payment/cancel",
            "notify_url": "https://guard-smart.tn/api/v1/payment/webhook",
            "timestamp": int(datetime.utcnow().timestamp())
        }

        # إضافة التوقيع الأمني
        payment_data["signature"] = self._generate_secure_signature(payment_data)

        # محاولة الدفع مع إعادة المحاولة التلقائية
        for attempt in range(self.config.max_retries):
            try:
                response = await self._make_payment_request(payment_data)
                if response.get("status") == "success":
                    return self._process_successful_response(response, order_id)
                else:
                    raise Exception(f"Payment failed: {response.get('message')}")
            except Exception as e:
                if attempt == self.config.max_retries - 1:
                    raise e
                await asyncio.sleep(1 * (attempt + 1))

    async def _make_payment_request(self, payment_data: Dict) -> Dict:
        """إجراء طلب الدفع مع التحقق من الأخطاء"""
        async with self.session.post(
            f"{self.config.api_url}/payments/create",
            json=payment_data,
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
                "X-Request-ID": self._generate_request_id()
            }
        ) as response:
            if response.status != 200:
                raise Exception(f"HTTP error: {response.status}")

            response_data = await response.json()
            self._validate_response_signature(response_data)

            return response_data

    def _generate_secure_signature(self, data: Dict) -> str:
        """توليد توقيع أمني متقدم"""
        # ترتيب البيانات وتنظيفها
        sorted_data = sorted([
            (k, str(v).lower() if isinstance(v, (bool, str)) else v)
            for k, v in data.items()
            if k != "signature" and v is not None
        ])

        # إنشاء سلسلة الاستعلام
        query_string = "&".join([f"{k}={v}" for k, v in sorted_data])

        # توليد التوقيع باستخدام خوارزمية متقدمة
        signature = hmac.new(
            self.config.secret_key.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()

        return signature

    def _validate_payment_parameters(self, amount: Decimal, user_id: str, company_id: str):
        """التحقق من صحة معاملات الدفع"""
        if amount <= Decimal('0'):
            raise ValueError("المبلغ يجب أن يكون أكبر من الصفر")

        if not user_id or not company_id:
            raise ValueError("معرف المستخدم والشركة مطلوبان")

        if amount > Decimal('10000'):
            raise ValueError("المبلغ لا يمكن أن يتجاوز 10,000 دينار")
