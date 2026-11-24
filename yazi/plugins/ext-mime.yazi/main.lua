-- Fetches MIME types from file extensions only (no file reads), for slow FUSE mounts.
local MIMES = {
	mp4 = "video/mp4", mkv = "video/x-matroska", webm = "video/webm", mov = "video/quicktime",
	avi = "video/x-msvideo", m4v = "video/x-m4v", wmv = "video/x-ms-wmv", flv = "video/x-flv",
	ts = "video/mp2t", mpg = "video/mpeg", mpeg = "video/mpeg",
	mp3 = "audio/mpeg", flac = "audio/flac", wav = "audio/x-wav", ogg = "audio/ogg",
	m4a = "audio/mp4", opus = "audio/opus",
	jpg = "image/jpeg", jpeg = "image/jpeg", png = "image/png", gif = "image/gif",
	webp = "image/webp", heic = "image/heic", svg = "image/svg+xml", bmp = "image/bmp",
	pdf = "application/pdf", epub = "application/epub+zip",
	txt = "text/plain", md = "text/markdown", nfo = "text/plain", srt = "text/plain",
	json = "application/json",
	zip = "application/zip", rar = "application/rar", ["7z"] = "application/7z-compressed",
}

local M = {}

function M:fetch(job)
	local updates = {}
	for _, f in ipairs(job.files) do
		local ext = tostring(f.url):match("%.([^./]+)$")
		local mime = f.cha.is_dir and "inode/directory" or (ext and MIMES[ext:lower()]) or "application/octet-stream"
		updates[f.url] = mime
	end
	ya.emit("update_mimes", { updates = updates })
	return true
end

return M
