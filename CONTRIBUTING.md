# Contributing to mayaLint Academic Extension

Thank you for your interest in contributing to the mayaLint Academic Extension! This guide will help you understand our development workflow and standards.

## Overview

This project extends the original [modelChecker](https://github.com/JakobJK/modelChecker) Maya plugin with 15 additional checks designed for academic evaluation of 3D models.

## Development Workflow

We use Claude Code slash commands to manage the implementation workflow:

| Command | Purpose |
|---------|---------|
| `/plan-release` | View the release roadmap and check status |
| `/dashboard` | Visual progress dashboard |
| `/start <check_id>` | Begin implementing a check |
| `/finish <check_id>` | Complete, verify, and commit a check |
| `/update-preview` | Update and deploy the UI preview |

## Implementation Standards

### 7-Step Workflow

Every new check must follow these 7 steps:

1. **Implementation** - Create the check function
2. **Registration** - Add to command list
3. **Testing** - Create test file with 4+ test cases
4. **Integration Testing** - Verify compatibility
5. **Documentation** - Update CHECKS.md
6. **UI Preview** - Update and deploy preview
7. **Finalization** - Commit and push

### Code Standards

#### Function Signature
```python
def checkName(nodes, SLMesh):
    # nodes: List of node UUIDs
    # SLMesh: MSelectionList containing mesh shapes
```

#### Return Format
```python
# For node-level errors:
return ("nodes", [uuid1, uuid2, ...])

# For component-level errors:
return ("polygon", {uuid: [face_indices]})  # or "vertex", "edge", "uv"
```

#### Docstring Requirements
Every function must include:
- Description
- Algorithm explanation
- Args section
- Returns section
- Known Limitations
- Academic Use context

### Testing Requirements

Each check needs a test file at `tests/test_<check_id>.py` with:
- Header documentation explaining the check
- Minimum 4 test cases:
  1. Pass case (clean geometry)
  2. Fail case (problematic geometry)
  3. Edge case handling
  4. Limitation documentation
- Maya test script for manual verification

### Documentation Requirements

Update `CHECKS.md` with:
- Description of what the check detects
- Why it matters for academic grading
- How the algorithm works
- Known limitations with workarounds
- How to fix detected issues in Maya
- Test case summary

## File Structure

```
mayaLint/
├── mayaLint/
│   ├── mayaLint_commands.py  # Check implementations
│   ├── mayaLint_list.py      # Command registry
│   └── mayaLint_UI.py        # Maya UI (don't modify)
├── tests/
│   └── test_<check_id>.py        # Test files
├── ui-preview/
│   ├── index.html                # Interactive UI mockup
│   └── checks-overview.html      # 1-pager documentation
├── .claude/
│   ├── release-plan.json         # Project state
│   └── commands/                 # Slash commands
├── CHECKS.md                     # Check documentation
├── CONTRIBUTING.md               # This file
└── CHANGELOG.md                  # Version history
```

## Quality Checklist

Before marking a check complete, verify:

### Code Quality
- [ ] Function follows existing patterns
- [ ] Comprehensive docstring
- [ ] Edge cases handled
- [ ] No syntax errors

### Testing
- [ ] Test file created
- [ ] 4+ test cases
- [ ] Maya script included

### Integration
- [ ] Function signature correct
- [ ] Return format correct
- [ ] Name matches registration

### Documentation
- [ ] CHECKS.md updated
- [ ] Limitations documented
- [ ] Fix instructions provided

### Preview
- [ ] UI preview updated
- [ ] Deployed to Vercel
- [ ] Mobile responsive

## Commit Message Format

```
feat(checks): add <check_name> check (#X/15)

Implement <functionName>() to detect <what it detects>.

Changes:
- Add check function in mayaLint_commands.py
- Register check in mayaLint_list.py under '<category>'
- Add tests in tests/test_<check_id>.py (X test cases)
- Update CHECKS.md with full documentation
- Update UI preview (deployed to Vercel)

Part of Academic Extension - Phase Y, Priority X/15
```

## Check Categories

| Category | Description |
|----------|-------------|
| `naming` | Node naming conventions |
| `general` | General scene/object checks |
| `topology` | Mesh topology issues |
| `UVs` | UV mapping problems |
| `materials` | Material/texture issues (NEW) |
| `scene` | Scene-level settings (NEW) |

## Getting Help

- Review existing checks in `mayaLint_commands.py` for patterns
- Check `CHECKS.md` for documentation examples
- Look at `tests/test_flipped_normals.py` for test structure
- Run `/plan-release` to see algorithm hints

## License

This project is licensed under the MIT License - see the original mayaLint repository for details.
