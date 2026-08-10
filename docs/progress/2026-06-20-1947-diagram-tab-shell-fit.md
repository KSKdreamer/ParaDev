# Diagram Tab Shell Fit

## Summary

Made diagram tabs visibly distinct from normal module tabs and tightened the desktop shell so normal-width windows do not get page-level horizontal overflow.

## Changes

- Added a diagram-tab branch icon and `data-tab-kind="diagram"` marker in the workspace tab strip.
- Added a render regression that checks normal module tabs and diagram tabs are marked separately.
- Constrained the main shell grid to `minmax(0, 1fr)` and changed the app root width to container width so collapsed inspectors/topbars cannot widen the page at 1024px.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/components/Workspace.test.tsx`
- `rtk npm --prefix apps/desktop run build`
- Browser QA on `http://127.0.0.1:5180/`:
  - 1024x768: focus diagram tab renders as `diagram-tab`, has the branch icon, and page overflow is `0`.
  - 1440x900: focus diagram tab remains marked and page overflow is `0`.
  - Console warnings/errors: none.
