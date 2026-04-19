---
name: visual-verdict
description: Structured visual QA verdict for screenshot-to-reference comparisons
triggers:
  - "visual verdict"
  - "compare screenshot"
---

# Visual Verdict

Structured visual QA verdict for screenshot-to-reference comparisons.

## Use When

- Comparing generated UI against a reference design
- User says "visual verdict" or wants visual QA
- Need structured assessment of visual fidelity

## Steps

1. **Load reference**: Read the reference image or design spec
2. **Load generated**: Read the generated screenshot
3. **Compare dimensions**: Check size, aspect ratio, layout structure
4. **Compare elements**: Verify all expected elements are present and positioned correctly
5. **Compare styling**: Check colors, fonts, spacing, borders
6. **Score**: Provide numeric score (0-100) and qualitative assessment
7. **Report**: List differences, suggestions, and next actions

## Output Format

```json
{
  "score": 85,
  "passed": true,
  "threshold": 80,
  "reasoning": "Overall layout matches well. Minor differences in font weight and button padding.",
  "differences": [
    "Header font is 2px smaller than reference",
    "Submit button has 4px extra padding"
  ],
  "suggestions": [
    "Adjust header font-size to 24px",
    "Reduce button padding to 12px 24px"
  ],
  "next_actions": [
    "Fix header font size",
    "Fix button padding"
  ]
}
```

## Tool Usage

- Use `ReadMediaFile` for image comparison
- Use `ReadFile` for design spec references
