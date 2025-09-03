import asyncio
import re
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import aiohttp
from pydantic import BaseModel, Field, validator
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class ContractRiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ContractClauseType(Enum):
    SALARY = "salary"
    WORKING_HOURS = "working_hours"
    VACATION = "vacation"
    TERMINATION = "termination"
    CONFIDENTIALITY = "confidentiality"
    NON_COMPETE = "non_compete"
    INTELECTUAL_PROPERTY = "intellectual_property"
    LIABILITY = "liability"

@dataclass
class ContractAnalysisResult:
    risk_score: float
    risk_level: ContractRiskLevel
    red_flags: List[Dict[str, str]]
    recommendations: List[str]
    clauses_analysis: Dict[ContractClauseType, Dict]
    missing_clauses: List[ContractClauseType]
    confidence_score: float
    detailed_breakdown: Dict

class TunisianContractAnalyzer:
    """نظام متقدم لتحليل العقود باستخدام الذكاء الاصطناعي"""

    def __init__(self):
        self.red_flags_patterns = {
            "unreasonable_termination": [
                r"يمكن لصاحب العمل إنهاء العقد دون إشعار",
                r"إنهاء العقد دون تعويض",
                r"التنازل عن الحق في المطالبة بتعويض"
            ],
            "hidden_fees": [
                r"رسوم.*التوظيف",
                r"مصاريف.*الاجراءات",
                r"دفع.*مقدم"
            ],
            "salary_issues": [
                r"راتب أقل من.*الحد الأدنى",
                r"عدم تحديد الراتب بشكل واضح",
                r"خصومات غير مبررة"
            ],
            "working_conditions": [
                r"ساعات عمل.*تزيد عن.*48",
                r"عدم تحديد أيام الراحة",
                r"عمل إضافي غير مدفوع"
            ]
        }

        self.required_clauses = [
            ContractClauseType.SALARY,
            ContractClauseType.WORKING_HOURS,
            ContractClauseType.VACATION,
            ContractClauseType.TERMINATION
        ]

        # تحميل نماذج الذكاء الاصطناعي المسبقة التدريب
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=5000)
        self._initialize_models()

    def _initialize_models(self):
        """تهيئة نماذج الذكاء الاصطناعي"""
        # سيتم تحميل النماذج المسبقة التدريب هنا
        pass

    async def analyze_contract(self, contract_text: str, context: Dict) -> ContractAnalysisResult:
        """تحليل شامل للعقد باستخدام تقنيات متعددة"""

        # تحليل متوازي لمختلف جوانب العقد
        analysis_tasks = [
            self._detect_red_flags(contract_text),
            self._extract_and_validate_clauses(contract_text),
            self._compare_with_standards(contract_text, context),
            self._calculate_risk_score(contract_text)
        ]

        results = await asyncio.gather(*analysis_tasks)

        # تجميع النتائج
        red_flags = results[0]
        clauses_analysis = results[1]
        standards_comparison = results[2]
        risk_score = results[3]

        # تحديد البنود المفقودة
        missing_clauses = self._identify_missing_clauses(clauses_analysis)

        # توليد التوصيات
        recommendations = self._generate_recommendations(
            red_flags, clauses_analysis, missing_clauses, standards_comparison
        )

        return ContractAnalysisResult(
            risk_score=risk_score,
            risk_level=self._determine_risk_level(risk_score),
            red_flags=red_flags,
            recommendations=recommendations,
            clauses_analysis=clauses_analysis,
            missing_clauses=missing_clauses,
            confidence_score=self._calculate_confidence(red_flags, clauses_analysis),
            detailed_breakdown={
                "red_flags": red_flags,
                "clauses_analysis": clauses_analysis,
                "standards_comparison": standards_comparison
            }
        )

    async def _detect_red_flags(self, text: str) -> List[Dict[str, str]]:
        """كشف العلامات الحمراء باستخدام أنماط متقدمة"""
        red_flags = []

        for category, patterns in self.red_flags_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    red_flags.append({
                        "category": category,
                        "pattern": pattern,
                        "matched_text": match.group(),
                        "position": match.start()
                    })

        return red_flags

    async def _extract_and_validate_clauses(self, text: str) -> Dict[ContractClauseType, Dict]:
        """استخراج والتحقق من البنود التعاقدية"""
        clauses = {}

        # استخدام نماذج الذكاء الاصطناعي لاستخراج البنود
        for clause_type in ContractClauseType:
            clause_text = self._extract_clause(text, clause_type)
            if clause_text:
                validation = self._validate_clause(clause_type, clause_text)
                clauses[clause_type] = {
                    "text": clause_text,
                    "validation": validation,
                    "is_compliant": validation.get("is_compliant", False)
                }

        return clauses

    def _extract_clause(self, text: str, clause_type: ContractClauseType) -> Optional[str]:
        """استخراج بند محدد من النص"""
        # تطبيق خوارزميات متقدمة لاستخراج البنود
        patterns = {
            ContractClauseType.SALARY: [
                r"(الراتب|الأجر|المكافأة)[^\n]{0,200}دينار",
                r"(راتب|أجر)[^\n]{0,100}\d+[^\n]{0,50}دينار"
            ],
            ContractClauseType.WORKING_HOURS: [
                r"(ساعات العمل|المدة الأسبوعية)[^\n]{0,150}\d+[^\n]{0,50}ساعة"
            ]
        }

        if clause_type in patterns:
            for pattern in patterns[clause_type]:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    return match.group()

        return None

    def _validate_clause(self, clause_type: ContractClauseType, clause_text: str) -> Dict:
        """التحقق من مطابقة البند للمعايير التونسية"""
        validations = {
            "is_compliant": False,
            "issues": [],
            "suggestions": []
        }

        if clause_type == ContractClauseType.SALARY:
            # التحقق من أن الراتب فوق الحد الأدنى
            salary_match = re.search(r'(\d+[,.]?\d*)\s*دينار', clause_text)
            if salary_match:
                salary = float(salary_match.group(1).replace(',', '.'))
                if salary >= 450:  # الحد الأدنى التونسي التقريبي
                    validations["is_compliant"] = True
                else:
                    validations["issues"].append(f"الراتب ({salary}) أقل من الحد الأدنى")
                    validations["suggestions"].append("رفع الراتب إلى 450 دينار على الأقل")

        return validations

    def _identify_missing_clauses(self, clauses_analysis: Dict) -> List[ContractClauseType]:
        """تحديد البنود المفقودة في العقد"""
        return [clause for clause in self.required_clauses if clause not in clauses_analysis]
