# Push EI V2 Branch (Bypass Rules)

Branch protection blocks the first push because status checks can't run until the branch exists.

## Quick fix

1. Create a Personal Access Token at https://github.com/settings/tokens  
   - Scopes: `repo` (full control)  
   - You must be a repo admin

2. Run:
   ```bash
   GITHUB_TOKEN=ghp_xxxx python scripts/ci/push_ei_branch_bypass.py
   ```

3. The script will:
   - Add admin bypass to rulesets (or temporarily disable them)
   - Push `codex/ei-v2-hybrid-only-clean`
   - Restore rulesets

4. Open PR: https://github.com/Ahjan108/phoenix_omega_v4.8/compare/main...codex/ei-v2-hybrid-only-clean

## If script fails

- Ensure you're on `codex/ei-v2-hybrid-only-clean` locally
- Ensure the branch has the EI hybrid files committed
- Manually: Settings → Rules → edit ruleset → add yourself to bypass list → push → remove bypass
