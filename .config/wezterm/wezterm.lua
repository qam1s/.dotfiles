local wezterm = require("wezterm")
local act = wezterm.action
local config = wezterm.config_builder()
local copy_mode = wezterm.gui.default_key_tables().copy_mode

for i = #copy_mode, 1, -1 do
    local k = copy_mode[i]
    if k.key == "v" and k.mods == "NONE" then
        table.remove(copy_mode, i)
    elseif k.key == "c" and k.mods == "CTRL" then
        table.remove(copy_mode, i)
    end
end

table.insert(copy_mode, {
    key = "Space",
    mods = "NONE",
    action = act.CopyMode({ SetSelectionMode = "Cell" }),
})

table.insert(copy_mode, {
    key = "c",
    mods = "CTRL",
    action = act.Multiple({
        act.CopyTo("ClipboardAndPrimarySelection"),
        act.ScrollToBottom,
        act.CopyMode("Close"),
    }),
})

config.font_size = 13.5
config.color_scheme = "Catppuccin Macchiato"
config.hide_tab_bar_if_only_one_tab = true
config.show_new_tab_button_in_tab_bar = false
config.use_fancy_tab_bar = false
config.default_cursor_style = "SteadyBar"
config.window_close_confirmation = "NeverPrompt"
config.keys = {
    {
        key = "Space",
        mods = "CTRL|SHIFT",
        action = act.ActivateCopyMode,
    },
    {
        key = "v",
        mods = "CTRL",
        action = act.PasteFrom("Clipboard"),
    },
    {
        key = "t",
        mods = "CTRL",
        action = act.SpawnTab("CurrentPaneDomain"),
    },
    {
        key = "w",
        mods = "CTRL",
        action = act.CloseCurrentTab({ confirm = false }),
    },
    {
        key = "Tab",
        mods = "CTRL",
        action = act.ActivateTabRelative(1),
    },
    {
        key = "Tab",
        mods = "CTRL|SHIFT",
        action = act.ActivateTabRelative(-1),
    },
    {
        key = "z",
        mods = "CTRL",
        action = act.SendKey({
            key = "c",
            mods = "CTRL",
        }),
    },
}

config.window_padding = {
    left = 1,
    right = 1,
    top = 0,
    bottom = 0,
}

config.key_tables = {
    copy_mode = copy_mode,
}

return config
