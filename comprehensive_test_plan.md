# Comprehensive Test Plan for AutoCommit VSCode Detection Fix

## Test Objectives
- Verify VSCode remote detection works correctly
- Test AutoCommit daemon functionality
- Ensure commits are generated when project is detected as open
- Test edge cases and error handling

## Test Scenarios

### 1. VSCode Detection Tests
- [ ] Test detection when VSCode is connected (current environment)
- [ ] Test detection when VSCode environment variables are missing
- [ ] Test fallback to process-based detection

### 2. AutoCommit Daemon Tests
- [ ] Test daemon startup and status reporting
- [ ] Test commit generation when project is open
- [ ] Test commit skipping when project appears closed
- [ ] Test interval-based scheduling

### 3. Integration Tests
- [ ] Test with actual git repository changes
- [ ] Test with different file types and change types
- [ ] Test error handling for git operations

### 4. Edge Cases
- [ ] Test with multiple projects
- [ ] Test when VSCode disconnects/reconnects
- [ ] Test with different terminal sessions
