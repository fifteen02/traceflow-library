# Searches for a skill review

Run each with `grep`, `path` set to the skill's folder (`skills-to-review/<name>`), `ignoreCase` on. A match is a place to read, not a finding: read the line in its file and say what it does.

## The network

- Web addresses: `https?://[^\s"')]+`
- Programs that download: `\b(curl|wget|nc|ncat|netcat|ssh|scp|rsync|ftp)\b`
- Python's web and sockets: `\b(requests|httpx|urllib|aiohttp|socket|http\.client|websocket)\b`
- JavaScript's: `\b(fetch|axios|XMLHttpRequest|WebSocket|https?\.request)\b`
- Addresses by number: `\b\d{1,3}(\.\d{1,3}){3}\b`

For each address, say what is sent there: a file, the workspace's contents, a setting, nothing.

## Running things

- Python running commands: `\b(subprocess|os\.system|os\.popen|os\.exec|pty\.spawn)\b`
- Code built at run time: `\b(eval|exec|compile|__import__|importlib)\s*\(`
- JavaScript's: `\b(child_process|execSync|spawn|new Function)\b`
- Shell piping a download into a shell: `(curl|wget)[^|]*\|\s*(ba|z)?sh`
- Hidden text: `\b(base64|b64decode|atob|fromCharCode|codecs\.decode|zlib\.decompress)\b`
- Long encoded strings: `[A-Za-z0-9+/=]{120,}`

Encoded text that is decoded and then run is a reason not to install.

## Settings and secrets

- Environment variables read: `\b(os\.environ|os\.getenv|getenv|process\.env|\$\{?[A-Z_]{3,})`
- Secrets by name: `(api[_-]?key|token|secret|password|passwd|credential|bearer)`
- Keys written into a file: `(sk-[A-Za-z0-9]{16,}|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{30,}|-----BEGIN [A-Z ]*PRIVATE KEY)`

Compare what is read with the header's `requires.env`. A key written into a file of the skill is a finding even when it looks like an example.

## Installing

- Packages installed while it runs: `\b(pip3? install|uv pip|npm (i|install)|npx|yarn add|apt(-get)? install|brew install|gem install|go install|cargo install)\b`
- The header's needs: `^\s*(bins|env|primaryEnv|tools|requires):`

traceflow installs only what the header and the requirements file declare, once, at install. A script that installs something itself is a finding.

## Reaching outside its folder

- Home and system paths: `(~/|\$HOME|/home/|/root|/etc/|/var/|/usr/|/tmp/|\.\./)`
- Keys and logins: `(\.ssh|id_rsa|\.aws|\.config|\.netrc|\.git-credentials|keychain|\.env\b)`
- Deleting or changing files: `\b(rm -rf|shutil\.rmtree|os\.remove|unlink|chmod|chown)\b`
- Reading the whole workspace: `(os\.walk|glob\.glob\(['"]/|\*\*/\*)`

## Text aimed at the agent

- Overriding its rules: `(ignore (all |any |the )?(previous|prior|above)|disregard|you are now|system prompt|developer mode)`
- Acting without asking: `(without asking|don't ask|do not ask|no need to confirm|silently|automatically (send|share|delete|install))`
- Hiding what it does: `(don't (tell|mention)|do not (tell|mention|reveal)|keep this secret|hide)`
