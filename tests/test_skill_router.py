"""Tests for Agent Harness Skill Router and Executor."""

import tempfile
from pathlib import Path

import pytest

from agent_harness.skill_router import SkillRouter, SkillDefinition
from agent_harness.skill_executor import SkillExecutor, StepType


class TestSkillRouter:
    """Tests for SkillRouter class."""
    
    @pytest.fixture
    def temp_workflows_dir(self):
        """Create a temporary workflows directory with sample files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workflows_path = Path(tmpdir)
            
            # Create sample workflow file
            sample_workflow = '''---
description: Sample skill for testing
---

# Skill: Sample Test

## Pre-requisitos
- [ ] Python installed
- [ ] Environment configured

## Pasos de Ejecución

### 1. First Step
Run the first command.
```bash
echo "Hello World"
```
*Validación*: Should output Hello World.

### 2. Second Step
This is a manual step.
'''
            (workflows_path / "sample_skill.md").write_text(sample_workflow, encoding="utf-8")
            
            # Create turbo workflow
            turbo_workflow = '''---
description: Turbo-enabled skill
---

# Skill: Turbo Test

// turbo-all

### 1. Auto Step
```bash
echo "Auto"
```
'''
            (workflows_path / "turbo_skill.md").write_text(turbo_workflow, encoding="utf-8")
            
            yield workflows_path
    
    @pytest.fixture
    def router(self, temp_workflows_dir):
        """Create a SkillRouter with temporary workflows."""
        return SkillRouter(workflows_path=temp_workflows_dir, verbose=False)
    
    def test_scan_finds_skills(self, router):
        """Router should find skills in directory."""
        skills = router.list_skills()
        assert len(skills) == 2
    
    def test_get_skill_by_name(self, router):
        """get_skill should find by name."""
        skill = router.get_skill("sample_skill")
        assert skill is not None
        assert skill.name == "sample_skill"
    
    def test_get_skill_by_slug(self, router):
        """get_skill should find by slug."""
        skill = router.get_skill("/sample_skill")
        assert skill is not None
        assert skill.slug == "/sample_skill"
    
    def test_skill_has_description(self, router):
        """Skill should have description from frontmatter."""
        skill = router.get_skill("sample_skill")
        assert skill.description == "Sample skill for testing"
    
    def test_skill_counts_steps(self, router):
        """Skill should count steps correctly."""
        skill = router.get_skill("sample_skill")
        assert skill.steps_count == 2
    
    def test_skill_detects_turbo(self, router):
        """Skill should detect turbo annotation."""
        turbo_skill = router.get_skill("turbo_skill")
        assert turbo_skill.has_turbo is True
        
        normal_skill = router.get_skill("sample_skill")
        assert normal_skill.has_turbo is False
    
    def test_skill_exists(self, router):
        """skill_exists should return correct boolean."""
        assert router.skill_exists("sample_skill") is True
        assert router.skill_exists("nonexistent") is False
    
    def test_to_dict(self, router):
        """to_dict should export catalog."""
        catalog = router.to_dict()
        assert catalog["count"] == 2
        assert len(catalog["skills"]) == 2


class TestSkillExecutor:
    """Tests for SkillExecutor class."""
    
    @pytest.fixture
    def temp_skill(self):
        """Create a temporary skill file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test_skill.md"
            content = '''---
description: Test execution skill
---

# Skill: Test Execution

### 1. First Command
Run first.
```bash
echo "Step 1"
```
*Validación*: Outputs Step 1.

// turbo
### 2. Turbo Step
Auto-run this.
```bash
echo "Step 2"
```

### 3. Manual Step
Do this manually.
'''
            path.write_text(content, encoding="utf-8")
            
            skill = SkillDefinition(
                name="test_skill",
                slug="/test_skill",
                path=path,
                description="Test execution skill",
            )
            yield skill
    
    @pytest.fixture
    def executor(self):
        """Create a SkillExecutor."""
        return SkillExecutor(verbose=False)
    
    def test_parse_workflow_finds_steps(self, executor, temp_skill):
        """parse_workflow should find all steps."""
        steps = executor.parse_workflow(temp_skill)
        assert len(steps) == 3
    
    def test_parse_workflow_extracts_code(self, executor, temp_skill):
        """parse_workflow should extract code blocks."""
        steps = executor.parse_workflow(temp_skill)
        assert steps[0].code == 'echo "Step 1"'
    
    def test_parse_workflow_detects_turbo(self, executor, temp_skill):
        """parse_workflow should detect turbo annotation."""
        steps = executor.parse_workflow(temp_skill)
        # Step 2 has turbo annotation
        turbo_steps = [s for s in steps if s.is_turbo]
        assert len(turbo_steps) >= 1
    
    def test_parse_workflow_identifies_types(self, executor, temp_skill):
        """parse_workflow should identify step types."""
        steps = executor.parse_workflow(temp_skill)
        command_steps = [s for s in steps if s.step_type == StepType.COMMAND]
        manual_steps = [s for s in steps if s.step_type == StepType.MANUAL]
        
        assert len(command_steps) == 2
        assert len(manual_steps) == 1
    
    def test_get_step_summary(self, executor, temp_skill):
        """get_step_summary should provide overview."""
        summary = executor.get_step_summary(temp_skill)
        
        assert summary["skill"] == "test_skill"
        assert summary["total_steps"] == 3
    
    def test_execute_skill_dry_run(self, executor, temp_skill):
        """execute_skill dry_run should not execute."""
        result = executor.execute_skill(temp_skill, dry_run=True)
        
        assert result.success is True
        assert len(result.steps_executed) == 0
        assert "DRY RUN" in result.output
