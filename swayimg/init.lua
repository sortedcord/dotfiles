-- Natural (inverted) two-finger touchpad scrolling.
-- Ctrl+scroll zoom is left in its default direction.

swayimg.viewer.on_scroll(function(kmods, horizontal, vertical)
  if kmods == "Ctrl" then
    if vertical then
      local mouse = swayimg.get_mouse_pos()
      local scale = swayimg.viewer.scale
      swayimg.viewer.set_abs_scale(scale - scale * vertical / 10.0, mouse.x, mouse.y)
    end
  else
    local pos = swayimg.viewer.get_position()
    swayimg.viewer.set_abs_position(pos.x - math.floor(horizontal * 50),
                                    pos.y - math.floor(vertical * 50))
  end
end)

swayimg.gallery.on_scroll(function(kmods, horizontal, vertical)
  if kmods == "Ctrl" then
    if vertical then
      swayimg.gallery.thumb_size = math.max(
        swayimg.gallery.thumb_size + math.floor(-vertical / 2), 0)
    end
  else
    if horizontal then
      swayimg.gallery.select(horizontal > 0 and "right" or "left")
    end
    if vertical then
      swayimg.gallery.select(vertical > 0 and "down" or "up")
    end
  end
end)

-- q closes the app
for _, mode in ipairs({ swayimg.viewer, swayimg.slideshow, swayimg.gallery }) do
  mode.on_key("q", function()
    swayimg.exit()
  end)
end
