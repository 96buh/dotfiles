#!/usr/bin/env python3
"""Remote TeX preview: manual builds, SSH snapshots, Skim and Neovim."""
import argparse
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shlex
import socket
import stat
import subprocess
import sys
import tarfile
import tempfile
import time
import uuid


def atomic(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + '.' + uuid.uuid4().hex)
    try:
        tmp.write_bytes(data)
        tmp.replace(path)
    finally:
        tmp.unlink(missing_ok=True)


def put_json(path, value):
    atomic(path, json.dumps(value, ensure_ascii=False).encode())


def get_json(path, default=None):
    return json.loads(Path(path).read_text()) if Path(path).exists() else default


def cache_base():
    base = Path(os.environ.get('XDG_CACHE_HOME', str(Path.home() / '.cache')))
    return base / 'remote-tex-preview'


def cache(root):
    key = hashlib.sha256(str(Path(root).resolve()).encode()).hexdigest()[:24]
    return cache_base() / key


def register(root, socket):
    root = str(Path(root).resolve())
    key = hashlib.sha256(socket.encode()).hexdigest()[:24]
    put_json(cache(root) / 'sessions' / (key + '.json'), {'root': root, 'socket': socket})


def project_status(root):
    state = cache(root)
    return {'root': str(root), 'latest': get_json(state / 'latest.json'),
            'forward': get_json(state / 'forward.json')}


def discover():
    """Only advertise projects with a still-existing Neovim Unix socket."""
    roots = set()
    for path in cache_base().glob('*/sessions/*.json'):
        try:
            session = get_json(path)
            if stat.S_ISSOCK(Path(session['socket']).stat().st_mode):
                with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
                    connection.settimeout(0.15)
                    connection.connect(session['socket'])
                roots.add(session['root'])
        except (OSError, ValueError, KeyError):
            continue
    return [project_status(root) for root in sorted(roots)]


def inside(path, root):
    path, root = Path(path).resolve(), Path(root).resolve()
    path.relative_to(root)
    return path


def inputs(data, root):
    found = {}
    for line in gzip.decompress(data).splitlines():
        match = re.match(rb'Input:(\d+):(.*)', line)
        if match:
            name = os.fsdecode(match[2])
            path = Path(name)
            if not path.is_absolute():
                path = Path(root) / path
            try:
                found[name] = str(inside(path, root).relative_to(Path(root).resolve()))
            except ValueError:
                pass  # TeX distribution files are not project sources.
    return found


def publish(root, pdf, socket):
    root = Path(root).resolve()
    pdf = inside(pdf, root)
    sync = pdf.with_suffix('.synctex.gz')
    before = [(p.stat().st_mtime_ns, p.stat().st_size) for p in (pdf, sync)]
    pdf_data, sync_data = pdf.read_bytes(), sync.read_bytes()
    after = [(p.stat().st_mtime_ns, p.stat().st_size) for p in (pdf, sync)]
    if before != after:
        raise ValueError('Build files changed during publication; publish again after compilation')
    if not pdf_data.startswith(b'%PDF-') or b'%%EOF' not in pdf_data[-4096:]:
        raise ValueError('PDF is incomplete')
    # minted records generated .minted inputs in SyncTeX, including config files
    # that it removes before the successful compile callback runs. They are not
    # editable project sources. Keep their SyncTeX tags, but do not snapshot them.
    mapping = {name: rel for name, rel in inputs(sync_data, root).items()
               if not rel.endswith('.minted')}
    if not mapping:
        raise ValueError('No project sources in SyncTeX; root must be the compile working directory')
    files = {str(pdf.relative_to(root)): pdf_data,
             str(sync.relative_to(root)): sync_data}
    for rel in set(mapping.values()):
        files[rel] = (root / rel).read_bytes()
    manifest = {'generation': uuid.uuid4().hex, 'root': str(root),
                'pdf': str(pdf.relative_to(root)), 'synctex': str(sync.relative_to(root)),
                'inputs': mapping, 'socket': socket,
                'files': {rel: hashlib.sha256(data).hexdigest() for rel, data in files.items()}}
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode='w:gz') as archive:
        for rel, data in files.items():
            info = tarfile.TarInfo(rel)
            info.size = len(data)
            archive.addfile(info, io.BytesIO(data))
        data = json.dumps(manifest).encode()
        info = tarfile.TarInfo('rtp-manifest.json')
        info.size = len(data)
        archive.addfile(info, io.BytesIO(data))
    state = cache(root)
    atomic(state / (manifest['generation'] + '.tar.gz'), buf.getvalue())
    put_json(state / 'latest.json', manifest)
    register(root, socket)
    # Bound storage; an in-flight fetch of an expired snapshot is retried.
    for old in sorted(state.glob('*.tar.gz'), key=lambda p: p.stat().st_mtime, reverse=True)[3:]:
        old.unlink(missing_ok=True)
    return manifest


def forward(root, file, line, socket):
    root = Path(root).resolve()
    file = inside(file, root)
    if line < 1:
        raise ValueError('Line numbers start at 1')
    put_json(cache(root) / 'forward.json', {'id': uuid.uuid4().hex,
             'file': str(file.relative_to(root)), 'line': line, 'socket': socket,
             'generation': (get_json(cache(root) / 'latest.json', {}) or {}).get('generation')})


def rewrite_synctex(data, mapping, local_root):
    """Rewrite Input records and byte-distance anchors, without changing node tags."""
    output = bytearray()
    old_pos = new_anchor = old_anchor = 0
    for line in gzip.decompress(data).splitlines(keepends=True):
        original = line
        m = re.match(rb'Input:(\d+):(.*?)(\r?\n)?$', line)
        if m and os.fsdecode(m[2]) in mapping:
            target = Path(local_root) / mapping[os.fsdecode(m[2])]
            line = b'Input:' + m[1] + b':' + os.fsencode(target) + b'\n'
        elif re.match(rb'!\d+\s*$', line):
            # Preserve the original anchor convention, including any fixed bias.
            distance = int(line[1:].strip())
            bias = distance - (old_pos - old_anchor)
            line = b'!' + str(len(output) - new_anchor + bias).encode() + b'\n'
            old_anchor, new_anchor = old_pos, len(output)
        output.extend(line)
        old_pos += len(original)
    return gzip.compress(bytes(output))


def install_bundle(data, destination):
    destination = Path(destination).expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destination.parent) as stage:
        stage = Path(stage)
        with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as archive:
            for member in archive.getmembers():
                if not member.isfile() or Path(member.name).is_absolute() or '..' in Path(member.name).parts:
                    raise ValueError('Unsafe snapshot member')
                target = stage / member.name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.extractfile(member).read())
        manifest = get_json(stage / 'rtp-manifest.json')
        for rel, digest in manifest['files'].items():
            path = inside(stage / rel, stage)
            if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
                raise ValueError('Snapshot checksum mismatch: ' + rel)
        sync = inside(stage / manifest['synctex'], stage)
        sync.write_bytes(rewrite_synctex(sync.read_bytes(), manifest['inputs'], destination))
        # Sources and SyncTeX first; PDF last is the viewer's commit point.
        for rel in [p for p in manifest['files'] if p != manifest['pdf']] + [manifest['pdf']]:
            target = inside(destination / rel, destination)
            atomic(target, (stage / rel).read_bytes())
        put_json(destination / 'rtp-manifest.json', manifest)
    return manifest


def inverse(root, rel, line, socket):
    file = inside(Path(root) / rel, root)
    if line < 1 or not socket:
        raise ValueError('Invalid inverse search target')
    # JSON carries filenames as data; never interpolate them into Ex commands.
    payload = json.dumps({'file': str(file), 'line': line}, ensure_ascii=True)
    lua = ('local p=vim.json.decode(' + json.dumps(payload) + '); '
           'local b=vim.fn.bufadd(p.file); vim.fn.bufload(b); '
           'vim.api.nvim_set_current_buf(b); '
           'vim.api.nvim_win_set_cursor(0,{math.min(p.line,vim.api.nvim_buf_line_count(b)),0})')
    lua = '(function() ' + lua + ' end)()'
    expression = 'luaeval(' + "'" + lua.replace("'", "''") + "'" + ')'
    subprocess.run(['nvim', '--server', socket, '--remote-expr', expression],
                   check=True, timeout=10, stdout=subprocess.DEVNULL)


def rpc(request):
    if request['op'] == 'discover':
        return json.dumps({'projects': discover()}).encode()
    root = str(Path(request['root']).resolve())
    state = cache(root)
    op = request['op']
    if op == 'status':
        return json.dumps(project_status(root)).encode()
    if op == 'fetch':
        generation = request['generation']
        if not re.fullmatch('[0-9a-f]{32}', generation):
            raise ValueError('Invalid generation')
        return (state / (generation + '.tar.gz')).read_bytes()
    if op == 'inverse':
        inverse(root, request['file'], int(request['line']), request['socket'])
        return b'{}'
    raise ValueError('Unknown operation')


def config(path):
    cfg = get_json(Path(path).expanduser())
    if not isinstance(cfg, dict):
        raise ValueError('Configuration must be a JSON object')
    cfg.setdefault('local_root', '~/Library/Caches/remote-tex-preview')
    for key in ('host', 'remote_tool', 'local_root'):
        if not isinstance(cfg.get(key), str) or not cfg[key]:
            raise ValueError('Missing configuration: ' + key)
    if cfg['host'].startswith('-'):
        raise ValueError('Invalid SSH host')
    cfg['local_root'] = str(Path(cfg['local_root']).expanduser().resolve())
    return cfg


def remote(cfg, request):
    request = dict(request)
    if 'remote_root' in cfg:
        request.setdefault('root', cfg['remote_root'])
    control = cache(cfg['local_root']) / 'ssh.sock'
    control.parent.mkdir(parents=True, exist_ok=True)
    cmd = ['ssh', '-oBatchMode=yes', '-oConnectTimeout=10', '-oControlMaster=auto',
           '-oControlPersist=60', '-oControlPath=' + str(control), cfg['host'],
           shlex.join([cfg.get('remote_python', 'python3'), cfg['remote_tool'], 'rpc'])]
    return subprocess.check_output(cmd, input=json.dumps(request).encode(), timeout=30)


def show(cfg, manifest, event=None):
    root = Path(cfg['local_root'])
    displayline = cfg.get('displayline', '/Applications/Skim.app/Contents/SharedSupport/displayline')
    if event:
        source = inside(root / event['file'], root)
        subprocess.run([displayline, '-r', '-g', str(event['line']), str(root / manifest['pdf']),
                        str(source)], check=True, timeout=15)
    else:
        # Explicit revert preserves the current page; disable Skim auto reload.
        script = ('on run argv\n tell application "Skim"\n'
                  'set d to open (POSIX file (item 1 of argv))\n'
                  'tell d to revert\n end tell\nend run')
        subprocess.run(['osascript', '-e', script, str(root / manifest['pdf'])],
                       check=True, timeout=15)


def project_config(cfg, root):
    if 'remote_root' in cfg:  # Existing single-project configurations still work.
        return cfg
    key = hashlib.sha256((cfg['host'] + '\0' + root).encode()).hexdigest()[:24]
    return dict(cfg, remote_root=root, local_root=str(Path(cfg['local_root']) / key))


def update_project(cfg, status, seen):
    root = status['root']
    local = project_config(cfg, root)
    destination = Path(local['local_root'])
    latest = get_json(destination / 'rtp-manifest.json')
    generation, seen_forward = seen.get(root, (None, None))
    new = status['latest']
    if new and new['generation'] != generation:
        bundle = remote(cfg, {'op': 'fetch', 'root': root, 'generation': new['generation']})
        latest = install_bundle(bundle, destination)
        if latest['root'] != root or latest['generation'] != new['generation']:
            raise ValueError('Unexpected snapshot identity')
        show(local, latest)
        generation = new['generation']
        print('Updated:', root, '/', latest['pdf'], flush=True)
    event = status['forward']
    if event and latest and event['id'] != seen_forward:
        if event.get('generation') == latest['generation']:
            show(local, latest, event)
            put_json(destination / 'rtp-session.json', event)
        seen_forward = event['id']
    seen[root] = (generation, seen_forward)


def watch(cfg, once=False):
    seen = {}
    while True:
        try:
            if 'remote_root' in cfg:
                status = json.loads(remote(cfg, {'op': 'status'}))
                status.setdefault('root', cfg['remote_root'])
                projects = [status]
            else:
                projects = json.loads(remote(cfg, {'op': 'discover'}))['projects']
            for status in projects:
                try:
                    update_project(cfg, status, seen)
                except (OSError, ValueError, subprocess.SubprocessError, tarfile.TarError) as exc:
                    if once:
                        raise
                    print('Project retry:', status['root'], exc, file=sys.stderr, flush=True)
        except (OSError, ValueError, subprocess.SubprocessError, tarfile.TarError) as exc:
            print('Preview retry:', exc, file=sys.stderr, flush=True)
            if once:
                raise
        if once:
            return
        time.sleep(max(0.2, float(cfg.get('interval', 1))))


def inverse_on_mac(cfg, file, line):
    # Same entry point as :VimtexInverseSearch, with filenames passed as Lua data.
    # Avoid embedding the path into an Ex command (quotes and bars are legal filenames).
    expression = ('lua vim.fn["vimtex#view#inverse_search_cmd"]('
                  + str(line) + ', ' + json.dumps(str(file), ensure_ascii=True) + ', 0)')
    subprocess.run([cfg.get('local_nvim', 'nvim'), '--headless', '-c', expression],
                   check=True, timeout=15)


def inverse_local(cfg, file, line):
    base = Path(cfg['local_root']).resolve()
    file = Path(file).expanduser().resolve()
    if line < 1:
        raise ValueError('Line numbers start at 1')
    try:
        file.relative_to(base)
    except ValueError:
        inverse_on_mac(cfg, file, line)
        return
    for root in file.parents:
        latest = get_json(root / 'rtp-manifest.json')
        if latest:
            session = get_json(root / 'rtp-session.json', {})
            remote(cfg, {'op': 'inverse', 'root': latest['root'],
                         'file': str(file.relative_to(root)), 'line': line,
                         'socket': session['socket'] if session.get('generation') == latest['generation']
                         else latest['socket']})
            return
        if root == base:
            break
    raise ValueError('File is not part of a downloaded preview project')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('register', 'publish', 'forward'):
        p = sub.add_parser(name)
        p.add_argument('--root', required=True)
        p.add_argument('--socket', required=True)
        if name == 'publish':
            p.add_argument('--pdf', required=True)
        elif name == 'forward':
            p.add_argument('--file', required=True)
            p.add_argument('--line', required=True, type=int)
    sub.add_parser('rpc')
    p = sub.add_parser('watch')
    p.add_argument('config')
    p.add_argument('--once', action='store_true')
    p = sub.add_parser('inverse')
    p.add_argument('config')
    p.add_argument('file')
    p.add_argument('line', type=int)
    args = parser.parse_args()
    if args.command == 'rpc':
        sys.stdout.buffer.write(rpc(json.load(sys.stdin)))
    elif args.command == 'register':
        register(args.root, args.socket)
    elif args.command == 'publish':
        publish(args.root, args.pdf, args.socket)
    elif args.command == 'forward':
        forward(args.root, args.file, args.line, args.socket)
    elif args.command == 'watch':
        watch(config(args.config), args.once)
    else:
        inverse_local(config(args.config), args.file, args.line)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as exc:
        print('rtp:', exc, file=sys.stderr)
        sys.exit(1)
