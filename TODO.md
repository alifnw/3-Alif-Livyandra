# TODO: Fix ValueError in External Data Risk Level Processing

## Approved Plan Implementation Steps (from 03_resource_constrained.ipynb or relevant notebook)

1. [ ] **Locate problematic code block** (Cell ~25): Load df_ext from maternal.csv, rename columns, process 'Risk Level' with map/filter/astype.
2. [ ] **Add debug prints**: Print `df_ext['Risk Level'].value_counts()` before/after filter to confirm 'mid risk' removal and unique values.
3. [ ] **Fix filter logic**: Use original string column for `df_ext = df_ext[df_ext['Risk Level'] != 'mid risk']` before mapping.
4. [ ] **Apply mapping**: `risk = df_ext['Risk Level'].map({'high risk': 1, 'low risk': 0})`.
5. [ ] **Assign & filter**: `df_ext['Risk Level'] = risk.astype(int)`; `df_ext = df_ext[df_ext['Risk Level'].between(0, 1)]`.
6. [ ] **Test cell execution**: Run the cell, confirm no ValueError, print final counts (High: ~?, Total: ?).
7. [ ] **Clean up**: Remove debug prints if confirmed working.
8. [ ] **attempt_completion**: Task complete.

**Current progress**: Plan approved (with file clarification). Next: Implement edits once exact code block confirmed via user or tool.

**Notes**: External data uses lowercase 'high risk'/'low risk'/'mid risk'. Filter must use string comparison before type change.
