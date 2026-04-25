"""
Regression test: ensure that setting SARVAM_API_KEY (uppercase) causes
settings.py to choose the Sarvam endpoint instead of HuggingFace.
"""

import importlib
import os
import sys


def _reload_settings(env_overrides: dict) -> object:
    """Re-import core.settings with a modified environment."""
    # Remove cached module so it is re-evaluated with new env vars
    for key in list(sys.modules.keys()):
        if "core.settings" in key or key == "core.settings":
            del sys.modules[key]
    # Also remove the parent package cache entry that might hold a stale ref
    if "core" in sys.modules:
        del sys.modules["core"]

    saved = {}
    for k, v in env_overrides.items():
        saved[k] = os.environ.get(k)
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v

    try:
        # Ensure the project root is on sys.path
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        if root not in sys.path:
            sys.path.insert(0, root)
        settings = importlib.import_module("core.settings")
    finally:
        # Restore original environment
        for k, orig in saved.items():
            if orig is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = orig

    return settings


def test_sarvam_key_uppercase_enables_direct_mode():
    """With SARVAM_API_KEY set (and no Databricks vars), USE_SARVAM_DIRECT must be True and
    LLM_BASE_URL must point to Sarvam (not HuggingFace)."""
    settings = _reload_settings({
        "SARVAM_API_KEY": "test-key-12345",
        "DATABRICKS_HOST": None,
        "DATABRICKS_TOKEN": None,
    })

    assert settings.USE_SARVAM_DIRECT is True, (
        "USE_SARVAM_DIRECT should be True when SARVAM_API_KEY is set"
    )
    assert "huggingface" not in settings.LLM_BASE_URL.lower(), (
        f"LLM_BASE_URL should not point to HuggingFace when SARVAM_API_KEY is set, "
        f"got: {settings.LLM_BASE_URL}"
    )
    assert settings.LLM_API_KEY == "test-key-12345", (
        "LLM_API_KEY should equal the SARVAM_API_KEY value"
    )


def test_missing_sarvam_key_falls_back_to_hf():
    """Without SARVAM_API_KEY or Databricks vars, USE_SARVAM_DIRECT must be False and
    LLM_BASE_URL must point to HuggingFace."""
    settings = _reload_settings({
        "SARVAM_API_KEY": None,
        "DATABRICKS_HOST": None,
        "DATABRICKS_TOKEN": None,
    })

    assert settings.USE_SARVAM_DIRECT is False, (
        "USE_SARVAM_DIRECT should be False when SARVAM_API_KEY is not set"
    )
    assert "huggingface" in settings.LLM_BASE_URL.lower(), (
        f"LLM_BASE_URL should point to HuggingFace when SARVAM_API_KEY is absent, "
        f"got: {settings.LLM_BASE_URL}"
    )


def test_lowercase_sarvam_key_does_not_enable_direct_mode():
    """Setting only the lowercase sarvam_api_key must NOT enable Sarvam mode —
    the app.yaml sets the uppercase SARVAM_API_KEY."""
    # Ensure uppercase is absent, only set the old incorrect lowercase name
    settings = _reload_settings(
        {"SARVAM_API_KEY": None, "sarvam_api_key": "wrong-case-key",
         "DATABRICKS_HOST": None, "DATABRICKS_TOKEN": None}
    )

    assert settings.USE_SARVAM_DIRECT is False, (
        "Setting lowercase sarvam_api_key should have no effect; "
        "only SARVAM_API_KEY (uppercase) is honored"
    )


def test_databricks_env_vars_select_databricks_endpoint():
    """When DATABRICKS_HOST and DATABRICKS_TOKEN are set, configuration must
    select the Databricks serving-endpoints URL and not Sarvam or HuggingFace."""
    settings = _reload_settings({
        "DATABRICKS_HOST": "https://dbc-test.cloud.databricks.com/",
        "DATABRICKS_TOKEN": "dapi-test-token",
        "SARVAM_API_KEY": None,
    })

    assert "serving-endpoints" in settings.LLM_BASE_URL, (
        f"LLM_BASE_URL should contain /serving-endpoints when Databricks is configured, "
        f"got: {settings.LLM_BASE_URL}"
    )
    assert "sarvam" not in settings.LLM_BASE_URL.lower(), (
        f"LLM_BASE_URL should not point to Sarvam when Databricks is configured, "
        f"got: {settings.LLM_BASE_URL}"
    )
    assert "huggingface" not in settings.LLM_BASE_URL.lower(), (
        f"LLM_BASE_URL should not point to HuggingFace when Databricks is configured, "
        f"got: {settings.LLM_BASE_URL}"
    )
    assert settings.LLM_API_KEY == "dapi-test-token", (
        "LLM_API_KEY should equal DATABRICKS_TOKEN"
    )
    # Trailing slash on host must not create double slashes in the path
    url_path = settings.LLM_BASE_URL.replace("https://", "")
    assert "//" not in url_path, (
        f"LLM_BASE_URL must not contain double slashes, got: {settings.LLM_BASE_URL}"
    )
    assert settings.USE_SARVAM_DIRECT is False, (
        "USE_SARVAM_DIRECT should be False when Databricks is the active endpoint"
    )
