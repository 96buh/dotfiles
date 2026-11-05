-- Loaded by Neovim's default user runtime; keep the editor config in its own repo.
local preview = vim.env.RTP_TOOL
  and (vim.fs.dirname(vim.env.RTP_TOOL) .. "/preview.lua")
  or vim.fn.expand("~/tools/remote-tex-preview/preview.lua")
if vim.fn.filereadable(preview) == 1 then
  dofile(preview).setup()
end
