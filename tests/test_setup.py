"""Integration checks; all deployment targets and Git repositories are temporary."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('manage', ROOT / 'scripts/manage.py')
manage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(manage)


class SetupTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='dotfiles test ')
        self.addCleanup(self.tmp.cleanup)
        self.target = Path(self.tmp.name) / 'target'
        self.target.mkdir()

    def test_preview_deploy_is_idempotent_and_preserves_independent_init(self):
        init = self.target / '.config/nvim/init.lua'
        init.parent.mkdir(parents=True)
        original = 'require("my_config")\n-- user-owned configuration\n'
        init.write_text(original)
        (init.parent / '.git').mkdir()
        manage.preview(self.target)
        manage.preview(self.target)
        self.assertEqual(init.read_text(), original)
        self.assertTrue((init.parent / '.git').is_dir())
        self.assertFalse((self.target / '.local/state/dotfiles/backups').exists())
        tool = self.target / 'tools/remote-tex-preview/rtp.py'
        self.assertTrue(tool.exists())
        self.assertTrue((self.target / '.local/share/nvim/site/plugin/remote-tex-preview.lua').exists())

    def test_preview_preflights_conflicts_before_any_links_or_init_changes(self):
        command = self.target / '.local/bin/remote-tex-preview'
        command.parent.mkdir(parents=True)
        command.write_text('user command')
        init = self.target / '.config/nvim/init.lua'
        init.parent.mkdir(parents=True)
        init.write_text('user-owned init')
        with self.assertRaises(ValueError):
            manage.preview(self.target)
        self.assertEqual(command.read_text(), 'user command')
        self.assertEqual(init.read_text(), 'user-owned init')
        self.assertFalse((self.target / 'tools').exists())

    def test_short_launcher_defaults_and_passthrough(self):
        fake = Path(self.tmp.name) / 'python-stub'
        fake.write_text('#!/usr/bin/env python3\nimport json,sys\nprint(json.dumps(sys.argv[1:]))\n')
        fake.chmod(0o755)
        env = dict(os.environ, RTP_PYTHON=str(fake), RTP_TOOL='/tool path/rtp.py', RTP_CONFIG='/config path/config.json')
        script = ROOT / 'dotfiles/common/.local/bin/remote-tex-preview'
        for argv, expected in [([], ['watch', env['RTP_CONFIG']]),
                               (['--once'], ['watch', env['RTP_CONFIG'], '--once']),
                               (['inverse', 'config', 'file with space', '2'], ['inverse', 'config', 'file with space', '2'])]:
            with self.subTest(argv=argv):
                result = subprocess.check_output([str(script)] + argv, env=env, text=True)
                self.assertEqual(json.loads(result), [env['RTP_TOOL']] + expected)

    @unittest.skipUnless(shutil.which('stow'), 'GNU Stow not installed')
    def test_real_stow_preserves_independent_neovim_and_supports_preview_links(self):
        manage.preview(self.target)
        config = self.target / '.config/nvim'
        config.mkdir(parents=True, exist_ok=True)
        (config / 'init.lua').write_text('independent nvim')
        command = ['stow', '--dir=' + str(ROOT / 'dotfiles'), '--target=' + str(self.target),
                   '--no-folding', '--ignore=\\.gitkeep$']
        result = subprocess.run(command + ['--simulate', 'common', 'linux'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.target / '.zshrc').exists())
        subprocess.run(command + ['common', 'linux'], check=True, capture_output=True)
        subprocess.run(command + ['common', 'linux'], check=True, capture_output=True)
        self.assertTrue((self.target / '.zshrc').is_symlink())
        self.assertFalse((self.target / '.config/.gitkeep').exists())
        self.assertEqual((config / 'init.lua').read_text(), 'independent nvim')
        self.assertTrue((self.target / 'tools/remote-tex-preview/rtp.py').exists())
        manage.preview(self.target)  # Also works after Stow unfolds managed directories.

    @unittest.skipUnless(shutil.which('stow'), 'GNU Stow not installed')
    def test_real_stow_conflicts_do_not_overwrite_user_files(self):
        shell = self.target / '.zshrc'
        shell.write_text('my existing shell')
        result = subprocess.run(['stow', '--dir=' + str(ROOT / 'dotfiles'),
            '--target=' + str(self.target), '--no-folding', '--simulate', 'common', 'linux'], capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(shell.read_text(), 'my existing shell')
        self.assertFalse((self.target / 'tools').exists())

    def test_local_config_override_is_outside_managed_defaults(self):
        spec = importlib.util.spec_from_file_location('rtp', ROOT / 'dotfiles/common/tools/remote-tex-preview/rtp.py')
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        base = self.target / 'config.json'
        base.write_text(json.dumps({'host':'linux','remote_tool':'/default/rtp.py'}))
        override = self.target / 'config.local.json'
        override.write_text(json.dumps({'host':'other-host','local_nvim':'/custom/nvim'}))
        cfg = module.config(base)
        self.assertEqual(cfg['host'], 'other-host')
        self.assertEqual(cfg['local_nvim'], '/custom/nvim')
        self.assertEqual(cfg['remote_tool'], '/default/rtp.py')
        self.assertEqual(json.loads(base.read_text())['host'], 'linux')


    @unittest.skipUnless(shutil.which('nvim'), 'Neovim unavailable')
    def test_user_runtime_hook_loads_without_modifying_independent_init(self):
        plugin = Path('/home/homer/.local/share/nvim/lazy/vimtex')
        if not plugin.exists():
            self.skipTest('VimTeX not installed')
        manage.preview(self.target)
        project = self.target / 'report'
        project.mkdir()
        (project / 'main.tex').write_text('Hello')
        init = self.target / '.config/nvim/init.lua'
        init.parent.mkdir(parents=True, exist_ok=True)
        original = ('vim.opt.rtp:prepend(' + json.dumps(str(plugin)) + ')\n' +
                    "vim.g.vimtex_view_method='general'\n" +
                    "vim.g.vimtex_view_general_viewer='true'\n" +
                    "vim.g.vimtex_view_automatic=1\n" +
                    "vim.cmd('filetype plugin indent on')\n")
        init.write_text(original)
        for ssh in (False, True):
            env = dict(os.environ, XDG_DATA_HOME=str(self.target/'.local/share'),
                       XDG_CACHE_HOME=str(self.target/'.cache'), XDG_STATE_HOME=str(self.target/'.local/state'),
                       RTP_TOOL=str(self.target/'tools/remote-tex-preview/rtp.py'))
            for key in ('SSH_CONNECTION', 'SSH_CLIENT', 'SSH_TTY', 'RTP_REMOTE_PREVIEW'):
                env.pop(key, None)
            if ssh:
                env['SSH_CONNECTION'] = 'test session'
            check = self.target / 'verify.lua'
            check.write_text("assert(vim.b.vimtex)\n" +
                ('assert(vim.b.vimtex.viewer.rtp_root==vim.fn.getcwd())\n'
                 if ssh else "assert(vim.b.vimtex.viewer.rtp_root==nil)\n") +
                'assert(vim.g.vimtex_view_automatic==' + ('0' if ssh else '1') + ')\n' +
                "print('PASS runtime'); vim.cmd('qa!')\n")
            result = subprocess.run(['nvim','--headless','-i','NONE','--listen',str(self.target/'nvim.sock'),
                '-u',str(init),str(project/'main.tex'),'-c','luafile '+str(check).replace(' ', r'\ '),'-c','qa!'],
                cwd=project, env=env, capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('PASS runtime', result.stdout + result.stderr)
            self.assertEqual(init.read_text(), original)


if __name__ == '__main__':
    unittest.main()
