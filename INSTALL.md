# ClueWrite Installation Guide

## Understanding the Installation

ClueWrite uses a **global + per-project** installation model:

1. **Global**: Install skills once to `~/.claude/skills/` (available everywhere)
2. **Per-Project**: Setup each research project with directory structure and tools

## Installation Paths

### Where Can I Clone ClueWrite?

You can clone ClueWrite anywhere you want! Common choices:

```bash
# Option 1: Home directory (simple)
git clone https://github.com/realmarcin/research-writer.git ~/research-writer

# Option 2: Documents folder
git clone https://github.com/realmarcin/research-writer.git ~/Documents/research-writer

# Option 3: Custom location
git clone https://github.com/realmarcin/research-writer.git /your/custom/path/research-writer
```

**Important**: Remember where you clone it! You'll need this path for setup.

## Step-by-Step Installation

### Step 1: Clone and Install Globally

```bash
# 1. Clone to your preferred location
git clone https://github.com/realmarcin/research-writer.git ~/research-writer

# 2. Navigate to the cloned directory
cd ~/research-writer

# 3. Run the global installer
./install.sh global
```

**What happens:**
```
Creating symbolic links:
~/.claude/skills/research-writer-plan-manuscript → ~/research-writer/.claude/skills/research-writer-plan-manuscript
~/.claude/skills/research-writer-draft-section → ~/research-writer/.claude/skills/research-writer-draft-section
~/.claude/skills/research-writer-review-manuscript → ~/research-writer/.claude/skills/research-writer-review-manuscript
```

**Verify it worked:**
```bash
ls -la ~/.claude/skills/
# Should show three symlinks (arrows →)
```

### Step 2: Setup Your Research Project

```bash
# Navigate to your research project
cd /path/to/your/research/project

# Run the project setup
~/research-writer/install.sh setup-project
```

**If you cloned to a different location:**
```bash
# Use the actual path where you cloned
/your/actual/path/to/research-writer/install.sh setup-project
```

**What happens:**
```
Creating directories:
  ✓ cluewrite-drafts/
  ✓ scripts/
  ✓ figures/
  ✓ data/processed/
  ✓ data/raw/

Copying files:
  ✓ CLUEWRITE.md (template)
  ✓ scripts/research-writer-verify-stats.py
  ✓ scripts/research-writer-clean-ipynb.py
  ✓ .gitignore
```

### Step 3: Start Using ClueWrite

```bash
# In your research project, edit CLUEWRITE.md
nano CLUEWRITE.md

# Start your AI agent and use the skills
"Use cluewrite-plan-manuscript to create an outline"
```

## Alternative: Local Installation

If you want skills **only** in one project (not global):

```bash
cd /path/to/your/research/project

# Copy ClueWrite repo temporarily
git clone https://github.com/realmarcin/research-writer.git temp-cluewrite

# Install locally
cd temp-cluewrite
./install.sh local

# Clean up
cd ..
rm -rf temp-cluewrite
```

**Result**: Skills copied to `.claude/skills/` in current project only.

## Verifying Your Installation

### Check Global Skills

```bash
# List global skills
ls -la ~/.claude/skills/

# Should see:
# cluewrite-plan-manuscript -> /path/to/research-writer/.claude/skills/research-writer-plan-manuscript
# cluewrite-draft-section -> /path/to/research-writer/.claude/skills/research-writer-draft-section
# cluewrite-review-manuscript -> /path/to/research-writer/.claude/skills/research-writer-review-manuscript
```

### Check Project Setup

```bash
cd /your/research/project

# Verify structure
ls -d drafts scripts figures data

# Verify files exist
ls CLUEWRITE.md scripts/research-writer-verify-stats.py scripts/research-writer-clean-ipynb.py
```

## Common Issues

### "Skills not found" when using AI agent

**Problem**: Symlinks point to wrong location

**Solution**:
```bash
# Check where symlink points
readlink ~/.claude/skills/research-writer-plan-manuscript

# If path is wrong, re-run from correct location
cd /actual/research-writer/location
./install.sh global
```

### "install.sh: command not found"

**Problem**: Not in ClueWrite directory

**Solution**:
```bash
# Find where you cloned it
cd ~/research-writer  # or wherever you cloned

# Verify you're in the right place
ls install.sh README.md .claude/

# Then run
./install.sh global
```

### I moved the ClueWrite repository

**Problem**: Symlinks are broken

**Solution**:
```bash
# Navigate to new location
cd /new/research-writer/location

# Re-run installer (updates symlinks)
./install.sh global
```

## Summary

```bash
# ONE TIME (Global Install)
cd /path/to/research-writer
./install.sh global

# FOR EACH PROJECT
cd /path/to/research/project
/path/to/research-writer/install.sh setup-project
```

**Key Points**:
- ✅ Clone ClueWrite anywhere you want
- ✅ Use full path to `install.sh` when setting up projects
- ✅ Symlinks mean updates propagate to all projects
- ✅ Each project gets its own `CLUEWRITE.md` and `scripts/`
