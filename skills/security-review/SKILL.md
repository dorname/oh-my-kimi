---
name: security-review
description: Security audit and vulnerability assessment with fix verification
metadata:
  triggers:
  - security review
  - audit security
  - check vulnerabilities
---

# Security Review

Security-focused audit of code, configuration, and architecture, followed by fix verification.

## Use When

- User wants a security audit of code or infrastructure
- User says "security review", "audit security", or "check vulnerabilities"
- Changes involve authentication, authorization, input handling, or data access
- Reviewing dependencies or configuration for security risks

## Do Not Use When

- User wants a general code quality review — use `code-review` instead
- User wants high-level threat modeling for a new system — use `plan` with security focus instead
- The request is purely about compliance paperwork (SOC2, ISO) without code review

## Steps

1. **Explore (Attack Surface Analysis)**: Use `explore` agent to map the attack surface
   - Identify entry points: API endpoints, user inputs, file uploads, external calls
   - Map trust boundaries and authentication/authorization flows
   - Locate sensitive data handling (PII, secrets, credentials)
   - Review dependency files and configuration for known risk patterns

2. **Security Audit**: Use `security-reviewer` agent for deep inspection
   - Check for injection risks (SQL, command, LDAP, XPath)
   - Verify input validation and sanitization
   - Assess authentication and authorization strength
   - Review secret management and hardcoded credentials
   - Evaluate output encoding and XSS prevention
   - Check for insecure dependencies and known CVEs
   - Assess access control and privilege escalation risks

3. **Fix Verification**: Use `code-reviewer` agent to validate proposed fixes
   - Verify fixes address the root cause, not just symptoms
   - Ensure fixes do not introduce regressions or new vulnerabilities
   - Confirm test coverage for security-sensitive paths
   - Provide a final verdict: PASS / PASS WITH NOTES / FAIL

## Output

Security review results include:

- **Executive Summary**: Overall risk level (Critical / High / Medium / Low)
- **Findings**: Each finding includes severity, location, description, and remediation
- **Fix Verification** *(if fixes were proposed)*: Validation of remediation quality
- **Recommendations**: Long-term security hygiene improvements

## Tool Usage

- Use `explore` agent for attack surface mapping
- Use `Agent(subagent_type="security-reviewer", description="Run security audit", ...)` for the primary audit
- Use `Agent(subagent_type="code-reviewer", description="Verify security fixes", ...)` for fix verification
- Use `ReadFile` to inspect code line-by-line
- Use `Grep` to search for dangerous patterns (eval, exec, raw SQL, etc.)
