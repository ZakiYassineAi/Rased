from typing import Dict, List
from sklearn.feature_extraction.text import TfidfVectorizer

class AdvancedOpportunityMatcher:
    """نظام مطابقة الفرص المتقدم باستخدام خوارزميات ML"""

    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000)
        self.similarity_threshold = 0.7

    async def match_user_to_opportunities(self, user_profile: Dict, opportunities: List[Dict]) -> List[Dict]:
        """مطابقة المستخدم مع الفرص المناسبة"""

        # تحليل الملف الشخصي
        user_vectors = self._vectorize_profile(user_profile)

        # تقييم كل فرصة
        scored_opportunities = []
        for opportunity in opportunities:
            score = await self._calculate_match_score(user_vectors, opportunity)
            if score >= self.similarity_threshold:
                scored_opportunities.append({
                    **opportunity,
                    "match_score": score,
                    "match_reasons": self._get_match_reasons(user_profile, opportunity),
                    "improvement_suggestions": self._get_improvement_suggestions(user_profile, opportunity)
                })

        # ترتيب حسب درجة المطابقة
        return sorted(scored_opportunities, key=lambda x: x["match_score"], reverse=True)

    def _vectorize_profile(self, profile: Dict) -> Dict:
        """تحويل الملف الشخصي إلى تمثيل رقمي"""
        # تجميع النص من الملف الشخصي
        text_data = f"""
        {profile.get('education_level', '')}
        {profile.get('skills', [])}
        {profile.get('work_experience', [])}
        {profile.get('languages', [])}
        """

        return self.vectorizer.fit_transform([text_data])
