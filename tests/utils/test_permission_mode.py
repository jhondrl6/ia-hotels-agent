"""Tests for permission_mode.py"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from modules.utils.permission_mode import (
    PermissionMode,
    COST_THRESHOLD,
    OperationPermission,
    check_permission,
    DEFAULT_MODE,
)


class TestOperationPermission:
    def test_operation_permission_creation(self):
        op = OperationPermission(
            name="places_api_call",
            estimated_cost=0.008,
            is_external=True,
        )
        assert op.name == "places_api_call"
        assert op.estimated_cost == 0.008
        assert op.is_external is True


class TestPermissionDefaults:
    def test_default_mode_is_auto(self):
        assert DEFAULT_MODE == PermissionMode.AUTO

    def test_cost_threshold(self):
        assert COST_THRESHOLD == 0.05


class TestPermissionModeEnum:
    def test_mode_values(self):
        assert PermissionMode.AUTO == "auto"
        assert PermissionMode.SMART_APPROVE == "smart_approve"
        assert PermissionMode.APPROVE == "approve"
        assert PermissionMode.CHAT == "chat"


class TestAutoMode:
    def test_auto_allows_external_expensive(self):
        op = OperationPermission("places_api", 0.50, is_external=True)
        assert check_permission(op, PermissionMode.AUTO) is True

    def test_auto_allows_internal(self):
        op = OperationPermission("local_calc", 0.0, is_external=False)
        assert check_permission(op, PermissionMode.AUTO) is True


class TestChatMode:
    def test_chat_blocks_external(self):
        op = OperationPermission("places_api", 0.008, is_external=True)
        assert check_permission(op, PermissionMode.CHAT) is False

    def test_chat_blocks_all_external(self):
        op = OperationPermission("expensive_api", 1.0, is_external=True)
        assert check_permission(op, PermissionMode.CHAT) is False


class TestApproveMode:
    def test_approve_asks_for_external(self):
        op = OperationPermission("places_api", 0.008, is_external=True)
        result = check_permission(op, PermissionMode.APPROVE, on_ask=lambda n, c: True)
        assert result is True

    def test_approve_rejects_when_user_denies(self):
        op = OperationPermission("places_api", 0.008, is_external=True)
        result = check_permission(op, PermissionMode.APPROVE, on_ask=lambda n, c: False)
        assert result is False

    def test_approve_allows_internal_without_ask(self):
        op = OperationPermission("local_calc", 0.0, is_external=False)
        # Should not call on_ask for internal operations
        ask_called = False
        def should_not_call(n, c):
            nonlocal ask_called
            ask_called = True
            return True
        result = check_permission(op, PermissionMode.APPROVE, on_ask=should_not_call)
        assert result is True
        assert ask_called is False

    def test_approve_without_callback_passes_internal(self):
        op = OperationPermission("local_calc", 0.0, is_external=False)
        assert check_permission(op, PermissionMode.APPROVE) is True


class TestSmartApproveMode:
    def test_smart_approve_allows_cheap_external(self):
        op = OperationPermission("places_api", 0.008, is_external=True)
        assert check_permission(op, PermissionMode.SMART_APPROVE) is True

    def test_smart_approve_asks_expensive_external(self):
        op = OperationPermission("expensive_api", 0.10, is_external=True)
        result = check_permission(op, PermissionMode.SMART_APPROVE, on_ask=lambda n, c: True)
        assert result is True

    def test_smart_approve_denies_expensive_when_user_rejects(self):
        op = OperationPermission("expensive_api", 0.10, is_external=True)
        result = check_permission(op, PermissionMode.SMART_APPROVE, on_ask=lambda n, c: False)
        assert result is False

    def test_smart_approve_denies_expensive_without_callback(self):
        op = OperationPermission("expensive_api", 0.10, is_external=True)
        result = check_permission(op, PermissionMode.SMART_APPROVE)
        assert result is False

    def test_smart_approve_allows_internal(self):
        op = OperationPermission("local_calc", 0.0, is_external=False)
        assert check_permission(op, PermissionMode.SMART_APPROVE) is True

    def test_smart_approve_at_threshold(self):
        op = OperationPermission("at_threshold", COST_THRESHOLD, is_external=True)
        # At exact threshold, should allow (not greater than)
        result = check_permission(op, PermissionMode.SMART_APPROVE)
        # Cost equals threshold means not > threshold, so should pass
        assert result is True


class TestDefaultMode:
    def test_no_mode_allows(self):
        op = OperationPermission("places_api", 0.008, is_external=True)
        assert check_permission(op) is True
