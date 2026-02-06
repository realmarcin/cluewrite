#!/bin/bash
# Installation script for Repo Research Writer (RRWrite) Skills

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "Repo Research Writer (RRWrite) Skills - Installation"
echo "=============================================="
echo ""

# Function to install globally
install_global() {
    echo "Installing skills globally to ~/.claude/skills/"

    # Create global skills directory
    mkdir -p ~/.claude/skills

    # Create symlinks
    for skill in rrwrite-plan-manuscript rrwrite-draft-section rrwrite-critique-manuscript rrwrite-research-literature; do
        target=~/.claude/skills/$skill
        if [ -L "$target" ] || [ -e "$target" ]; then
            echo "  ⚠️  Removing existing $skill"
            rm -rf "$target"
        fi
        echo "  ✓ Linking $skill"
        ln -s "$SCRIPT_DIR/.claude/skills/$skill" "$target"
    done

    echo ""
    echo "✅ Global installation complete!"
    echo "Skills are now available globally to all your AI agent sessions."
    echo ""
    echo "📋 Next Step: Setup each research project (once per project)"
    echo ""
    echo "  cd /path/to/your/research/project"
    echo "  bash $SCRIPT_DIR/install.sh setup-project"
    echo ""
    echo "This creates directories and copies PROJECT.md template + scripts."
}

# Function to setup a project
setup_project() {
    local project_dir="${1:-.}"

    echo "Setting up project directory structure in: $project_dir"
    echo ""

    cd "$project_dir"

    # Create directories
    echo "Creating directory structure..."
    mkdir -p manuscript
    mkdir -p manuscript/.rrwrite
    mkdir -p manuscript/runs
    mkdir -p scripts
    mkdir -p schemas
    mkdir -p figures
    mkdir -p data/processed
    mkdir -p data/raw

    # Copy PROJECT.md template if it doesn't exist
    if [ ! -f "PROJECT.md" ]; then
        echo "  ✓ Creating PROJECT.md from template"
        cp "$SCRIPT_DIR/PROJECT.md.template" PROJECT.md
    else
        echo "  ⚠️  PROJECT.md already exists, skipping"
    fi

    # Copy scripts
    echo "  ✓ Copying scripts to scripts/"
    cp "$SCRIPT_DIR/scripts/rrwrite-verify-stats.py" scripts/
    cp "$SCRIPT_DIR/scripts/rrwrite-clean-ipynb.py" scripts/
    cp "$SCRIPT_DIR/scripts/rrwrite-validate-manuscript.py" scripts/
    cp "$SCRIPT_DIR/scripts/rrwrite-state-manager.py" scripts/
    cp "$SCRIPT_DIR/scripts/rrwrite-status.py" scripts/
    chmod +x scripts/*.py

    # Copy schema
    echo "  ✓ Copying manuscript schema to schemas/"
    cp "$SCRIPT_DIR/schemas/manuscript.yaml" schemas/

    # Initialize state file
    echo "  ✓ Initializing state tracking"
    python3 scripts/rrwrite-state-manager.py init --project-name "$(basename "$(pwd)")" > /dev/null 2>&1

    # Create .gitignore if it doesn't exist
    if [ ! -f ".gitignore" ]; then
        echo "  ✓ Creating .gitignore"
        cat > .gitignore << 'EOF'
# Manuscript outputs (optional - you may want to commit these)
manuscript/*.md
manuscript/*.bib
manuscript/*.csv

# State tracking (keep in Git for collaboration)
!manuscript/.rrwrite/
!manuscript/.rrwrite/state.json

# Archived runs (optional: can exclude if large)
# manuscript/runs/

# Python
__pycache__/
*.py[cod]

# OS
.DS_Store
EOF
    fi

    echo ""
    echo "✅ Project setup complete!"
    echo ""
    echo "Next steps:"
    echo "  1. Edit PROJECT.md with your project details"
    echo "  2. Start your AI agent"
    echo "  3. Use the skills: 'Use plan-manuscript to create an outline'"
}

# Function to install to current project only
install_local() {
    echo "Installing skills to current project (.claude/skills/)"

    mkdir -p .claude/skills

    # Copy skills to project
    for skill in rrwrite-plan-manuscript rrwrite-draft-section rrwrite-critique-manuscript rrwrite-research-literature; do
        target=.claude/skills/$skill
        if [ -e "$target" ]; then
            echo "  ⚠️  Removing existing $skill"
            rm -rf "$target"
        fi
        echo "  ✓ Copying $skill"
        cp -r "$SCRIPT_DIR/.claude/skills/$skill" "$target"
    done

    echo ""
    setup_project "."
}

# Main menu
case "${1:-}" in
    global)
        install_global
        ;;
    local)
        install_local
        ;;
    setup-project)
        setup_project "${2:-.}"
        ;;
    *)
        echo "Usage: $0 [global|local|setup-project]"
        echo ""
        echo "Options:"
        echo "  global          - Install skills globally (~/.claude/skills/)"
        echo "                    Recommended for using across multiple projects"
        echo ""
        echo "  local           - Install skills to current project only"
        echo "                    Useful for project-specific customization"
        echo ""
        echo "  setup-project   - Setup project directory structure"
        echo "                    (Assumes skills already installed globally)"
        echo ""
        echo "Examples:"
        echo "  $0 global"
        echo "  $0 local"
        echo "  cd /path/to/project && $0 setup-project"
        ;;
esac
