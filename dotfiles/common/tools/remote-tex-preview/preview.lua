-- Load before opening TeX buffers; this module never starts a compiler.
local M = {}
local module_dir = vim.fs.dirname(debug.getinfo(1, 'S').source:sub(2))
function M.setup(opts)
  -- macOS keeps its local VimTeX/Skim viewer, even with a shared init.lua.
  if vim.fn.has('macunix') == 1 then return end
  -- Local Linux sessions retain their normal viewer. An explicit override also
  -- handles tmux sessions whose SSH environment differs from their attachment.
  local mode = vim.env.RTP_REMOTE_PREVIEW
  local ssh = false
  for _, name in ipairs({'SSH_CONNECTION', 'SSH_CLIENT', 'SSH_TTY'}) do
    if vim.env[name] and vim.env[name] ~= '' then ssh = true end
  end
  if mode == '0' or (mode ~= '1' and not ssh) then return end
  opts = opts or {}
  -- Capture startup cwd once; subsequent :lcd/:cd must not change this project.
  local root = vim.uv.fs_realpath(opts.root or vim.fn.getcwd())
  assert(root, 'Remote preview: project directory does not exist')
  local tool = vim.fs.normalize(opts.tool or (module_dir .. '/rtp.py'))
  local python = opts.python or 'python3'
  vim.g.vimtex_view_automatic = 0
  _G.RemoteTexPreviewHandlers = _G.RemoteTexPreviewHandlers or {}
  local function belongs(path)
    return path == root or path:sub(1, #root + 1) == root .. '/'
  end
  local function is_project(state)
    return state and type(state.root) == 'string' and vim.uv.fs_realpath(state.root) == root
      and vim.fn.filereadable(root .. '/main.tex') == 1
  end
  local function run(args)
    vim.system(args, { text = true }, function(result)
      if result.code ~= 0 then
        vim.schedule(function() vim.notify('Remote preview: ' .. result.stderr, vim.log.levels.ERROR) end)
      end
    end)
  end
  local function base(command)
    return { python, tool, command, '--root', root, '--socket', vim.v.servername }
  end
  local group = vim.api.nvim_create_augroup('RemoteTexPreview_' .. vim.fn.sha256(root):sub(1, 12), {clear=true})
  vim.api.nvim_create_autocmd('User', {
    group = group, pattern = 'VimtexEventCompileSuccess',
    callback = function()
      local state = vim.b.vimtex
      if not is_project(state) or type(state.compiler) ~= 'table' then return end
      local pdf = vim.fn.eval("b:vimtex.compiler.get_file('pdf')")
      if pdf == '' then return end
      local args = base('publish')
      vim.list_extend(args, {'--pdf', pdf})
      run(args)
    end,
  })
  -- A per-buffer viewer avoids modifying the global Zathura configuration.
  vim.api.nvim_create_autocmd('User', {
    group = group, pattern = 'VimtexEventInitPost',
    callback = function()
      local state = vim.b.vimtex
      -- Package/class buffers and disabled viewer modules may have no viewer.
      if not is_project(state) or type(state.viewer) ~= 'table' then return end
      run(base('register'))
      vim.cmd('let b:vimtex.viewer.rtp_root = ' .. vim.fn.string(root))
      vim.cmd([[
        let b:vimtex.viewer.view = function('RemoteTexPreviewView')
      ]])
    end,
  })
  _G.RemoteTexPreviewHandlers[root] = function()
    local file = vim.api.nvim_buf_get_name(0)
    if not belongs(file) then return end
    local args = base('forward')
    vim.list_extend(args, {'--file', file, '--line', tostring(vim.fn.line('.'))})
    run(args)
  end
  _G.RemoteTexPreviewForward = function(project)
    _G.RemoteTexPreviewHandlers[project]()
  end
  vim.cmd([[
    function! RemoteTexPreviewView(...) dict abort
      call v:lua.RemoteTexPreviewForward(self.rtp_root)
    endfunction
  ]])
end
return M
