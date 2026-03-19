import os
import requests
from typing import Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class PageSpeedResult:
    url: str
    device: str
    has_field_data: bool
    performance_score: Optional[int]
    lcp: Optional[float]
    fid: Optional[int]
    cls: Optional[float]
    tbt: Optional[int]
    status: str
    message: str
    raw_response: Optional[Dict] = None


class PageSpeedClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("PAGESPEED_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.base_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

        if not self.api_key:
            raise ValueError(
                "API key is required. Provide it as a parameter or set PAGESPEED_API_KEY environment variable."
            )

    def _make_request(self, url: str, device: str = "mobile") -> Dict:
        params = {
            "url": url,
            "key": self.api_key,
            "device": device,
            "category": "PERFORMANCE",
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=30)

            if response.status_code == 429:
                raise Exception("PageSpeed API rate limit exceeded. Please try again later.")
            elif response.status_code == 400:
                error_data = response.json()
                error_msg = error_data.get("error", {}).get("message", "Invalid request")
                raise ValueError(f"Invalid URL or request: {error_msg}")
            elif response.status_code == 403:
                raise Exception("Invalid API key or API key has exceeded quota.")
            elif response.status_code != 200:
                raise Exception(f"API request failed with status {response.status_code}: {response.text}")

            return response.json()

        except requests.exceptions.Timeout:
            raise Exception("Request to PageSpeed API timed out.")
        except requests.exceptions.ConnectionError:
            raise Exception("Network error: Unable to connect to PageSpeed API.")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")

    def analyze_url(self, url: str, device: str = "mobile") -> PageSpeedResult:
        try:
            data = self._make_request(url, device)

            # SIEMPRE extraer Lighthouse score (siempre disponible)
            lighthouse_result = data.get("lighthouseResult", {})
            categories = lighthouse_result.get("categories", {})
            performance = categories.get("performance", {})
            performance_score = performance.get("score")
            if performance_score is not None:
                performance_score = int(performance_score * 100)

            # Extraer audits adicionales de Lighthouse (lab data)
            audits = lighthouse_result.get("audits", {})

            # LCP Lab (siempre disponible en Lighthouse)
            lcp_lab = audits.get("largest-contentful-paint", {})
            lcp_lab_value = lcp_lab.get("numericValue")
            if lcp_lab_value:
                lcp_lab_value = lcp_lab_value / 1000.0  # Convertir a segundos

            # CLS Lab
            cls_lab = audits.get("cumulative-layout-shift", {})
            cls_lab_value = cls_lab.get("numericValue")

            # TBT Lab
            tbt_audit = audits.get("total-blocking-time", {})
            tbt = tbt_audit.get("numericValue")
            if tbt is not None:
                tbt = int(tbt)

            # Verificar CrUX field data
            loading_experience = data.get("loadingExperience", {})
            has_field_data = "metrics" in loading_experience

            if has_field_data:
                metrics = loading_experience.get("metrics", {})

                lcp_data = metrics.get("LARGEST_CONTENTFUL_PAINT_MS", {})
                fid_data = metrics.get("FIRST_INPUT_DELAY_MS", {})
                cls_data = metrics.get("CUMULATIVE_LAYOUT_SHIFT_SCORE", {})

                lcp_field = lcp_data.get("percentile")
                fid = fid_data.get("percentile")
                cls_field = cls_data.get("percentile")

                if lcp_field is not None:
                    lcp_field = lcp_field / 1000.0

                if cls_field is not None:
                    cls_field = cls_field / 100.0

                return PageSpeedResult(
                    url=url,
                    device=device,
                    has_field_data=True,
                    performance_score=performance_score,
                    lcp=lcp_field or lcp_lab_value,
                    fid=fid,
                    cls=cls_field or cls_lab_value,
                    tbt=tbt,
                    status="VERIFIED",
                    message="Core Web Vitals data successfully retrieved from Chrome User Experience Report.",
                    raw_response=data,
                )
            else:
                # No hay CrUX data, usar lab data
                return PageSpeedResult(
                    url=url,
                    device=device,
                    has_field_data=False,
                    performance_score=performance_score,
                    lcp=lcp_lab_value,
                    fid=None,
                    cls=cls_lab_value,
                    tbt=tbt,
                    status="LAB_DATA_ONLY",
                    message="Lighthouse lab data available. Field data not yet available from Chrome User Experience Report.",
                    raw_response=data,
                )

        except ValueError as e:
            return PageSpeedResult(
                url=url,
                device=device,
                has_field_data=False,
                performance_score=None,
                lcp=None,
                fid=None,
                cls=None,
                tbt=None,
                status="ERROR",
                message=str(e),
                raw_response=None,
            )
        except Exception as e:
            return PageSpeedResult(
                url=url,
                device=device,
                has_field_data=False,
                performance_score=None,
                lcp=None,
                fid=None,
                cls=None,
                tbt=None,
                status="ERROR",
                message=str(e),
                raw_response=None,
            )

    def get_core_web_vitals(self, url: str) -> Dict[str, Any]:
        mobile_result = self.analyze_url(url, device="mobile")
        desktop_result = self.analyze_url(url, device="desktop")

        return {
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "mobile": mobile_result,
            "desktop": desktop_result,
            "summary": {
                "mobile_status": mobile_result.status,
                "desktop_status": desktop_result.status,
                "has_complete_data": (
                    mobile_result.has_field_data and desktop_result.has_field_data
                ),
            },
        }

    @staticmethod
    def interpret_lcp(lcp: float) -> str:
        if lcp < 2.5:
            return "Good"
        elif lcp < 4.0:
            return "Needs Improvement"
        else:
            return "Poor"

    @staticmethod
    def interpret_cls(cls: float) -> str:
        if cls < 0.1:
            return "Good"
        elif cls < 0.25:
            return "Needs Improvement"
        else:
            return "Poor"
