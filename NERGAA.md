# Nergaa's Press

This fork runs Nergaa Cloud (https://cloud.nergaa.cloud). Branches:

- `master`: Frappe's Press, as it was when the fork was made (not used).
- `nergaa`: **what Nergaa Cloud runs.** Frappe's `master` plus the commits below. Nergaa Cloud's
  `config/platform.yml` (`press.press_repo`, `press.press_branch`, `press.press_ref`) points at it, pinned to a
  tested commit.
- `sync/upstream-YYYY-MM-DD`: a daily scheduled job merges Frappe's `master` into `nergaa` on such a branch and
  opens a pull request. Nothing reaches `nergaa`, or customers, without that PR being reviewed and merged.

## Our changes (keep them small; each one says why)

1. `press/press/doctype/app_release/app_release.py` — `check_python_syntax` compiles in memory and only a real
   syntax error marks a release invalid. `compileall` wrote `__pycache__`, so a full build disk ("No space left
   on device") marked good releases invalid for good ("Invalid release found" on every later deploy).

2. `press/press/doctype/deploy_candidate/deploy_notifications.py`: a build step the kernel killed for memory
   (exit code 137, SIGKILL) is reported as "Build ran out of memory". It used to fall through to "App frontend
   build failed… may be due to issues with the app", which blamed the app for a small build server.

Fixes that still live as runtime patches in nergaa-cloud (`apps/nergaa_cloud/nergaa_cloud/press_fixes.py`) move
here one by one; the patches check whether Press already has the fix, so both can run during the move.

## Syncing with Frappe

```
git fetch upstream master
git checkout -b sync/upstream-$(date +%F) origin/nergaa
git merge upstream/master        # conflicts: keep Frappe's change and re-apply ours on top
```
Then a PR into `nergaa`. Upstream CI runs on it; nergaa-cloud's own suite (`bench run-tests --app nergaa_cloud`)
is the check that matters for us.
