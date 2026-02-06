# Repo Research Writer (RRWrite) Installation Guide

## Understanding the Installation

RRWrite uses a **global + per-project** installation model:

1. **Global**: Install skills once to `~/.claude/skills/` (available everywhere)
2. **Per-Project**: Setup each research project with directory structure and tools

## Installation Paths

### Where Can I Clone RRWrite?

You can clone RRWrite anywhere you want! Common choices:

```bash
# Option 1: Home directory (simple)
git clone https://github.com/realmarcin/repo-research-writer.git ~/repo-research-writer

# Option 2: Documents folder
git clone https://github.com/realmarcin/repo-research-writer.git ~/Documents/repo-research-writer

# Option 3: Custom location
git clone https://github.com/realmarcin/repo-research-writer.git /your/custom/path/repo-research-writer
```

**Important**: Remember where you clone it! You'll need this path for setup.

## Step-by-Step Installation

### Step 1: Clone and Install Globally

```bash
# 1. Clone to your preferred location
git clone https://github.com/realmarcin/repo-research-writer.git ~/repo-research-writer

# 2. Navigate to the cloned directory
cd ~/repo-research-writer

# 3. Run the global installer
./install.sh global
```

**What happens:**
```
Creating symbolic links:
~/.claude/skills/rrwrite-plan-manuscript → ~/repo-research-writer/.claude/skills/rrwrite-plan-manuscript
~/.claude/skills/rrwrite-draft-section → ~/repo-research-writer/.claude/skills/rrwrite-draft-section
~/.claude/skills/rrwrite-critique-manuscript → ~/repo-research-writer/.claude/skills/rrwrite-critique-manuscript
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
~/repo-research-writer/install.sh setup-project
```

**If you cloned to a different location:**
```bash
# Use the actual path where you cloned
/your/actual/path/to/repo-research-writer/install.sh setup-project
```

**What happens:**
```
Creating directories:
  ✓ rrwrite-drafts/
  ✓ scripts/
  ✓ figures/
  ✓ data/processed/
  ✓ data/raw/

Copying files:
  ✓ PROJECT.md (template)
  ✓ scripts/rrwrite-verify-stats.py
  ✓ scripts/rrwrite-clean-ipynb.py
  ✓ .gitignore
```

### Step 3: Start Using ClueWrite

```bash
# In your research project, edit PROJECT.md
nano PROJECT.md

# Start your AI agent and use the skills
"Use /rrwrite-plan-manuscript to create an outline"
```

## Alternative: Local Installation

If you want skills **only** in one project (not global):

```bash
cd /path/to/your/research/project

# Copy RRWrite repo temporarily
git clone https://github.com/realmarcin/repo-research-writer.git temp-rrw

# Install locally
cd temp-rrw
./install.sh local

# Clean up
cd ..
rm -rf temp-rrw
```

**Result**: Skills copied to `.claude/skills/` in current project only.

## Verifying Your Installation

### Check Global Skills

```bash
# List global skills
ls -la ~/.claude/skills/

# Should see:
# rrwrite-plan-manuscript -> /path/to/repo-research-writer/.claude/skills/rrwrite-plan-manuscript
# rrwrite-draft-section -> /path/to/repo-research-writer/.claude/skills/rrwrite-draft-section
# rrwrite-critique-manuscript -> /path/to/repo-research-writer/.claude/skills/rrwrite-critique-manuscript
```

### Check Project Setup

```bash
cd /your/research/project

# Verify structure
ls -d drafts scripts figures data

# Verify files exist
ls PROJECT.md scripts/rrwrite-verify-stats.py scripts/rrwrite-clean-ipynb.py
```

## Common Issues

### "Skills not found" when using AI agent

**Problem**: Symlinks point to wrong location

**Solution**:
```bash
# Check where symlink points
readlink ~/.claude/skills/rrwrite-plan-manuscript

# If path is wrong, re-run from correct location
cd /actual/repo-research-writer/location
./install.sh global
```

### "install.sh: command not found"

**Problem**: Not in RRWrite directory

**Solution**:
```bash
# Find where you cloned it
cd ~/repo-research-writer  # or wherever you cloned

# Verify you're in the right place
ls install.sh README.md .claude/

# Then run
./install.sh global
```

### I moved the RRWrite repository

**Problem**: Symlinks are broken

**Solution**:
```bash
# Navigate to new location
cd /new/repo-research-writer/location

# Re-run installer (updates symlinks)
./install.sh global
```

## Summary

```bash
# ONE TIME (Global Install)
cd /path/to/repo-research-writer
./install.sh global

# FOR EACH PROJECT
cd /path/to/research/project
/path/to/repo-research-writer/install.sh setup-project
```

**Key Points**:
- ✅ Clone RRWrite anywhere you want
- ✅ Use full path to `install.sh` when setting up projects
- ✅ Symlinks mean updates propagate to all projects
- ✅ Each project gets its own `PROJECT.md` and `scripts/`
