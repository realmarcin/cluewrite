# Usage Guide: Integrating with Existing Research Projects

## Scenario 1: You Have an Existing Local Git Repo

Let's say you have a research project at `/Users/yourname/research/my-awesome-project/`

### Step 1: Install the Skills Globally (Do Once)

```bash
# Clone this repo to a permanent location (adjust path as needed)
git clone https://github.com/realmarcin/repo-research-writer.git ~/repo-research-writer
# OR clone to wherever you prefer:
# git clone https://github.com/realmarcin/repo-research-writer.git /your/preferred/path

# Run the installer (automatically creates symlinks)
cd ~/repo-research-writer  # or cd /your/preferred/path
./install.sh global
```

**What this does:**
- Creates `~/.claude/skills/` directory
- Creates symbolic links pointing to RRW skills
- Skills are now available in all AI agent sessions

**Benefits**: Skills are available to ALL your projects. Update once, use everywhere.

### Step 2: Prepare Your Research Project

```bash
# Navigate to your project
cd /Users/yourname/research/my-awesome-project

# Run the project setup script
~/repo-research-writer/install.sh setup-project
# OR if you cloned elsewhere: /your/path/to/repo-research-writer/install.sh setup-project

# Edit CLUEWRITE.md with your project details
nano CLUEWRITE.md  # or use your preferred editor
```

**What this does:**
- Creates directory structure (rrw-drafts/, scripts/, figures/, data/)
- Copies CLUEWRITE.md template
- Copies verification scripts
- Creates .gitignore

### Step 3: Add Supporting Scripts

**Note:** If you used `install.sh setup-project`, the scripts are already copied!

The setup script automatically:
- Copies `rrw-verify-stats.py` to `scripts/`
- Copies `rrw-clean-ipynb.py` to `scripts/`
- Makes them executable

**Manual copy (if needed):**
```bash
cp ~/research-writer/scripts/research-writer-verify-stats.py ./scripts/
cp ~/research-writer/scripts/research-writer-clean-ipynb.py ./scripts/
chmod +x scripts/*.py
```

### Step 4: Start Using the Skills

```bash
# Start AI agent in your project directory
cd /Users/yourname/research/my-awesome-project
# Start AI agent
```

In the agent, invoke the skills:

```
"Use the /rrw-plan-manuscript skill to create an outline targeting Nature Methods"

"Use the /rrw-draft-section skill to write the Methods section"

"Use the /rrw-review-manuscript skill to check the draft"
```

## Scenario 2: Installing Per-Project (No Global Installation)

If you prefer project-specific skills:

```bash
cd /Users/yourname/research/my-awesome-project

# Option A: Direct copy
git clone <this-repo-url> temp-skills
mkdir -p .claude/skills
cp -r temp-skills/.claude/skills/* .claude/skills/
rm -rf temp-skills

# Option B: Git submodule (easier to update)
git submodule add <this-repo-url> .claude/scientific-writer
mkdir -p .claude/skills
ln -s ../scientific-writer/.claude/skills/* .claude/skills/
```

## Scenario 3: Multiple Projects Workflow

When you have multiple research projects that all need these skills:

```bash
# Project structure
~/research/
├── project-a/
├── project-b/
└── project-c/

# ONE TIME: Install skills globally
cd ~
git clone <this-repo-url> cluewrite
mkdir -p ~/.claude/skills
ln -s ~/research-writer/.claude/skills/* ~/.claude/skills/

# For each project, just add the necessary structure
for proj in project-a project-b project-c; do
  cd ~/research/$proj
  mkdir -p drafts scripts
  cp ~/research-writer/CLUEWRITE.md.template ./CLUEWRITE.md
  cp ~/research-writer/scripts/*.py ./scripts/
done
```

## Example: Complete Workflow

### Starting from a typical research repo:

```
my-project/
├── data/
│   ├── experiment1.csv
│   └── experiment2.csv
├── notebooks/
│   ├── exploration.ipynb
│   └── analysis.ipynb
├── src/
│   └── analysis.py
├── README.md
└── requirements.txt
```

### After setup:

```bash
cd my-project

# Create structure
mkdir -p drafts scripts figures

# Initialize CLUEWRITE.md
cat > CLUEWRITE.md << 'EOF'
# My Awesome Research Project

## Project Overview
Investigating the effect of X on Y using computational methods.

## Target Journal
PLOS Computational Biology

## Key Findings
1. Finding from experiment1.csv: X shows significant correlation
2. Finding from experiment2.csv: Y demonstrates novel behavior

## Repository Map
- data/experiment1.csv: Experimental data (n=1000 samples)
- notebooks/analysis.ipynb: Statistical analysis
- src/analysis.py: Core computational pipeline
EOF

# Copy verification script
cp ~/research-writer/scripts/research-writer-verify-stats.py ./scripts/

# Start AI agent
# Start AI agent
```

### In Claude session:

```
User: "Use /rrw-plan-manuscript to outline a paper for PLOS Comp Bio"

Claude: Agent: [Analyzes repo, creates manuscript_plan.md]

User: "Use /rrw-draft-section to write the Results section"

Claude: Agent: [Reads relevant data files, generates rrw-drafts/results.md]

User: "Use /rrw-review-manuscript to check it"

Claude: Agent: [Reviews for PLOS compliance, generates review_round_1.md]
```

## Checking Skill Installation

To verify skills are properly installed:

```bash
# Check global skills
ls -la ~/.claude/skills/

# Check project skills
ls -la .claude/skills/

# In AI agent session, list skills
claude  # start session
# Then: "What skills are available?"
```

## Updating Skills

### If using global symlinks:

```bash
cd ~/repo-research-writer
git pull origin main
# All projects automatically get updates
```

### If using git submodules per project:

```bash
cd /path/to/project
git submodule update --remote
```

### If using direct copies:

```bash
# Re-copy the updated skills
cd /path/to/project
rm -rf .claude/skills/rrw-plan-manuscript
rm -rf .claude/skills/rrw-draft-section
rm -rf .claude/skills/rrw-review-manuscript

git clone <this-repo-url> temp-skills
cp -r temp-skills/.claude/skills/* .claude/skills/
rm -rf temp-skills
```

## Troubleshooting

**Skills not found?**
- Check symlinks: `ls -la ~/.claude/skills/`
- Verify SKILL.md exists: `cat ~/.claude/skills/rrw-plan-manuscript/SKILL.md`

**Verification scripts failing?**
- Ensure scripts are executable: `chmod +x scripts/*.py`
- Check Python environment: `python3 --version`
- Install pandas: `pip install pandas openpyxl`

**Skills not activating?**
- Ensure YAML frontmatter is valid in SKILL.md files
- Check AI agent can find the skills directory
- Try restarting AI agent session
