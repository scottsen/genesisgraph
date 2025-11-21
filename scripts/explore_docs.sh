#!/bin/bash
# GenesisGraph Documentation Explorer
# Systematically reveals all documentation with progressive levels

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if reveal is installed
if ! command -v reveal &> /dev/null; then
    echo -e "${RED}Error: 'reveal' command not found${NC}"
    echo "Install it with: cd tools/progressive-reveal-cli && pip install -e ."
    exit 1
fi

# Function to print section header
print_header() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

# Function to explore a document
explore_doc() {
    local file="$1"
    local level="${2:-0}"
    local description="$3"

    if [ ! -f "$file" ]; then
        echo -e "${RED}File not found: $file${NC}"
        return
    fi

    echo -e "${YELLOW}📄 $description${NC}"
    echo -e "   File: $file"
    echo ""
    reveal "$file" --level "$level" 2>/dev/null || echo -e "${RED}   Error reading file${NC}"
    echo ""
}

# Parse arguments
LEVEL=0
CATEGORY="all"

while [[ $# -gt 0 ]]; do
    case $1 in
        --level)
            LEVEL="$2"
            shift 2
            ;;
        --category)
            CATEGORY="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --level N         Set revelation level (0-3, default: 0)"
            echo "                    0 = metadata, 1 = structure, 2 = preview, 3 = full"
            echo "  --category NAME   Explore specific category (default: all)"
            echo "                    Categories: essential, developer, strategic, features, spec"
            echo "  --help           Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                              # Quick overview (level 0)"
            echo "  $0 --level 1                    # See all document structures"
            echo "  $0 --level 1 --category essential  # Essential docs structures only"
            echo "  $0 --level 2 --category developer  # Developer docs preview"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

cd "$REPO_ROOT"

# Main exploration
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           GenesisGraph Documentation Explorer                        ║${NC}"
echo -e "${GREEN}║           Revelation Level: $LEVEL                                          ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════════╝${NC}"

# Essential Documents
if [ "$CATEGORY" = "all" ] || [ "$CATEGORY" = "essential" ]; then
    print_header "⭐ ESSENTIAL DOCUMENTS - Start Here"

    explore_doc "README.md" "$LEVEL" "Main Entry Point - Project Overview"
    explore_doc "QUICKSTART.md" "$LEVEL" "5-Minute Tutorial - Get Started Fast"
    explore_doc "FAQ.md" "$LEVEL" "Frequently Asked Questions"
    explore_doc "USE_CASES.md" "$LEVEL" "Real-World Integration Patterns"
fi

# Developer Documentation
if [ "$CATEGORY" = "all" ] || [ "$CATEGORY" = "developer" ]; then
    print_header "🛠️  DEVELOPER DOCUMENTATION - Technical Implementation"

    explore_doc "SDK-QUICK-REFERENCE.md" "$LEVEL" "SDK Quick Reference - API Overview"
    explore_doc "SDK-DEVELOPMENT-GUIDE.md" "$LEVEL" "SDK Development Guide - Deep Dive"
    explore_doc "docs/developer-guide/architecture.md" "$LEVEL" "System Architecture"
    explore_doc "docs/developer-guide/troubleshooting.md" "$LEVEL" "Troubleshooting Guide"
    explore_doc "docs/getting-started/installation.md" "$LEVEL" "Installation Instructions"
fi

# Feature Guides
if [ "$CATEGORY" = "all" ] || [ "$CATEGORY" = "features" ]; then
    print_header "🎯 FEATURE GUIDES - Advanced Capabilities"

    explore_doc "docs/DID_WEB_GUIDE.md" "$LEVEL" "DID Web - Enterprise Identity"
    explore_doc "docs/SELECTIVE_DISCLOSURE.md" "$LEVEL" "Selective Disclosure - Privacy Patterns"
    explore_doc "docs/TRANSPARENCY_LOG.md" "$LEVEL" "Transparency Log - Audit Trails"
    explore_doc "docs/PROFILE_VALIDATORS.md" "$LEVEL" "Profile Validators - Industry Compliance"
    explore_doc "docs/ZKP_TEMPLATES.md" "$LEVEL" "Zero-Knowledge Proofs"
fi

# Strategic Documentation
if [ "$CATEGORY" = "all" ] || [ "$CATEGORY" = "strategic" ]; then
    print_header "📊 STRATEGIC DOCUMENTATION - Vision & Planning"

    explore_doc "STRATEGIC_CONTEXT.md" "$LEVEL" "Strategic Context - Vision & 5-Year Roadmap"
    explore_doc "ROADMAP.md" "$LEVEL" "Development Roadmap - Current Status"
    explore_doc "CRITICAL_GAPS_ANALYSIS.md" "$LEVEL" "Critical Gaps Analysis - Path to v1.0"
    explore_doc "IMPROVEMENT_PLAN.md" "$LEVEL" "Improvement Plan - Tactical Roadmap"
fi

# Security Documentation
if [ "$CATEGORY" = "all" ] || [ "$CATEGORY" = "security" ]; then
    print_header "🔒 SECURITY DOCUMENTATION - Enterprise Concerns"

    explore_doc "SECURITY.md" "$LEVEL" "Security Model & Threat Analysis"
    explore_doc "SECURITY_AUDIT_FINDINGS.md" "$LEVEL" "Security Audit Results"
fi

# Specification
if [ "$CATEGORY" = "all" ] || [ "$CATEGORY" = "spec" ]; then
    print_header "📖 SPECIFICATION - Formal Standards"

    explore_doc "spec/MAIN_SPEC.md" "$LEVEL" "Main Specification - Complete Formal Spec (886 lines)"
fi

# Project Metadata
if [ "$CATEGORY" = "all" ] || [ "$CATEGORY" = "meta" ]; then
    print_header "📋 PROJECT METADATA - Reference Information"

    explore_doc "CONTRIBUTING.md" "$LEVEL" "Contributing Guidelines"
    explore_doc "CHANGELOG.md" "$LEVEL" "Change Log - Version History"
    explore_doc "IMPLEMENTATION_SUMMARY.md" "$LEVEL" "Implementation Summary"
fi

# Summary
print_header "✅ EXPLORATION COMPLETE"

echo -e "${GREEN}Next Steps:${NC}"
echo ""
echo "  1. Deep dive into specific docs:"
echo -e "     ${BLUE}reveal README.md --level 3${NC}"
echo ""
echo "  2. Search for specific topics:"
echo -e "     ${BLUE}reveal FAQ.md --level 3 --grep 'blockchain'${NC}"
echo ""
echo "  3. Explore by category:"
echo -e "     ${BLUE}$0 --level 1 --category developer${NC}"
echo ""
echo "  4. Read the exploration guide:"
echo -e "     ${BLUE}reveal DOCUMENT_EXPLORER_GUIDE.md --level 3${NC}"
echo ""
echo -e "${GREEN}For more information: $0 --help${NC}"
echo ""
