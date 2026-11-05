"""Run with python3 -m unittest discover -s tests -v."""
import gzip
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import tarfile
import tempfile
import unittest
from unittest import mock

TOOL = Path(__file__).resolve().parents[1] / "dotfiles/common/tools/remote-tex-preview"
spec = importlib.util.spec_from_file_location('rtp', TOOL / 'rtp.py')
rtp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rtp)


class PreviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='rtp test ')
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.root = self.base / 'remote project'
        self.root.mkdir()
        self.env = mock.patch.dict(os.environ, {'XDG_CACHE_HOME': str(self.base / 'cache'),
                 'XDG_STATE_HOME': str(self.base / 'state')})
        self.env.start()
        self.addCleanup(self.env.stop)
        (self.root / 'main.tex').write_text('hello')
        self.pdf = self.root / 'out' / 'main.pdf'
        self.pdf.parent.mkdir()
        self.pdf.write_bytes(b'%PDF-1.4\nhello\n%%EOF\n')
        self.sync = self.pdf.with_suffix('.synctex.gz')
        self.sync.write_bytes(gzip.compress(('SyncTeX Version:1\nInput:1:' +
            str(self.root / 'main.tex') + '\nOutput:pdf\n!0\nContent:\n').encode()))

    def publish(self):
        return rtp.publish(self.root, self.pdf, '/tmp/test.sock')

    def test_snapshot_relocation_and_sources(self):
        m = self.publish()
        dest = self.base / 'Mac preview'
        bundle = rtp.rpc({'op': 'fetch', 'root': str(self.root), 'generation': m['generation']})
        rtp.install_bundle(bundle, dest)
        self.assertEqual((dest / 'out/main.pdf').read_bytes(), self.pdf.read_bytes())
        content = gzip.decompress((dest / 'out/main.synctex.gz').read_bytes())
        self.assertIn(os.fsencode(dest / 'main.tex'), content)
        self.assertEqual((dest / 'main.tex').read_text(), 'hello')

    def test_failed_publish_preserves_previous(self):
        m = self.publish()
        self.pdf.write_bytes(b'%PDF-1.4\npartial')
        with self.assertRaises(ValueError):
            self.publish()
        self.assertEqual(rtp.get_json(rtp.cache(self.root) / 'latest.json'), m)

    def test_minted_transient_inputs_do_not_block_publication(self):
        missing = self.root / 'out' / '_FAD58DE.config.minted'
        existing = self.root / 'out' / 'highlight.pygtex.minted'
        existing.write_text('generated highlighting')
        sync = gzip.decompress(self.sync.read_bytes())
        sync += ('Input:2:' + str(missing) + '\nInput:3:' + str(existing) + '\n').encode()
        self.sync.write_bytes(gzip.compress(sync))
        manifest = self.publish()
        self.assertEqual(set(manifest['inputs'].values()), {'main.tex'})
        self.assertNotIn('out/highlight.pygtex.minted', manifest['files'])
        destination = self.base / 'Mac preview'
        rtp.install_bundle(rtp.rpc({'op': 'fetch', 'root': str(self.root),
                           'generation': manifest['generation']}), destination)
        rewritten = gzip.decompress((destination / 'out/main.synctex.gz').read_bytes())
        self.assertIn(b'Input:2:' + os.fsencode(missing), rewritten)
        self.assertEqual((destination / 'main.tex').read_text(), 'hello')

    def test_missing_real_source_still_fails_without_replacing_preview(self):
        previous = self.publish()
        sync = gzip.decompress(self.sync.read_bytes()) + b'Input:2:./missing.tex\n'
        self.sync.write_bytes(gzip.compress(sync))
        with self.assertRaises(FileNotFoundError):
            self.publish()
        self.assertEqual(rtp.get_json(rtp.cache(self.root) / 'latest.json'), previous)

    def test_generation_retention_and_independent_projects(self):
        for _ in range(5):
            self.publish()
        self.assertEqual(len(list(rtp.cache(self.root).glob('*.tar.gz'))), 3)
        self.assertNotEqual(rtp.cache(self.root), rtp.cache(self.root.parent / 'other'))

    def test_forward_unicode_and_traversal(self):
        file = self.root / "章 ' quoted.tex"
        file.write_text('hello')
        rtp.forward(self.root, file, 12, '/tmp/one.sock')
        state = json.loads(rtp.rpc({'op': 'status', 'root': str(self.root)}))
        self.assertEqual(state['forward']['file'], file.name)
        with self.assertRaises(ValueError):
            rtp.forward(self.root, self.root / '../escape.tex', 1, 'sock')
        with self.assertRaises(ValueError):
            rtp.rpc({'op': 'fetch', 'root': str(self.root), 'generation': '../escape'})

    def test_tar_traversal_rejected(self):
        data = io.BytesIO()
        with tarfile.open(fileobj=data, mode='w:gz') as tar:
            entry = tarfile.TarInfo('../escape')
            entry.size = 1
            tar.addfile(entry, io.BytesIO(b'x'))
        with self.assertRaises(ValueError):
            rtp.install_bundle(data.getvalue(), self.base / 'local')
        self.assertFalse((self.base / 'escape').exists())

    def test_retry_and_no_compiler_invocation(self):
        cfg = {'local_root': str(self.base / 'local')}
        with mock.patch.object(rtp, 'remote', side_effect=OSError('disconnected')):
            with self.assertRaises(OSError):
                rtp.watch(cfg, once=True)
        with mock.patch.object(rtp, 'remote', return_value=b'{"projects":[]}'):
            with mock.patch.object(rtp.subprocess, 'run') as run:
                rtp.watch(cfg, once=True)
                run.assert_not_called()

    @unittest.skipUnless(shutil.which('pdflatex') and shutil.which('synctex'), 'TeX tools unavailable')
    def test_real_synctex_forward_and_inverse_after_relocation(self):
        (self.root / 'main.tex').write_text('\\documentclass{article}\n\\begin{document}\nHello world.\n\\input{section}\n\\end{document}\n')
        (self.root / 'section.tex').write_text('A child section.\n')
        subprocess.run(['pdflatex', '-synctex=1', '-interaction=nonstopmode',
                        '-output-directory=out', 'main.tex'], cwd=self.root,
                       check=True, stdout=subprocess.DEVNULL)
        m = self.publish()
        dest = self.base / 'local much longer path' / 'project'
        rtp.install_bundle(rtp.rpc({'op':'fetch', 'root':str(self.root),
                                  'generation':m['generation']}), dest)
        result = subprocess.check_output(['synctex', 'view', '-i',
                  '1:0:' + str(dest / 'section.tex'), '-o', str(dest / 'out/main.pdf')], text=True)
        self.assertIn('Page:1', result)
        fields = dict(line.split(':', 1) for line in result.splitlines() if ':' in line)
        result = subprocess.check_output(['synctex', 'edit', '-o',
             '1:' + fields['x'] + ':' + fields['y'] + ':' + str(dest / 'out/main.pdf')], text=True)
        self.assertIn(str(dest / 'section.tex'), result)

    @unittest.skipUnless(shutil.which('nvim'), 'Neovim unavailable')
    def test_inverse_existing_neovim_with_quoted_filename(self):
        socket = str(self.base / 'nvim.sock')
        process = subprocess.Popen(['nvim', '--headless', '-u', 'NONE', '--listen', socket],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.addCleanup(lambda: (process.kill(), process.wait()) if process.poll() is None else None)
        import time
        for _ in range(100):
            if Path(socket).exists():
                break
            time.sleep(.02)
        file = self.root / "a ' quoted.tex"
        file.write_text('one\ntwo\nthree\n')
        rtp.inverse(self.root, file.name, 2, socket)
        result = subprocess.check_output(['nvim', '--server', socket, '--remote-expr',
                                          'json_encode([expand("%:p"), line(".")])'], text=True)
        self.assertEqual(json.loads(result), [str(file), 2])
        process.terminate()
        process.wait(timeout=5)


    @unittest.skipUnless(shutil.which('nvim') and shutil.which('pdflatex'), 'Editor/TeX unavailable')
    def test_vimtex_manual_compile_hook_and_view(self):
        plugin = Path.home() / '.local/share/nvim/lazy/vimtex'
        if not plugin.exists():
            self.skipTest('VimTeX not installed')
        (self.root / 'main.tex').write_text('\\documentclass{article}\n\\begin{document}\nHello.\n\\end{document}\n')
        init = self.base / 'init.lua'
        init.write_text("vim.opt.rtp:prepend(" + json.dumps(str(plugin)) + ")\n" +
            "vim.env.SSH_CONNECTION='test-ssh-session'; vim.env.RTP_REMOTE_PREVIEW=nil\n" +
            "vim.g.vimtex_view_automatic=0\n" +
            "vim.g.vimtex_compiler_latexmk={out_dir='out', options={'-pdf','-synctex=1','-interaction=nonstopmode'}}\n" +
            "dofile(" + json.dumps(str(TOOL / 'preview.lua')) + ").setup()\n" +
            "vim.cmd('filetype plugin indent on')\n")
        latest = rtp.cache(self.root) / 'latest.json'
        forward = rtp.cache(self.root) / 'forward.json'
        check = self.base / 'check.lua'
        check.write_text("vim.cmd('write')\n" +
            "assert(vim.fn.filereadable(" + json.dumps(str(latest)) + ")==0, 'save compiled unexpectedly')\n" +
            "vim.cmd('VimtexCompileSS')\n" +
            "assert(vim.wait(20000,function() return vim.fn.filereadable(" + json.dumps(str(latest)) + ")==1 end,50),'publish timed out')\n" +
            "vim.cmd('VimtexView')\n" +
            "assert(vim.wait(5000,function() return vim.fn.filereadable(" + json.dumps(str(forward)) + ")==1 end,50),'forward timed out')\n" +
            "vim.cmd('qa!')\n")
        result = subprocess.run(['nvim', '--headless', '-u', str(init), str(self.root / 'main.tex'),
                    '-c', 'luafile ' + str(check).replace(' ', r'\ ' )], cwd=self.root,
                    capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(latest.exists(), result.stderr)
        self.assertTrue(forward.exists(), result.stderr)


    def test_tool_can_move_and_run_outside_repository(self):
        moved = self.base / 'unrelated location' / 'preview'
        shutil.copytree(TOOL, moved, ignore=shutil.ignore_patterns('__pycache__'))
        subprocess.run([os.sys.executable, str(moved / 'rtp.py'), 'publish',
            '--root', str(self.root), '--pdf', str(self.pdf), '--socket', '/tmp/moved.sock'],
            cwd=self.base, check=True)
        self.assertEqual(rtp.get_json(rtp.cache(self.root) / 'latest.json')['socket'], '/tmp/moved.sock')

    def test_skim_commands_use_arguments_not_shell_interpolation(self):
        cfg = {'local_root': str(self.base / 'Mac preview')}
        manifest = {'pdf': 'out/main.pdf'}
        with mock.patch.object(rtp.subprocess, 'run') as run:
            rtp.show(cfg, manifest)
            self.assertEqual(run.call_args.args[0][0], 'osascript')
            rtp.show(cfg, manifest, {'file': "a ' quoted.tex", 'line': 2})
            self.assertEqual(run.call_args.args[0][1:3], ['-r', '-g'])
            self.assertEqual(run.call_args.args[0][-1], str(Path(cfg['local_root']) / "a ' quoted.tex"))

    def test_ssh_protocol_transmits_json_and_quotes_tool_path(self):
        cfg = {'local_root':str(self.base / 'Mac preview'), 'host':'my-alias',
               'remote_root':str(self.root), 'remote_tool':"/a b/quoted ' tool.py"}
        with mock.patch.object(rtp.subprocess, 'check_output', return_value=b'{}') as run:
            rtp.remote(cfg, {'op':'status'})
            args = run.call_args.args[0]
            import shlex
            self.assertEqual(shlex.split(args[-1]), ['python3', cfg['remote_tool'], 'rpc'])
            self.assertEqual(json.loads(run.call_args.kwargs['input'])['root'], str(self.root))

    def listening_socket(self, name):
        path = str(self.base / name)
        listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        listener.bind(path)
        listener.listen(32)
        self.addCleanup(listener.close)
        return path, listener

    def test_discovery_waits_without_compiling_and_ignores_closed_sessions(self):
        path, listener = self.listening_socket('editor.sock')
        rtp.register(self.root, path)
        projects = json.loads(rtp.rpc({'op': 'discover'}))['projects']
        self.assertEqual([p['root'] for p in projects], [str(self.root)])
        self.assertIsNone(projects[0]['latest'])
        listener.close()  # Socket file remains, but the editor is gone.
        self.assertEqual(rtp.discover(), [])
        self.assertFalse((rtp.cache(self.root) / 'latest.json').exists())

    def test_auto_multi_project_sync_and_inverse_routing(self):
        first_socket, _ = self.listening_socket('first.sock')
        second_socket, _ = self.listening_socket('second.sock')
        second = self.base / 'second project'
        second.mkdir()
        (second / 'main.tex').write_text('second project source')
        (second / 'main.pdf').write_bytes(self.pdf.read_bytes())
        (second / 'main.synctex.gz').write_bytes(gzip.compress(
            b'SyncTeX Version:1\nInput:1:./main.tex\nOutput:pdf\n'))
        rtp.publish(self.root, self.pdf, first_socket)
        rtp.publish(second, second / 'main.pdf', second_socket)
        rtp.forward(second, second / 'main.tex', 1, second_socket)
        cfg = {'host': 'one-host', 'local_root': str(self.base / 'Mac cache')}
        calls = []

        def transport(_cfg, request):
            calls.append(dict(request))
            return rtp.rpc(request)

        with mock.patch.object(rtp, 'remote', side_effect=transport):
            with mock.patch.object(rtp, 'show') as show:
                rtp.watch(cfg, once=True)
                self.assertEqual(show.call_count, 3)  # Two PDFs and one forward search.
        self.assertEqual(calls[0], {'op': 'discover'})
        for root, expected_socket in [(self.root, first_socket), (second, second_socket)]:
            local = Path(rtp.project_config(cfg, str(root))['local_root'])
            self.assertEqual((local / 'main.tex').read_text(), (root / 'main.tex').read_text())
            with mock.patch.object(rtp, 'remote', return_value=b'{}') as send:
                rtp.inverse_local(cfg, local / 'main.tex', 1)
                request = send.call_args.args[1]
                self.assertEqual(request['root'], str(root))
                self.assertEqual(request['socket'], expected_socket)
                self.assertEqual(request['file'], 'main.tex')

    def test_host_and_project_cache_isolation(self):
        a = {'host': 'host-a', 'local_root': str(self.base / 'Mac cache')}
        b = dict(a, host='host-b')
        self.assertNotEqual(rtp.project_config(a, '/report'), rtp.project_config(b, '/report'))
        self.assertNotEqual(rtp.project_config(a, '/report'), rtp.project_config(a, '/other'))

    def test_config_needs_no_report_path(self):
        path = self.base / 'config.json'
        path.write_text(json.dumps({'host': 'my-linux', 'remote_tool': '/fixed/rtp.py'}))
        cfg = rtp.config(path)
        self.assertNotIn('remote_root', cfg)
        self.assertIn('local_root', cfg)

    def test_local_source_uses_existing_vimtex_entry_point_without_ssh(self):
        cfg = {'local_root': str(self.base / 'Mac cache'), 'local_nvim': '/custom/nvim'}
        file = self.base / "local 章 ' quoted | main.tex"
        file.write_text('local source')
        with mock.patch.object(rtp, 'remote') as ssh:
            with mock.patch.object(rtp.subprocess, 'run') as run:
                rtp.inverse_local(cfg, file, 12)
                args = run.call_args.args[0]
                self.assertEqual(args[:3], ['/custom/nvim', '--headless', '-c'])
                self.assertIn('vimtex#view#inverse_search_cmd', args[3])
                self.assertIn(json.dumps(str(file), ensure_ascii=True), args[3])
                ssh.assert_not_called()

    def test_remote_missing_manifest_never_falls_back_to_local_editor(self):
        cfg = {'local_root': str(self.base / 'Mac cache')}
        file = Path(cfg['local_root']) / 'project' / 'main.tex'
        file.parent.mkdir(parents=True)
        file.write_text('cached remote source')
        with mock.patch.object(rtp, 'inverse_on_mac') as local:
            with self.assertRaises(ValueError):
                rtp.inverse_local(cfg, file, 1)
            local.assert_not_called()

    def test_remote_connection_failure_never_falls_back_to_local_editor(self):
        cfg = {'local_root': str(self.base / 'Mac cache')}
        root = Path(cfg['local_root']) / 'project'
        rtp.put_json(root / 'rtp-manifest.json', {'root': '/remote/report',
                     'generation': 'generation', 'socket': '/remote/nvim.sock'})
        with mock.patch.object(rtp, 'remote', side_effect=OSError('offline')):
            with mock.patch.object(rtp, 'inverse_on_mac') as local:
                with self.assertRaises(OSError):
                    rtp.inverse_local(cfg, root / 'main.tex', 1)
                local.assert_not_called()

    def test_inverse_rejects_invalid_line_before_either_route(self):
        cfg = {'local_root': str(self.base / 'Mac cache')}
        with mock.patch.object(rtp, 'inverse_on_mac') as local:
            with self.assertRaises(ValueError):
                rtp.inverse_local(cfg, self.root / 'main.tex', 0)
            local.assert_not_called()

    @unittest.skipUnless(shutil.which('nvim'), 'Neovim unavailable')
    def test_local_fallback_reaches_existing_vimtex_session(self):
        plugin = Path.home() / '.local/share/nvim/lazy/vimtex'
        if not plugin.exists():
            self.skipTest('VimTeX not installed')
        init = self.base / 'local-init.lua'
        init.write_text('vim.opt.rtp:prepend(' + json.dumps(str(plugin)) + ')\n'
                        "vim.g.vimtex_view_automatic=0\n"
                        "vim.g.vimtex_view_method='general'\n"
                        "vim.g.vimtex_view_general_viewer='true'\n"
                        "vim.cmd('filetype plugin indent on')\n"
                        "vim.cmd('runtime plugin/vimtex.vim')\n")
        file = self.root / 'main.tex'
        file.write_text('one\ntwo\nthree\n')
        server = str(self.base / 'local-editor.sock')
        process = subprocess.Popen(['nvim', '--headless', '-u', str(init), '-i', 'NONE',
                    '--listen', server, str(file)], cwd=self.root,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.addCleanup(lambda: (process.kill(), process.wait()) if process.poll() is None else None)
        import time
        for _ in range(100):
            if Path(server).exists():
                break
            time.sleep(.02)
        # Ensure FileType initialization and VimTeX server registration completed.
        subprocess.check_output(['nvim', '--server', server, '--remote-expr', 'b:vimtex.root'])
        original_run = subprocess.run

        def isolated_client(args, **kwargs):
            return original_run(args[:1] + ['-u', str(init), '-i', 'NONE'] + args[1:], **kwargs)

        with mock.patch.object(rtp.subprocess, 'run', side_effect=isolated_client):
            rtp.inverse_local({'local_root': str(self.base / 'Mac cache')}, file, 2)
        result = subprocess.check_output(['nvim', '--server', server, '--remote-expr',
                    'json_encode([expand("%:p"),line(".")])'], text=True)
        self.assertEqual(json.loads(result), [str(file), 2])

    @unittest.skipUnless(shutil.which('nvim'), 'Neovim unavailable')
    def test_moved_lua_automatically_uses_cwd_for_different_reports(self):
        moved = self.base / 'fixed tool location'
        shutil.copytree(TOOL, moved, ignore=shutil.ignore_patterns('__pycache__'))
        second = self.base / 'another report'
        second.mkdir()
        for root in (self.root, second):
            (root / 'main.tex').write_text('hello')
            script = self.base / 'probe.lua'
            script.write_text("vim.env.SSH_CONNECTION='test-ssh-session'; vim.env.RTP_REMOTE_PREVIEW=nil\n" +
                'dofile(' + json.dumps(str(moved / 'preview.lua')) + ').setup()\n' +
                "vim.b.vimtex={root=vim.fn.getcwd(),viewer={name='Test'}}\n" +
                "vim.cmd('doautocmd User VimtexEventInitPost')\n" +
                "assert(vim.wait(5000,function() return #vim.fn.glob(" +
                json.dumps(str(rtp.cache(root) / 'sessions' / '*.json')) +
                ",false,true)>0 end,20),'registration failed')\n" +
                "vim.cmd('qa!')\n")
            result = subprocess.run(['nvim', '--headless', '-u', 'NONE', '-i', 'NONE',
                '-c', 'luafile ' + str(script).replace(' ', r'\ ')], cwd=root,
                capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            session_files = list((rtp.cache(root) / 'sessions').glob('*.json'))
            self.assertEqual(len(session_files), 1)
            self.assertEqual(rtp.get_json(session_files[0])['root'], str(root))

    @unittest.skipUnless(shutil.which('nvim'), 'Neovim unavailable')
    def test_preview_activation_preserves_local_viewer_and_detects_ssh(self):
        cases = [({}, False), ({'SSH_CONNECTION': ''}, False),
                 ({'SSH_CONNECTION': 'client port server port'}, True),
                 ({'SSH_CLIENT': 'client port port'}, True),
                 ({'SSH_TTY': '/dev/pts/1'}, True),
                 ({'SSH_CONNECTION': 'connected', 'RTP_REMOTE_PREVIEW': '0'}, False),
                 ({'RTP_REMOTE_PREVIEW': '1'}, True)]
        for env, enabled in cases:
            with self.subTest(env=env):
                script = self.base / 'activation.lua'
                lines = ["vim.env.SSH_CONNECTION=nil; vim.env.SSH_CLIENT=nil; vim.env.SSH_TTY=nil; vim.env.RTP_REMOTE_PREVIEW=nil",
                         "vim.g.vimtex_view_automatic=1; vim.g.vimtex_view_method='zathura'"]
                lines += ['vim.env[' + json.dumps(k) + ']=' + json.dumps(v) for k, v in env.items()]
                lines += ['dofile(' + json.dumps(str(TOOL / 'preview.lua')) + ').setup()',
                          'assert((_G.RemoteTexPreviewHandlers ~= nil) == ' + str(enabled).lower() + ')',
                          'assert(vim.g.vimtex_view_automatic == ' + ('0' if enabled else '1') + ')',
                          "assert(vim.g.vimtex_view_method == 'zathura')",
                          "print('PASS activation'); vim.cmd('qa!')"]
                script.write_text('\n'.join(lines))
                result = subprocess.run(['nvim', '--headless', '-u', 'NONE', '-i', 'NONE',
                    '-c', 'luafile ' + str(script).replace(' ', r'\ '), '-c', 'qa!'],
                    cwd=self.root, capture_output=True, text=True, timeout=10)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('PASS activation', result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
