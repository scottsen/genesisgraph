# GenesisGraph Documentation Explorer Guide

**Quick Navigation**: Use the Progressive Reveal CLI to explore documentation incrementally.

## Installation

```bash
cd tools/progressive-reveal-cli
pip install -e .
```

## The 4 Revelation Levels

| Level | Name | Purpose | When to Use |
|-------|------|---------|-------------|
| **0** | Metadata | File stats, size, line count | Quick inventory, decide if relevant |
| **1** | Structure | Headings, sections, organization | Understand document layout |
| **2** | Preview | First lines of each section | Get content overview without full read |
| **3** | Full | Complete content (paged) | Deep dive, search specific content |

## Progressive Documentation Journey

### 🎯 For New Users: Start Here

**1. Understand What GenesisGraph Is**
```bash
# Quick overview
reveal README.md --level 1

# Read key sections
reveal README.md --level 2 --grep "Why GenesisGraph"

# Full introduction
reveal README.md --level 3 --page-size 50
```

**2. Get Started in 5 Minutes**
```bash
# See structure
reveal QUICKSTART.md --level 1

# Preview steps
reveal QUICKSTART.md --level 2

# Follow along
reveal QUICKSTART.md --level 3
```

**3. Explore Real Use Cases**
```bash
# See available use cases
reveal USE_CASES.md --level 1

# Find your industry
reveal USE_CASES.md --level 2 --grep "manufacturing|AI|science"

# Deep dive
reveal USE_CASES.md --level 3 --grep "manufacturing" --context 5
```

**4. Common Questions**
```bash
# See all FAQ topics
reveal FAQ.md --level 1

# Find specific questions
reveal FAQ.md --level 2 --grep "blockchain|PROV-O|performance"

# Read answers
reveal FAQ.md --level 3 --grep "Why not blockchain" --context 10
```

---

### 🛠️ For Developers: Technical Docs

**5. Architecture Overview**
```bash
# System components
reveal docs/developer-guide/architecture.md --level 1

# Component details
reveal docs/developer-guide/architecture.md --level 2

# Implementation patterns
reveal docs/developer-guide/architecture.md --level 3
```

**6. SDK Documentation**
```bash
# SDK guide structure
reveal SDK-DEVELOPMENT-GUIDE.md --level 1

# Quick reference
reveal SDK-QUICK-REFERENCE.md --level 2

# Python examples
reveal sdks/python/README.md --level 2

# JavaScript examples
reveal sdks/javascript/README.md --level 2
```

**7. Feature Guides**
```bash
# Enterprise identity (did:web)
reveal docs/DID_WEB_GUIDE.md --level 2

# Privacy patterns
reveal docs/SELECTIVE_DISCLOSURE.md --level 2

# Transparency logs
reveal docs/TRANSPARENCY_LOG.md --level 2

# Zero-knowledge proofs
reveal docs/ZKP_TEMPLATES.md --level 2

# Industry compliance
reveal docs/PROFILE_VALIDATORS.md --level 2
```

**8. Security**
```bash
# Security considerations
reveal SECURITY.md --level 1

# Audit findings
reveal SECURITY_AUDIT_FINDINGS.md --level 1 --grep "CRITICAL|HIGH"

# Full security review
reveal SECURITY_AUDIT_FINDINGS.md --level 3
```

---

### 📋 For Decision-Makers: Strategic Context

**9. Project Vision**
```bash
# Strategic context
reveal STRATEGIC_CONTEXT.md --level 1

# Vision and roadmap
reveal STRATEGIC_CONTEXT.md --level 2

# 5-year plan
reveal STRATEGIC_CONTEXT.md --level 3 --grep "adoption|market"
```

**10. Current Status & Roadmap**
```bash
# What's implemented
reveal ROADMAP.md --level 1

# Current gaps
reveal ROADMAP.md --level 2 --grep "v1.0|milestone"

# Full roadmap
reveal ROADMAP.md --level 3
```

**11. Critical Analysis**
```bash
# All gaps overview
reveal CRITICAL_GAPS_ANALYSIS.md --level 1

# Critical gaps only
reveal CRITICAL_GAPS_ANALYSIS.md --level 2 --grep "CRITICAL"

# Difficulty analysis
reveal CRITICAL_GAPS_ANALYSIS.md --level 3 --grep "Exceptionally Hard" --context 10
```

---

### 🔬 For Researchers: Specification & Standards

**12. Main Specification**
```bash
# Spec metadata (886 lines!)
reveal spec/MAIN_SPEC.md

# Spec structure
reveal spec/MAIN_SPEC.md --level 1

# Specific sections
reveal spec/MAIN_SPEC.md --level 2 --grep "attestation|verification|disclosure"

# Deep dive
reveal spec/MAIN_SPEC.md --level 3 --grep "cryptographic" --context 5
```

**13. Implementation Details**
```bash
# Implementation summary
reveal IMPLEMENTATION_SUMMARY.md --level 2

# Change history
reveal CHANGELOG.md --level 2
```

---

## Advanced Usage Tips

### Filter by Topic Across Multiple Docs

```bash
# Find all mentions of "selective disclosure"
for doc in *.md; do
  echo "=== $doc ==="
  reveal "$doc" --level 2 --grep "selective disclosure" 2>/dev/null
done
```

### Compare Related Docs

```bash
# Compare SDK documentation
reveal SDK-DEVELOPMENT-GUIDE.md --level 1 > /tmp/sdk-dev.txt
reveal SDK-QUICK-REFERENCE.md --level 1 > /tmp/sdk-ref.txt
diff /tmp/sdk-dev.txt /tmp/sdk-ref.txt
```

### Find Examples

```bash
# Search for YAML examples
reveal README.md --level 3 --grep "```yaml" --context 10

# Search for Python code
reveal SDK-DEVELOPMENT-GUIDE.md --level 3 --grep "def |class " --context 3
```

### Explore by File Size

```bash
# Quick metadata scan
for doc in *.md docs/*.md; do reveal "$doc" 2>/dev/null; done

# Sort by size
for doc in $(find . -name "*.md" | head -20); do
  reveal "$doc" 2>/dev/null | grep "Size (bytes)"
done | sort -t: -k2 -n
```

---

## Common Workflows

### Workflow 1: "I Need to Integrate GenesisGraph"

1. `reveal README.md --level 2` - Understand the basics
2. `reveal QUICKSTART.md --level 3` - Follow tutorial
3. `reveal USE_CASES.md --level 3 --grep "your-industry"` - See relevant examples
4. `reveal SDK-QUICK-REFERENCE.md --level 2` - API overview
5. `reveal docs/developer-guide/troubleshooting.md --level 2` - Common issues

### Workflow 2: "I'm Evaluating GenesisGraph"

1. `reveal README.md --level 1` - High-level structure
2. `reveal FAQ.md --level 3 --grep "why not|vs|comparison"` - Compare alternatives
3. `reveal STRATEGIC_CONTEXT.md --level 2` - Vision and maturity
4. `reveal ROADMAP.md --level 2` - Implementation status
5. `reveal SECURITY_AUDIT_FINDINGS.md --level 1` - Risk assessment

### Workflow 3: "I Want to Contribute"

1. `reveal CONTRIBUTING.md --level 3` - Guidelines
2. `reveal ROADMAP.md --level 2 --grep "TODO|future|planned"` - Open work
3. `reveal CRITICAL_GAPS_ANALYSIS.md --level 2` - High-impact areas
4. `reveal docs/developer-guide/architecture.md --level 2` - System design
5. `reveal SDK-DEVELOPMENT-GUIDE.md --level 3` - Implementation patterns

### Workflow 4: "I'm Writing a Paper"

1. `reveal spec/MAIN_SPEC.md --level 1` - Specification structure
2. `reveal README.md --level 3 --grep "citation|reference"` - How to cite
3. `reveal STRATEGIC_CONTEXT.md --level 3` - Problem space analysis
4. `reveal USE_CASES.md --level 3` - Application domains
5. `reveal CRITICAL_GAPS_ANALYSIS.md --level 3` - Future research directions

---

## Document Inventory

### Root-Level Documents (16 files)

| Priority | Document | Purpose | Lines | Audience |
|----------|----------|---------|-------|----------|
| ⭐⭐⭐ | README.md | Main entry point | 704 | Everyone |
| ⭐⭐⭐ | QUICKSTART.md | 5-minute tutorial | 258 | New users |
| ⭐⭐⭐ | FAQ.md | Common questions | 551 | Evaluators |
| ⭐⭐ | USE_CASES.md | Integration patterns | 467 | Developers |
| ⭐⭐ | ROADMAP.md | Project status | 699 | Contributors |
| ⭐⭐ | SECURITY.md | Security model | 440 | Enterprise |
| ⭐ | STRATEGIC_CONTEXT.md | Vision & strategy | 372 | Decision-makers |
| ⭐ | CRITICAL_GAPS_ANALYSIS.md | Deep analysis | 1574 | Architects |
| ⭐ | IMPROVEMENT_PLAN.md | Tactical roadmap | 1131 | Core team |
| • | CONTRIBUTING.md | Contributor guide | 200 | Contributors |
| • | CHANGELOG.md | Release history | 352 | All users |
| • | SECURITY_AUDIT_FINDINGS.md | Audit results | 583 | Security team |
| • | SDK-DEVELOPMENT-GUIDE.md | SDK architecture | 1045 | SDK devs |
| • | SDK-QUICK-REFERENCE.md | API reference | 350 | SDK users |
| • | IMPLEMENTATION_SUMMARY.md | Status summary | 320 | Trackers |
| • | claude.md | Claude config | 122 | Claude users |

### Feature Documentation (/docs - 8 files)

| Document | Purpose | Lines |
|----------|---------|-------|
| DID_WEB_GUIDE.md | Enterprise identity | 382 |
| SELECTIVE_DISCLOSURE.md | Privacy patterns | 413 |
| TRANSPARENCY_LOG.md | Audit trails | 351 |
| PROFILE_VALIDATORS.md | Industry compliance | 321 |
| ZKP_TEMPLATES.md | Zero-knowledge proofs | 411 |
| developer-guide/architecture.md | System design | 666 |
| developer-guide/troubleshooting.md | Common issues | 267 |
| getting-started/installation.md | Installation | 78 |

### Specification (/spec - 1 file)

| Document | Purpose | Lines |
|----------|---------|-------|
| MAIN_SPEC.md | Complete formal spec | 886 |

---

## Tips for Claude Code Users

When working with Claude Code, use progressive reveal to:

1. **Reduce Context Window Usage**: Start with level 0/1 instead of reading full files
2. **Understand Before Editing**: Use level 1 to see structure before making changes
3. **Targeted Search**: Use `--grep` to find relevant sections without full reads
4. **Verify Changes**: Use level 2 to preview changes without full file reads

### Example Claude Workflow

```bash
# Task: "Update security documentation"

# Step 1: Understand current security docs
reveal SECURITY.md --level 1

# Step 2: Find relevant sections
reveal SECURITY.md --level 2 --grep "threat|attack"

# Step 3: Read specific sections
reveal SECURITY.md --level 3 --grep "threat model" --context 20

# Step 4: Check related docs
reveal SECURITY_AUDIT_FINDINGS.md --level 2 --grep "CRITICAL"

# Step 5: Make targeted edits (now you know exactly what to change)
```

---

## Troubleshooting

### Tool Not Found

```bash
cd /home/user/genesisgraph/tools/progressive-reveal-cli
pip install -e .
```

### Large Files Timeout

```bash
# Use --force for large files
reveal large-file.md --force

# Or start with metadata
reveal large-file.md  # level 0 is always fast
```

### Pattern Not Matching

```bash
# Try case-insensitive (default)
reveal file.md --level 2 --grep "pattern"

# Force case-sensitive if needed
reveal file.md --level 2 --grep "Pattern" --grep-case-sensitive
```

### Want More Context

```bash
# Add context lines around matches
reveal file.md --level 3 --grep "pattern" --context 5
```

---

## Next Steps

1. **Explore the docs**: Start with `reveal README.md --level 1`
2. **Find your path**: Use the workflows above based on your role
3. **Go deep**: Use level 3 + grep when you need details
4. **Share feedback**: This tool is new - let us know how it works!

---

## Related Tools

- **Progressive Reveal CLI**: `/tools/progressive-reveal-cli/README.md`
- **Verification Scripts**: `/scripts/verify_*.py`
- **MkDocs Configuration**: `/mkdocs.yml`

---

*Last Updated: 2025-11-21*
