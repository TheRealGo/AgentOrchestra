---
name: agent-orchestra-release
description: Use when releasing AgentOrchestra from the private AgentOrchestra-dev repository to the public AgentOrchestra repository, including version-* release branches, v* tags, compact public release history, GitHub Release updates, release CI mirror checkout, and keeping dev and public release content aligned.
---

# AgentOrchestra Release

Use this Skill only for the project-local release workflow rooted at the
AgentOrchestra development repository checkout.

Repository roles:

- `TheRealGo/AgentOrchestra-dev`: private development repo. Normal
  implementation history lives here.
- `TheRealGo/AgentOrchestra`: public release mirror. Its `main` should stay as a
  compact release history, one commit per public version after `v1.0.0`.

## Release Rules

- Release branches in dev are named `version-x.y.z`.
- Tags in both repos are named `vx.y.z`.
- Public release commits use message `Release vx.y.z`.
- Public release commits must have the same tree as the dev release branch and
  the previous public release commit as parent.
- Use signed commits/tags with the user's configured Git identity.
- Use `--force-with-lease` for public mirror rewrites and tag moves. Never use a
  blind force push.
- Keep local tag refs straight: when pushing public, local `vx.y.z` may point to
  the public release commit; when pushing dev, move it back to the dev release
  branch commit.

## Workflow

1. Confirm the working tree, current branch, remotes, and signing config.
2. Pick the release version and previous public release tag. For `2.0.0`, use:
   - dev branch: `version-2.0.0`
   - release tag: `v2.0.0`
   - previous public release tag: `v1.0.0`
3. Verify the dev release branch content locally:
   `python3 -m unittest discover -s tests` and `git diff --check`.
4. Create or update the public release commit with `git commit-tree -S` using:
   - tree: `version-x.y.z^{tree}`
   - parent: previous public release tag commit
5. Push public `AgentOrchestra` `main`, public `vx.y.z` tag, and GitHub Release.
6. Push dev `version-x.y.z` and dev `vx.y.z` tag.
7. Open or update the `AgentOrchestra-dev` release PR.
8. Verify:
   - public `AgentOrchestra` Actions success
   - dev release PR checks success
   - public `main` commit count is expected
   - `git diff --quiet refs/remotes/public/main version-x.y.z`

## Stable Command Pattern

Use this pattern for ordinary releases. Replace `2.2.0` with the selected
version.

Avoid a plain `git fetch --tags` during release work. Dev and public repos have
same-named release tags that intentionally point at different commits. Fetch
branch refs first, then inspect remote tags with `git ls-remote`:

```sh
git fetch origin '+refs/heads/*:refs/remotes/origin/*'
git fetch public '+refs/heads/*:refs/remotes/public/*'
git ls-remote --tags public 'v2.2.0*'
git ls-remote --heads origin version-2.2.0
git ls-remote --tags origin 'v2.2.0*'
```

Prepare and verify the dev release branch:

```sh
git switch -c version-2.2.0
python3 -m unittest discover -s tests
git diff --check
git add <release files>
git commit -S -m "v2.2.0に変更を反映"
git tag -s -f v2.2.0 -m "v2.2.0" version-2.2.0
git log --show-signature --oneline -1
git tag -v v2.2.0
```

Create the public one-commit release locally. Use `public/main` as the parent
after fetching it; it should be the previous public release commit. Keep a
temporary local branch so verification and push commands are explicit:

```sh
PUBLIC_COMMIT=$(git commit-tree -S version-2.2.0^{tree} -p public/main -m "Release v2.2.0")
git update-ref refs/heads/public-release-v2.2.0 "$PUBLIC_COMMIT"
git tag -s -f v2.2.0 -m "v2.2.0" "$PUBLIC_COMMIT"
git diff --quiet public-release-v2.2.0^{tree} version-2.2.0^{tree}
git rev-list --count public/main..public-release-v2.2.0
```

Push public first. Use `--force-with-lease` only for the public mirror `main`
rewrite/move; never use blind force. Then move the local tag back to the dev
release commit before pushing dev:

```sh
git push public \
  --force-with-lease=refs/heads/main:refs/remotes/public/main \
  public-release-v2.2.0:main \
  refs/tags/v2.2.0:refs/tags/v2.2.0

git update-ref refs/remotes/public/main public-release-v2.2.0
git tag -s -f v2.2.0 -m "v2.2.0" version-2.2.0
git push origin version-2.2.0 refs/tags/v2.2.0:refs/tags/v2.2.0
```

Create the public GitHub Release and the dev release PR. Keep release notes and
PR body concrete: highlights, verification, E2E result when relevant, and the
public release URL.

```sh
gh release create v2.2.0 \
  --repo TheRealGo/AgentOrchestra \
  --target main \
  --title "v2.2.0" \
  --notes "<release notes>"

gh pr create \
  --repo TheRealGo/AgentOrchestra-dev \
  --base main \
  --head version-2.2.0 \
  --title "Release v2.2.0" \
  --body "<summary, verification, public release URL>"
```

Final verification commands:

```sh
git ls-remote --heads public main
git ls-remote --tags public 'v2.2.0*'
git ls-remote --heads origin version-2.2.0
git ls-remote --tags origin 'v2.2.0*'
git diff --quiet refs/remotes/public/main version-2.2.0
git rev-list --count public/main
git log --oneline --first-parent public/main | sed -n '1,8p'
gh run list --repo TheRealGo/AgentOrchestra --branch main --limit 5
gh pr checks <dev-release-pr-number> --repo TheRealGo/AgentOrchestra-dev --watch=false
gh release view v2.2.0 --repo TheRealGo/AgentOrchestra
```

The local `v2.2.0` tag should end the workflow pointing at the dev release
commit. The public remote `v2.2.0` tag should point at the public release commit;
verify remote refs with `git ls-remote --tags public 'v2.2.0*'`.

## CI Quirk

For dev release PRs, the workflow may validate the matching public release tag
instead of using private-repo `actions/checkout`. This is intentional for
`version-*` release branches and avoids transient GitHub `GITHUB_TOKEN` checkout
403s while still verifying the public release content.
