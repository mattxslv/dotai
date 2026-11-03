---
name: setup-copilot-t3
description: Sets up GitHub Copilot as a provider in T3 Code on this machine (Linux or Windows). Use when asked to "set up Copilot in T3", "add GitHub Copilot to T3 Code", or to get Copilot working on a new or home PC.
user-invocable: true
---

# Set up GitHub Copilot in T3 Code

T3 Code runs Copilot through its ACP Registry provider (`driver: acpRegistry`, agent `github-copilot-cli`).
Copilot runs on the machine T3 runs on, so every machine needs its own install and login. Never copy auth files between machines.

## 1. Check Copilot CLI

Run `copilot --version`.

- Missing: install with `npm install -g @github/copilot`. On Windows, `winget install GitHub.Copilot` also works. Confirm with the user before installing.
- Record the absolute path: `which copilot` (Linux/macOS) or `where copilot` (Windows; prefer the `.cmd` or `.exe` entry).

## 2. Check Copilot login

Login is interactive, so the user must do it. Ask them to run `copilot`, then `/login`, using the GitHub account that has the Copilot subscription.
Do not read or print anything under `~/.copilot`.

## 3. Find the T3 data directory

T3 keeps settings in `<T3 home>/userdata/settings.json`. Find the T3 home:

- `T3CODE_HOME` set in the launcher or environment: use that. Check launcher scripts such as `~/bin/t3-*`.
- Otherwise the default is `~/.t3` (Linux) or `%USERPROFILE%\.t3` (Windows).
- Several T3 profiles (for example `~/.t3-personal`, `~/.t3-ai-innov`): the active one has a recently modified `userdata/statev2.sqlite`. Ask the user which profiles they want; it can be more than one.

## 4. Add the provider

Back up `settings.json` first. Then merge this key into the existing JSON object. Keep every other key unchanged; do not replace the file.

```json
"providerInstances": {
  "github-copilot": {
    "driver": "acpRegistry",
    "displayName": "GitHub Copilot",
    "enabled": true,
    "config": {
      "source": "registry",
      "agentId": "github-copilot-cli",
      "commandPath": "<absolute path from step 1>"
    }
  }
}
```

- If `providerInstances` already exists, add `github-copilot` beside the existing entries.
- `commandPath` is optional. Without it, T3 downloads Copilot through `npx`.
- Keep `"source": "registry"`. The `"local"` source does not pass the `--acp` flag Copilot needs, and the settings form cannot add it.
- Codex and Claude are default providers. Adding this entry does not remove them.

Linux example with `jq`. It writes in place, so file permissions are kept:

```bash
F="$T3_HOME/userdata/settings.json"; cp -p "$F" "$F.bak-copilot"
jq --arg cmd "$(command -v copilot)" '.providerInstances = ((.providerInstances // {}) + {"github-copilot": {"driver":"acpRegistry","displayName":"GitHub Copilot","enabled":true,"config":{"source":"registry","agentId":"github-copilot-cli","commandPath":$cmd}}})' "$F" > "$F.tmp" && cat "$F.tmp" > "$F" && rm "$F.tmp"
```

Instead of editing the file, the user can add it in the app: **Settings → Providers → + Add provider → ACP**.
Choose source **ACP Registry**, set agent ID `github-copilot-cli`, and put the path in **Executable override**.

## 5. Verify

T3 watches `settings.json` and reloads it while running. A restart is not needed.

- In the app: **Settings → Providers** shows **GitHub Copilot** with a model list.
- From an agent inside T3: call `orchestrator_capabilities` with `search: "copilot"`. Expect provider `github-copilot`, no constraints, and a non-empty `models` list.
- Unauthenticated or no models: redo step 2, then refresh the provider.
- Not listed: check that `settings.json` is valid JSON (`jq . "$F"`), then check `<T3 home>/userdata/logs/server.trace.ndjson` for `AcpRegistry` errors.

## Rollback

Delete the `github-copilot` entry from `providerInstances`, or restore the backup. You can also remove it in **Settings → Providers**.
