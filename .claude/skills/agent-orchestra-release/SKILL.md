---
name: agent-orchestra-release
description: Use when releasing AgentOrchestra from the private AgentOrchestra-dev repository to the public AgentOrchestra repository, including version-* release branches, v* tags, compact public release history, GitHub Release updates, release CI mirror checkout, and keeping dev and public release content aligned.
---

# AgentOrchestra Release

Use this Skill only for the project-local release workflow rooted at
`${AGENT_ORCHESTRA_DEV_ROOT}`.

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
   `python3 -m unittest discover -s tests_claude` and `git diff --check`.
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

## CI Quirk

For dev release PRs, the workflow may validate the matching public release tag
instead of using private-repo `actions/checkout`. This is intentional for
`version-*` release branches and avoids transient GitHub `GITHUB_TOKEN` checkout
403s while still verifying the public release content.
