# Execution boundaries

SkillForge deliberately does **not** execute arbitrary generated scripts. The
script in each generated package is a fixed entrypoint into the reviewed
SkillForge CLI. The variable part is a plain-English browser procedure.

Each attempt creates a temporary Chrome profile and a fresh Chrome process,
binds CDP to loopback, shares that one endpoint between Kane action and analysis,
then terminates the process and removes the profile. No everyday Chrome session
is attached. Kane subprocesses have a wall-clock timeout and their own process
groups, including cleanup on interruption.

This is session isolation, not a host security sandbox. Kane and Chrome run with
the current user's OS permissions. The objective restricts the intended origin,
and the analyzer checks the final origin, but neither prevents all off-origin
network requests. The demo app itself uses `connect-src 'none'` and has no network
calls. Treat browser contents and evidence as untrusted data.

## Optional disposable Linux container

The Dockerfile supplies Python, Kane and Chromium. It is an optional Linux path,
not a container that was tested on the Android development device.

```sh
docker build -t skillforge-kane .
docker run --rm --read-only --cap-drop ALL --security-opt no-new-privileges \
  --tmpfs /tmp:rw,nosuid,nodev,size=512m \
  --tmpfs /home/forge:rw,nosuid,nodev,uid=10001,gid=10001,size=512m \
  skillforge-kane doctor
```

The container runs as UID 10001, has no host directories mounted and no Docker
socket. For an interactive session use `--entrypoint sh -it` with the same flags.
Then start `python3 demo/serve.py` inside that container and use
`python3 forge.py ...` there. Authenticate with `kane-cli login`; keep credentials
in the temporary home. Everything in that home, including the registry, is lost
when the container exits unless you deliberately export it.

Some container hosts cannot run Chromium's own namespace sandbox under these
restrictions. If that occurs, the explicit `SKILLFORGE_CHROME_NO_SANDBOX=1`
environment variable disables the **inner Chrome sandbox**; the outer container
is then the filesystem/process boundary. Do not use that setting on an ordinary
host as a convenience fix. Do not add `--privileged` or mount your home directory.

Kane needs outbound network access to TestMu services. This container does not
provide a domain egress allowlist or a zero-network environment. Such a policy
requires a separately configured network/proxy. Use the synthetic local fixture
for the supplied demo; do not infer permission to access real customer systems.

The registry is an integrity gate for a cooperative owner. Someone who can
replace the verifier binary or rewrite every state/hash file can forge their own
records. The current hashes do not defend against that threat model.
