-- Per-folder sort rules: newest-modified files first in selected folders.
-- Exact matches apply only to the folder itself; "subtree" entries also apply to all subfolders.

local home = os.getenv("HOME")

local rules = {
	{ path = home .. "/Downloads", subtree = false },
	{ path = home .. "/Documents", subtree = false },
	{ path = home .. "/Pictures", subtree = true },
	{ path = home .. "/Videos", subtree = true },
}

local function matches(cwd)
	for _, rule in ipairs(rules) do
		if cwd == rule.path then
			return true
		end
		if rule.subtree and cwd:sub(1, #rule.path + 1) == rule.path .. "/" then
			return true
		end
	end
	return false
end

local function setup()
	ps.sub("ind-sort", function(opt)
		local cwd = tostring(cx.active.current.cwd)
		if matches(cwd) then
			-- mtime + reverse = most recently modified at the top
			opt.by, opt.reverse, opt.dir_first = "mtime", true, false
		end
		return opt
	end)
end

return { setup = setup }
