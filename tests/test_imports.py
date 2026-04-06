#!/usr/bin/env python3
import sys
sys.path.insert(0, r"C:\Users\Jhond\Github\iah-cli")

try:
    from modules.auditors.v4_comprehensive import V4ComprehensiveAuditor, CrossValidationResult
    print("v4_comprehensive import: OK")
except Exception as e:
    print(f"v4_comprehensive import: FAIL - {e}")

try:
    from modules.data_validation.cross_validator import CrossValidator
    print("cross_validator import: OK")
except Exception as e:
    print(f"cross_validator import: FAIL - {e}")

try:
    from modules.auditors.seo_elements_detector import SEOElementsDetector, SEOElementsResult
    print("seo_elements_detector import: OK")
except Exception as e:
    print(f"seo_elements_detector import: FAIL - {e}")

try:
    from modules.commercial_documents.v4_diagnostic_generator import V4DiagnosticGenerator
    print("v4_diagnostic_generator import: OK")
except Exception as e:
    print(f"v4_diagnostic_generator import: FAIL - {e}")

print("All imports completed.")
