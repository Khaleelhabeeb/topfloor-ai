#!/bin/bash

# Script to manually test Alembic migrations up and down
# This tests that migrations can be applied and reverted successfully

set -e  # Exit on error

echo "========================================="
echo "Testing Alembic Migrations Up and Down"
echo "========================================="
echo ""

# Check current migration state
echo "1. Checking current migration state..."
alembic current
echo ""

# Upgrade to head
echo "2. Upgrading to head..."
alembic upgrade head
echo ""

# Check current state after upgrade
echo "3. Verifying we're at head..."
alembic current
echo ""

# Show migration history
echo "4. Showing migration history..."
alembic history
echo ""

# Downgrade one step
echo "5. Downgrading one step (to 4ff9d7947698)..."
alembic downgrade 4ff9d7947698
echo ""

# Check current state after downgrade
echo "6. Verifying downgrade..."
alembic current
echo ""

# Upgrade back to head
echo "7. Upgrading back to head..."
alembic upgrade head
echo ""

# Final verification
echo "8. Final verification - should be at head..."
alembic current
echo ""

# Downgrade to base (optional - commented out to preserve data)
# echo "9. Testing full downgrade to base..."
# alembic downgrade base
# echo ""
# echo "10. Verifying at base..."
# alembic current
# echo ""
# echo "11. Upgrading back to head..."
# alembic upgrade head
# echo ""

echo "========================================="
echo "✅ Migration tests completed successfully!"
echo "========================================="
