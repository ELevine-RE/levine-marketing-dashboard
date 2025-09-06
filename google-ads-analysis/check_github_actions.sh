#!/bin/bash

# GitHub Actions Deprecation Checker and Fixer
# This script automatically detects and fixes deprecated GitHub Actions

set -e

echo "🔍 Checking for deprecated GitHub Actions..."
echo "============================================="

# Function to check and fix deprecated actions
check_and_fix_action() {
    local file=$1
    local old_pattern=$2
    local new_pattern=$3
    local description=$4
    
    if grep -q "$old_pattern" "$file"; then
        echo "⚠️  Found deprecated $description in $file"
        echo "   Updating $old_pattern → $new_pattern"
        sed -i.bak "s|$old_pattern|$new_pattern|g" "$file"
        echo "✅ Fixed $description"
        return 0
    else
        echo "✅ $description is up to date in $file"
        return 1
    fi
}

# Check all workflow files
WORKFLOW_FILES=$(find .github/workflows -name "*.yml" 2>/dev/null || true)

if [ -z "$WORKFLOW_FILES" ]; then
    echo "❌ No workflow files found in .github/workflows/"
    exit 1
fi

FIXES_MADE=0

for file in $WORKFLOW_FILES; do
    echo ""
    echo "📄 Checking $file:"
    echo "-------------------"
    
    # Check for deprecated actions
    if check_and_fix_action "$file" "actions/upload-artifact@v3" "actions/upload-artifact@v4" "upload-artifact action"; then
        ((FIXES_MADE++))
    fi
    
    if check_and_fix_action "$file" "actions/cache@v3" "actions/cache@v4" "cache action"; then
        ((FIXES_MADE++))
    fi
    
    if check_and_fix_action "$file" "actions/checkout@v3" "actions/checkout@v4" "checkout action"; then
        ((FIXES_MADE++))
    fi
    
    if check_and_fix_action "$file" "actions/setup-python@v3" "actions/setup-python@v4" "setup-python action"; then
        ((FIXES_MADE++))
    fi
    
    if check_and_fix_action "$file" "peaceiris/actions-gh-pages@v3\"" "peaceiris/actions-gh-pages@v3.9.3\"" "gh-pages action"; then
        ((FIXES_MADE++))
    fi
    
    # Check for other common deprecated patterns
    if check_and_fix_action "$file" "actions/upload-artifact@v2" "actions/upload-artifact@v4" "upload-artifact v2 action"; then
        ((FIXES_MADE++))
    fi
    
    if check_and_fix_action "$file" "actions/cache@v2" "actions/cache@v4" "cache v2 action"; then
        ((FIXES_MADE++))
    fi
done

echo ""
echo "📊 Summary:"
echo "==========="

if [ $FIXES_MADE -eq 0 ]; then
    echo "✅ All GitHub Actions are up to date!"
else
    echo "🔧 Made $FIXES_MADE fixes to deprecated actions"
    echo ""
    echo "📝 Next steps:"
    echo "1. Review the changes: git diff"
    echo "2. Commit the fixes: git add .github/workflows/ && git commit -m 'Update deprecated GitHub Actions'"
    echo "3. Push the changes: git push"
fi

# Clean up backup files
find .github/workflows -name "*.bak" -delete 2>/dev/null || true

echo ""
echo "🎯 Current action versions:"
echo "=========================="
grep -h "@v" .github/workflows/*.yml | sort | uniq
