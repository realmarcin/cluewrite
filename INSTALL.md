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
git clone https://github.com/realmarcin/cluewrite.git ~/cluewrite

# Option 2: Documents folder
git clone https://github.com/realmarcin/cluewrite.git ~/Documents/cluewrite

# Option 3: Custom location
git clone https://github.com/realmarcin/cluewrite.git /your/custom/path/cluewrite
```

**Important**: Remember where you clone it! You'll need this path for setup.

## Step-by-Step Installation

### Step 1: Clone and Install Globally

```bash
# 1. Clone to your preferred location
git clone https://github.com/realmarcin/cluewrite.git ~/cluewrite

# 2. Navigate to the cloned directory
cd ~/cluewrite

# 3. Run the global installer
./install.sh global
```

**What happens:**
```
Creating symbolic links:
~/.claude/skills/cluewrite-plan-manuscript → ~/cluewrite/.claude/skills/cluewrite-plan-manuscript
~/.claude/skills/cluewrite-draft-section → ~/cluewrite/.claude/skills/cluewrite-draft-section
~/.claude/skills/cluewrite-review-manuscript → ~/cluewrite/.claude/skills/cluewrite-review-manuscript
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
~/cluewrite/install.sh setup-project
```

**If you cloned to a different location:**
```bash
# Use the actual path where you cloned
/your/actual/path/to/cluewrite/install.sh setup-project
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
  ✓ scripts/cluewrite-verify-stats.py
  ✓ scripts/cluewrite-clean-ipynb.py
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
git clone https://github.com/realmarcin/cluewrite.git temp-cluewrite

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
# cluewrite-plan-manuscript -> /path/to/cluewrite/.claude/skills/cluewrite-plan-manuscript
# cluewrite-draft-section -> /path/to/cluewrite/.claude/skills/cluewrite-draft-section
# cluewrite-review-manuscript -> /path/to/cluewrite/.claude/skills/cluewrite-review-manuscript
```

### Check Project Setup

```bash
cd /your/research/project

# Verify structure
ls -d drafts scripts figures data

# Verify files exist
ls CLUEWRITE.md scripts/cluewrite-verify-stats.py scripts/cluewrite-clean-ipynb.py
```

## Common Issues

### "Skills not found" when using AI agent

**Problem**: Symlinks point to wrong location

**Solution**:
```bash
# Check where symlink points
readlink ~/.claude/skills/cluewrite-plan-manuscript

# If path is wrong, re-run from correct location
cd /actual/cluewrite/location
./install.sh global
```

### "install.sh: command not found"

**Problem**: Not in ClueWrite directory

**Solution**:
```bash
# Find where you cloned it
cd ~/cluewrite  # or wherever you cloned

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
cd /new/cluewrite/location

# Re-run installer (updates symlinks)
./install.sh global
```

## Summary

```bash
# ONE TIME (Global Install)
cd /path/to/cluewrite
./install.sh global

# FOR EACH PROJECT
cd /path/to/research/project
/path/to/cluewrite/install.sh setup-project
```

**Key Points**:
- ✅ Clone ClueWrite anywhere you want
- ✅ Use full path to `install.sh` when setting up projects
- ✅ Symlinks mean updates propagate to all projects
- ✅ Each project gets its own `CLUEWRITE.md` and `scripts/`
