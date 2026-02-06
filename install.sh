#!/bin/bash
# Installation script for ClueWrite Skills

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "ClueWrite Skills - Installation"
echo "=============================================="
echo ""

# Function to install globally
install_global() {
    echo "Installing skills globally to ~/.claude/skills/"

    # Create global skills directory
    mkdir -p ~/.claude/skills

    # Create symlinks
    for skill in cluewrite-plan-manuscript cluewrite-draft-section cluewrite-review-manuscript; do
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
    echo "Skills are now available to all your AI agent projects."
    echo ""
    echo "To use in a project:"
    echo "  cd /path/to/your/research/project"
    echo "  bash $SCRIPT_DIR/install.sh setup-project"
}

# Function to setup a project
setup_project() {
    local project_dir="${1:-.}"

    echo "Setting up project directory structure in: $project_dir"
    echo ""

    cd "$project_dir"

    # Create directories
    echo "Creating directory structure..."
    mkdir -p drafts
    mkdir -p scripts
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
    echo "  ✓ Copying verification scripts to scripts/"
    cp "$SCRIPT_DIR/scripts/cluewrite-verify-stats.py" scripts/
    cp "$SCRIPT_DIR/scripts/cluewrite-clean-ipynb.py" scripts/
    chmod +x scripts/*.py

    # Create .gitignore if it doesn't exist
    if [ ! -f ".gitignore" ]; then
        echo "  ✓ Creating .gitignore"
        cat > .gitignore << 'EOF'
# Drafts and outputs
drafts/
manuscript_plan.md
review_round_*.md
repo_map.md
bib_index.md

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
    for skill in cluewrite-plan-manuscript cluewrite-draft-section cluewrite-review-manuscript; do
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
