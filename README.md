# Verified Software Merge

The script discovers all current documentation files matching:

```text
docs/software*.md
docs/api*.md
docs/deployment*.md
```

It merges them in natural filename order into:

```text
docs/software_merged.md
```

It deliberately does not overwrite `docs/software.md` and does not delete any source file.

It adds a generated clickable table of contents, verifies that removing this table reproduces all source content exactly in the same order, and creates before/after size reports.

Run from the repository root:

```powershell
Expand-Archive -Path "$HOME\Downloads\spy_turtle_merge_software_verified.zip" -DestinationPath . -Force
.\merge_software.ps1
Get-Content .\SOFTWARE_MERGE_REPORT.md
git diff --no-index .\docs\software.md .\docs\software_merged.md
```

The `git diff --no-index` command is optional and only applies if `docs/software.md` already exists.

After review, rename the merged file and remove only the source files listed in the generated report:

```powershell
Move-Item .\docs\software_merged.md .\docs\software.md -Force
Remove-Item .\merge_software.ps1,.\SOFTWARE_MERGE_REPORT.md,.\SOFTWARE_MERGE_REPORT.json
git status
```

Do not delete source documentation until the report and merged document have been checked.
