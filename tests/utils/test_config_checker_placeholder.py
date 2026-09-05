"""V12: un placeholder corto no debe leerse como clave API configurada.

El fallback de PageSpeed resuelve `PAGESPEED_API_KEY or GOOGLE_PAGESPEED_API_KEY
or GOOGLE_API_KEY`; un placeholder de 3 chars en cualquiera de esas variables se
reportaba [OK] «configurada» y el síntoma («API key not valid») reaparecía al
eliminar la clave canónica.
"""
from modules.utils.config_checker import ConfigChecker


class TestPlaceholderNoCuentaComoConfigurada:
    def _run_check(self, monkeypatch, **env):
        for key, value in env.items():
            if value is None:
                monkeypatch.delenv(key, raising=False)
            else:
                monkeypatch.setenv(key, value)
        checker = ConfigChecker()
        checker._check_env_variables()
        return checker

    def test_placeholder_corto_genera_warning_y_no_ok(self, monkeypatch):
        checker = self._run_check(monkeypatch, GOOGLE_PAGESPEED_API_KEY="xxx")
        assert not any("GOOGLE_PAGESPEED_API_KEY" in check for check, _ in checker.checks)
        assert any(
            "GOOGLE_PAGESPEED_API_KEY parece un placeholder" in w for w in checker.warnings
        )

    def test_clave_valida_se_reporta_ok(self, monkeypatch):
        valid = "AIza" + "a" * 35  # 39 chars, longitud de una Google API key
        checker = self._run_check(monkeypatch, PAGESPEED_API_KEY=valid)
        assert any("PAGESPEED_API_KEY" in check for check, _ in checker.checks)
        assert not any(
            "PAGESPEED_API_KEY parece un placeholder" in w for w in checker.warnings
        )

    def test_las_dos_claves_pagespeed_estan_en_el_censo(self, monkeypatch):
        checker = self._run_check(
            monkeypatch, PAGESPEED_API_KEY=None, GOOGLE_PAGESPEED_API_KEY=None
        )
        assert any("PAGESPEED_API_KEY" in w for w in checker.warnings)
        assert any("GOOGLE_PAGESPEED_API_KEY" in w for w in checker.warnings)
