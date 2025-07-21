#!/bin/bash
# run_tests.sh - Test runner script for CourtListener MCP Server

set -e  # Exit on any error

# Change to the project root directory (parent of tests/)
cd "$(dirname "$0")/.."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📋 CourtListener MCP Server Test Suite${NC}"
echo "========================================="
echo "🗂️  Working directory: $(pwd)"

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "🐍 Python version: ${python_version}"

# Check if virtual environment exists
if [[ -z "${VIRTUAL_ENV}" ]]; then
    echo -e "${YELLOW}⚠️  No virtual environment detected. Consider using one.${NC}"
fi

# Check for API token
if [[ -z "${COURTLISTENER_API_TOKEN}" ]]; then
    echo -e "${YELLOW}⚠️  COURTLISTENER_API_TOKEN not set${NC}"
    echo "   Get your token from: https://www.courtlistener.com/profile/tokens/"
    echo "   Set it with: export COURTLISTENER_API_TOKEN=your_token_here"
    echo ""
fi

# Check dependencies
echo "📦 Checking dependencies..."
if ! python3 -c "import httpx, mcp" 2>/dev/null; then
    echo -e "${RED}❌ Missing dependencies. Installing...${NC}"
    pip install -r requirements.txt
fi

# Create test results directory
mkdir -p test_results
timestamp=$(date +"%Y%m%d_%H%M%S")

# Function to run a test and capture results
run_test() {
    local test_name="$1"
    local test_command="$2"
    local output_file="test_results/${test_name}_${timestamp}.json"
    
    echo ""
    echo -e "${BLUE}🧪 Running ${test_name}...${NC}"
    echo "Command: ${test_command}"
    
    if eval "${test_command} --output ${output_file}"; then
        echo -e "${GREEN}✅ ${test_name} completed successfully${NC}"
        return 0
    else
        echo -e "${RED}❌ ${test_name} failed${NC}"
        return 1
    fi
}

# Test execution
failed_tests=0
total_tests=0

# Basic functionality tests
((total_tests++))
if ! run_test "basic_functionality" "python3 tests/mcp_test_runner.py --mode basic"; then
    ((failed_tests++))
fi

# Integration workflow tests  
((total_tests++))
if ! run_test "integration_workflows" "python3 tests/mcp_test_runner.py --mode integration"; then
    ((failed_tests++))
fi

# Single tool tests (examples)
test_cases=(
    "get_court:'{\"court_id\": \"scotus\"}'"
    "search_legal_cases:'{\"query\": \"privacy rights\", \"limit\": 5}'"
    "verify_citations:'{\"volume\": \"576\", \"reporter\": \"U.S.\", \"page\": \"644\"}'"
)

for case in "${test_cases[@]}"; do
    IFS=':' read -r tool_name params <<< "$case"
    ((total_tests++))
    if ! run_test "single_${tool_name}" "python3 tests/mcp_test_runner.py --mode single --tool ${tool_name} --params '${params}'"; then
        ((failed_tests++))
    fi
done

# Performance test (run basic tests multiple times)
echo ""
echo -e "${BLUE}⚡ Running performance test...${NC}"
start_time=$(date +%s)

for i in {1..3}; do
    echo "  Performance run $i/3..."
    python3 tests/mcp_test_runner.py --mode basic --output "test_results/perf_run_${i}_${timestamp}.json" >/dev/null 2>&1
done

end_time=$(date +%s)
duration=$((end_time - start_time))
echo -e "${GREEN}✅ Performance test completed in ${duration}s${NC}"

# Generate comprehensive test report
echo ""
echo -e "${BLUE}📊 Generating comprehensive test report...${NC}"

cat > "test_results/test_summary_${timestamp}.md" << EOF
# CourtListener MCP Server Test Report

**Generated:** $(date)
**Python Version:** ${python_version}
**API Token:** $(if [[ -n "${COURTLISTENER_API_TOKEN}" ]]; then echo "Available"; else echo "Not Set"; fi)

## Test Summary

- **Total Tests:** ${total_tests}
- **Passed:** $((total_tests - failed_tests))
- **Failed:** ${failed_tests}
- **Success Rate:** $(echo "scale=1; $((total_tests - failed_tests)) * 100 / ${total_tests}" | bc)%

## Test Results

### Basic Functionality Tests
- Location: \`test_results/basic_functionality_${timestamp}.json\`
- Purpose: Verify all 16 tools work with basic parameters

### Integration Workflow Tests  
- Location: \`test_results/integration_workflows_${timestamp}.json\`
- Purpose: Test realistic legal research workflows

### Single Tool Tests
- Purpose: Validate specific tool functionality with various parameters

$(for case in "${test_cases[@]}"; do
    IFS=':' read -r tool_name params <<< "$case"
    echo "- ${tool_name}: \`test_results/single_${tool_name}_${timestamp}.json\`"
done)

### Performance Tests
- Duration: ${duration} seconds for 3 runs
- Files: \`test_results/perf_run_*_${timestamp}.json\`

## Recommendations

$(if [[ ${failed_tests} -eq 0 ]]; then
    echo "🎉 **All tests passed!** The CourtListener MCP Server is working correctly."
else
    echo "⚠️ **${failed_tests} test(s) failed.** Review the individual test results for details."
fi)

$(if [[ -z "${COURTLISTENER_API_TOKEN}" ]]; then
    echo ""
    echo "### API Token Setup"
    echo "Some tests may have limited functionality without an API token."
    echo "Get your token from: https://www.courtlistener.com/profile/tokens/"
fi)

## Next Steps

1. Review individual test result files for detailed information
2. For failed tests, check the error messages and fix any issues
3. Run \`python3 tests/test_courtlistener_mcp.py\` for the comprehensive evaluation suite
4. Consider setting up continuous integration with these tests

## Files Generated

\`\`\`
test_results/
├── test_summary_${timestamp}.md (this file)
├── basic_functionality_${timestamp}.json
├── integration_workflows_${timestamp}.json
$(for case in "${test_cases[@]}"; do
    IFS=':' read -r tool_name params <<< "$case"
    echo "├── single_${tool_name}_${timestamp}.json"
done)
└── perf_run_*_${timestamp}.json
\`\`\`
EOF

# Final summary
echo ""
echo "========================================="
echo -e "${BLUE}📋 TEST EXECUTION COMPLETE${NC}"
echo "========================================="
echo "Total Tests: ${total_tests}"
echo -e "Passed: ${GREEN}$((total_tests - failed_tests))${NC}"
echo -e "Failed: ${RED}${failed_tests}${NC}"

if [[ ${failed_tests} -eq 0 ]]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED!${NC}"
    echo -e "📄 Test report: ${GREEN}test_results/test_summary_${timestamp}.md${NC}"
    exit 0
else
    echo -e "${RED}❌ ${failed_tests} TEST(S) FAILED${NC}"
    echo -e "📄 Test report: ${YELLOW}test_results/test_summary_${timestamp}.md${NC}"
    echo "Review individual test files for details."
    exit 1
fi

# Additional test configuration
# pytest.ini
cat > pytest.ini << 'EOF'
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    --color=yes
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
    requires_token: marks tests that require API token
EOF

# .env.test template
cat > .env.test << 'EOF'
# Test Configuration for CourtListener MCP Server
# Copy this file to .env and fill in your values

# Required: Your CourtListener API token
COURTLISTENER_API_TOKEN=your_token_here

# Optional: Test configuration
TEST_MODE=full
MCP_TRANSPORT=stdio
MCP_LOG_FILE=true

# Optional: Custom API base URL (for testing against different environments)
# COURTLISTENER_BASE_URL=https://www.courtlistener.com/api/rest/v4

# Test data overrides (optional)
# TEST_OPINION_ID=11063335
# TEST_CLUSTER_ID=123456
# TEST_DOCKET_ID=65663213
# TEST_PERSON_ID=8521
EOF

echo ""
echo -e "${BLUE}📁 Additional test files created:${NC}"
echo "   • pytest.ini - Pytest configuration"
echo "   • .env.test - Test environment template"
echo ""
echo -e "${YELLOW}💡 To run the comprehensive evaluation suite:${NC}"
echo "   python3 tests/test_courtlistener_mcp.py"
echo ""
echo -e "${YELLOW}💡 To run individual tool tests:${NC}"
echo "   python3 tests/mcp_test_runner.py --mode single --tool get_court --params '{\"court_id\": \"scotus\"}'"