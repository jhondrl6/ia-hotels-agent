"""Deployer module for remote asset deployment.

This module provides the infrastructure for deploying generated assets
to hotel websites remotely via FTP or WordPress API.

v2.5 MVP: Dry-run mode only (validates credentials, lists actions).
v2.6+: Full deployment execution.
"""

from modules.deployer.manager import DeployManager

__all__ = ["DeployManager"]
