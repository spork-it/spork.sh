#!/bin/sh
set -eu

INSTALLER=${INSTALLER:-static/install}
SANDBOX=$(mktemp -d)
trap 'rm -rf "$SANDBOX"' 0 1 2 15

fail() {
    printf '%s\n' "installer test failed: $*" >&2
    exit 1
}

FAKE_BIN="$SANDBOX/fake-bin"
mkdir -p "$FAKE_BIN"
cat >"$FAKE_BIN/python3" <<'PYTHON'
#!/bin/sh
set -eu

if [ "$#" -ge 2 ] && [ "$1" = "-I" ] && [ "$2" = "-c" ]; then
    exit 0
fi

if [ "$#" -eq 4 ] && [ "$1" = "-I" ] && [ "$2" = "-m" ] && [ "$3" = "venv" ]; then
    target=$4
    mkdir -p "$target/bin"
    cat >"$target/bin/python" <<'VENV_PYTHON'
#!/bin/sh
set -eu
case "$*" in
    *importlib.metadata*) printf '%s\n' "9.9.9" ; exit 0 ;;
    *spork-lang*)
        if [ "${FAIL_SPORK_INSTALL:-0}" = "1" ]; then
            exit 23
        fi
        exit 0 ;;
    *" -m pip "*) exit 0 ;;
esac
exit 1
VENV_PYTHON
    cat >"$target/bin/spork" <<'SPORK'
#!/bin/sh
printf '%s\n' "fake spork"
SPORK
    chmod +x "$target/bin/python" "$target/bin/spork"
    exit 0
fi

exit 1
PYTHON
chmod +x "$FAKE_BIN/python3"

make_old_install() {
    home=$1
    mkdir -p "$home/.spork/venv/bin" "$home/.local/bin"
    printf '%s\n' "old installation" >"$home/.spork/venv/old-marker"
    cat >"$home/.spork/venv/bin/spork" <<'OLD_SPORK'
#!/bin/sh
printf '%s\n' "old spork"
OLD_SPORK
    chmod +x "$home/.spork/venv/bin/spork"
    ln -s "$home/.spork/venv/bin/spork" "$home/.local/bin/spork"
}

# A successful update removes the old environment and installs a fresh one.
SUCCESS_HOME="$SANDBOX/success-home"
mkdir -p "$SUCCESS_HOME"
SUCCESS_REAL=$(CDPATH= cd -P "$SUCCESS_HOME" && pwd -P)
make_old_install "$SUCCESS_HOME"
HOME="$SUCCESS_HOME" PATH="$FAKE_BIN:$PATH" sh "$INSTALLER" \
    >"$SANDBOX/success.out" 2>"$SANDBOX/success.err"
[ ! -e "$SUCCESS_HOME/.spork/venv/old-marker" ] || fail "old environment was retained"
[ -x "$SUCCESS_HOME/.spork/venv/bin/spork" ] || fail "new command is missing"
[ -L "$SUCCESS_HOME/.local/bin/spork" ] || fail "launcher is not a symlink"
[ "$(readlink "$SUCCESS_HOME/.local/bin/spork")" = \
  "$SUCCESS_REAL/.spork/venv/bin/spork" ] || fail "launcher target is incorrect"
find "$SUCCESS_HOME/.spork" -name 'venv.backup.*' -print | grep . && \
    fail "successful update retained a backup"
grep -q 'Spork 9.9.9 installed successfully' "$SANDBOX/success.out" || \
    fail "installed version was not reported"

# A failed package installation restores the complete previous environment.
ROLLBACK_HOME="$SANDBOX/rollback-home"
mkdir -p "$ROLLBACK_HOME"
make_old_install "$ROLLBACK_HOME"
if HOME="$ROLLBACK_HOME" PATH="$FAKE_BIN:$PATH" FAIL_SPORK_INSTALL=1 \
    sh "$INSTALLER" >"$SANDBOX/rollback.out" 2>"$SANDBOX/rollback.err"; then
    fail "failed package installation returned success"
fi
[ -f "$ROLLBACK_HOME/.spork/venv/old-marker" ] || \
    fail "previous environment was not restored"
[ -L "$ROLLBACK_HOME/.local/bin/spork" ] || \
    fail "previous launcher was not retained"
find "$ROLLBACK_HOME/.spork" -name 'venv.backup.*' -print | grep . && \
    fail "rollback retained a backup"
grep -q 'previous Spork installation was restored' "$SANDBOX/rollback.err" || \
    fail "rollback was not reported"

# A non-symlink launcher is never overwritten, and checking it happens before
# the existing environment is moved.
CONFLICT_HOME="$SANDBOX/conflict-home"
mkdir -p "$CONFLICT_HOME/.spork/venv" "$CONFLICT_HOME/.local/bin"
printf '%s\n' "keep me" >"$CONFLICT_HOME/.spork/venv/old-marker"
printf '%s\n' "unrelated command" >"$CONFLICT_HOME/.local/bin/spork"
if HOME="$CONFLICT_HOME" PATH="$FAKE_BIN:$PATH" sh "$INSTALLER" \
    >"$SANDBOX/conflict.out" 2>"$SANDBOX/conflict.err"; then
    fail "non-symlink launcher conflict returned success"
fi
[ "$(cat "$CONFLICT_HOME/.local/bin/spork")" = "unrelated command" ] || \
    fail "non-symlink launcher was overwritten"
[ -f "$CONFLICT_HOME/.spork/venv/old-marker" ] || \
    fail "environment changed before launcher conflict was rejected"

# A symbolic-link installation root is rejected without touching its target.
SYMLINK_HOME="$SANDBOX/symlink-home"
VICTIM="$SANDBOX/victim"
mkdir -p "$SYMLINK_HOME" "$VICTIM/venv"
printf '%s\n' "do not delete" >"$VICTIM/venv/marker"
ln -s "$VICTIM" "$SYMLINK_HOME/.spork"
if HOME="$SYMLINK_HOME" PATH="$FAKE_BIN:$PATH" sh "$INSTALLER" \
    >"$SANDBOX/symlink.out" 2>"$SANDBOX/symlink.err"; then
    fail "symbolic-link installation root returned success"
fi
[ -f "$VICTIM/venv/marker" ] || fail "symbolic-link target was modified"

printf '%s\n' "installer safety tests passed"
