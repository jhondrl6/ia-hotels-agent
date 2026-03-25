"""
Data Assessment Module - FASE 6: Orchestration V2

Classifies hotel data availability into LOW/MED/HIGH tiers to determine
the appropriate generation path (fast/standard/full).

Classification Logic:
- LOW (< 30%): Minimal data available → Fast Path (3-4 assets)
- MED (30-70%): Partial data → Standard Path (6-7 assets)
- HIGH (> 70%): Complete data → Full Path (9+ assets)

Metrics evaluated:
- GBP completeness (reviews, photos, score)
- Web scraping success
- SEO data availability
- Schema markup presence
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum


class DataClassification(Enum):
    """Data availability classification tiers."""
    LOW = "low"       # < 30% data available
    MED = "medium"    # 30-70% data available
    HIGH = "high"     # > 70% data available


# Thresholds for classification
CLASSIFICATION_THRESHOLDS = {
    "low_max": 0.30,      # < 30% = LOW
    "high_min": 0.70,     # > 70% = HIGH
    # Everything in between = MED
}


@dataclass
class DataMetric:
    """Individual metric for data assessment."""
    name: str
    available: bool
    weight: float  # 0.0 - 1.0, contribution to overall score
    details: str = ""


@dataclass
class DataAssessmentResult:
    """Result of data assessment with classification and metrics."""
    classification: DataClassification
    overall_score: float  # 0.0 - 1.0
    metrics: List[DataMetric]
    missing_data: List[str]
    recommendations: List[str]
    
    @property
    def is_valid(self) -> bool:
        """Data is valid if classification is not completely absent."""
        return self.classification != DataClassification.LOW or len(self.missing_data) < 5


class DataAssessment:
    """
    Assesses hotel data quality and classifies it into LOW/MED/HIGH tiers.
    
    This assessment runs BEFORE generation to determine which path to take:
    - LOW data → Fast generation (3-4 essential assets only)
    - MED data → Standard generation (6-7 assets)
    - HIGH data → Full generation (9+ assets)
    """
    
    def __init__(self):
        """Initialize the data assessor."""
        pass
    
    def assess(
        self,
        hotel_data: Dict[str, Any],
        gbp_data: Optional[Dict[str, Any]] = None,
        seo_data: Optional[Dict[str, Any]] = None,
        scraping_success: bool = False
    ) -> DataAssessmentResult:
        """
        Assess data availability and return classification.
        
        Args:
            hotel_data: Core hotel data (name, address, phone, etc.)
            gbp_data: Google Business Profile data (reviews, photos, score)
            seo_data: SEO-related data (schema markup, meta tags)
            scraping_success: Whether web scraping succeeded
            
        Returns:
            DataAssessmentResult with classification and metrics
        """
        metrics: List[DataMetric] = []
        missing_data: List[str] = []
        total_weight = 0.0
        weighted_score = 0.0
        
        # 1. Core hotel data assessment (weight: 0.25)
        core_score, core_missing = self._assess_core_data(hotel_data)
        metrics.append(DataMetric(
            name="core_hotel_data",
            available=core_score > 0,
            weight=0.25,
            details=f"Score: {core_score:.2f}, Missing: {core_missing}"
        ))
        weighted_score += core_score * 0.25
        total_weight += 0.25
        missing_data.extend(core_missing)
        
        # 2. GBP data assessment (weight: 0.35)
        gbp_score, gbp_missing = self._assess_gbp_data(gbp_data or {})
        metrics.append(DataMetric(
            name="gbp_data",
            available=gbp_score > 0,
            weight=0.35,
            details=f"Score: {gbp_score:.2f}, Missing: {gbp_missing}"
        ))
        weighted_score += gbp_score * 0.35
        total_weight += 0.35
        missing_data.extend(gbp_missing)
        
        # 3. SEO data assessment (weight: 0.20)
        seo_score, seo_missing = self._assess_seo_data(seo_data or {})
        metrics.append(DataMetric(
            name="seo_data",
            available=seo_score > 0,
            weight=0.20,
            details=f"Score: {seo_score:.2f}, Missing: {seo_missing}"
        ))
        weighted_score += seo_score * 0.20
        total_weight += 0.20
        missing_data.extend(seo_missing)
        
        # 4. Web scraping success (weight: 0.20)
        scraping_score = 1.0 if scraping_success else 0.0
        metrics.append(DataMetric(
            name="web_scraping",
            available=scraping_success,
            weight=0.20,
            details="Success" if scraping_success else "Failed/No data"
        ))
        weighted_score += scraping_score * 0.20
        total_weight += 0.20
        if not scraping_success:
            missing_data.append("web_scraping")
        
        # Normalize score by actual weight used
        overall_score = weighted_score / total_weight if total_weight > 0 else 0.0
        
        # Classify based on score
        classification = self._classify_score(overall_score)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(classification, missing_data)
        
        return DataAssessmentResult(
            classification=classification,
            overall_score=overall_score,
            metrics=metrics,
            missing_data=list(set(missing_data)),  # Remove duplicates
            recommendations=recommendations
        )
    
    def _assess_core_data(self, hotel_data: Dict[str, Any]) -> tuple:
        """
        Assess core hotel data availability.
        
        Returns:
            Tuple of (score, list of missing fields)
        """
        required_fields = ["name", "phone", "address"]
        optional_fields = ["email", "website", "description", "amenities"]
        
        if not hotel_data:
            return 0.0, required_fields + optional_fields
        
        present_fields = [f for f in required_fields if hotel_data.get(f)]
        present_optional = [f for f in optional_fields if hotel_data.get(f)]
        
        # Required fields weight: 60%, Optional: 40%
        required_score = len(present_fields) / len(required_fields) if required_fields else 0
        optional_score = len(present_optional) / len(optional_fields) if optional_fields else 0
        
        overall = (required_score * 0.6) + (optional_score * 0.4)
        
        missing = [f for f in required_fields if f not in present_fields]
        missing.extend([f for f in optional_fields if f not in present_optional])
        
        return overall, missing
    
    def _assess_gbp_data(self, gbp_data: Dict[str, Any]) -> tuple:
        """
        Assess Google Business Profile data availability.
        
        Returns:
            Tuple of (score, list of missing fields)
        """
        if not gbp_data:
            return 0.0, ["reviews", "photos", "rating", "reviews_count"]
        
        metrics_evaluated = ["reviews", "photos", "rating", "reviews_count"]
        present = []
        missing = []
        
        for metric in metrics_evaluated:
            value = gbp_data.get(metric)
            if value is not None and value != 0:
                present.append(metric)
            else:
                missing.append(metric)
        
        # Reviews matter more if there's actual content
        reviews = gbp_data.get("reviews", [])
        has_reviews = isinstance(reviews, list) and len(reviews) > 0
        
        photos = gbp_data.get("photos", [])
        has_photos = isinstance(photos, list) and len(photos) > 0
        
        score = len(present) / len(metrics_evaluated)
        
        # Boost score if reviews have actual content
        if has_reviews:
            score = min(1.0, score + 0.1)
        if has_photos:
            score = min(1.0, score + 0.1)
        
        return score, missing
    
    def _assess_seo_data(self, seo_data: Dict[str, Any]) -> tuple:
        """
        Assess SEO data availability.
        
        Returns:
            Tuple of (score, list of missing fields)
        """
        if not seo_data:
            return 0.0, ["schema_markup", "meta_description", "title_tag", "headings"]
        
        fields = ["schema_markup", "meta_description", "title_tag", "headings"]
        present = [f for f in fields if seo_data.get(f)]
        missing = [f for f in fields if not seo_data.get(f)]
        
        score = len(present) / len(fields) if fields else 0
        
        return score, missing
    
    def _classify_score(self, score: float) -> DataClassification:
        """
        Classify the overall score into LOW/MED/HIGH.
        
        Args:
            score: Overall data availability score (0.0 - 1.0)
            
        Returns:
            DataClassification enum value
        """
        if score < CLASSIFICATION_THRESHOLDS["low_max"]:
            return DataClassification.LOW
        elif score >= CLASSIFICATION_THRESHOLDS["high_min"]:
            return DataClassification.HIGH
        else:
            return DataClassification.MED
    
    def _generate_recommendations(
        self,
        classification: DataClassification,
        missing_data: List[str]
    ) -> List[str]:
        """
        Generate recommendations based on classification and missing data.
        
        Args:
            classification: The data classification tier
            missing_data: List of missing data fields
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        if classification == DataClassification.LOW:
            recommendations.append("Use FAST path: Generate only essential assets (3-4)")
            recommendations.append("Consider running AutonomousResearcher to fill data gaps")
            if "reviews" in missing_data:
                recommendations.append("Collect customer reviews to improve MED/HIGH classification")
        elif classification == DataClassification.MED:
            recommendations.append("Use STANDARD path: Generate moderate asset set (6-7)")
            recommendations.append("Some assets will use fallback data")
        else:  # HIGH
            recommendations.append("Use FULL path: Generate complete asset suite (9+)")
            recommendations.append("All data sources are well populated")
        
        return recommendations
    
    def get_generation_path(self, classification: DataClassification) -> str:
        """
        Get the appropriate generation path name for a classification.
        
        Args:
            classification: The data classification tier
            
        Returns:
            Path name: 'fast', 'standard', or 'full'
        """
        path_map = {
            DataClassification.LOW: "fast",
            DataClassification.MED: "standard",
            DataClassification.HIGH: "full"
        }
        return path_map.get(classification, "standard")
    
    def get_asset_count_range(self, classification: DataClassification) -> tuple:
        """
        Get the expected asset count range for a classification.
        
        Args:
            classification: The data classification tier
            
        Returns:
            Tuple of (min_assets, max_assets)
        """
        ranges = {
            DataClassification.LOW: (3, 4),
            DataClassification.MED: (6, 7),
            DataClassification.HIGH: (9, 12)
        }
        return ranges.get(classification, (6, 7))
