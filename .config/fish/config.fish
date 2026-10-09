if status is-interactive
    set fish_greeting ""

    bind -m visual shift-left 'commandline -f begin-selection; commandline -f backward-char'
    bind -m visual shift-right 'commandline -f begin-selection; commandline -f forward-char'
    bind -m visual ctrl-shift-left 'commandline -f begin-selection; commandline -f backward-word'
    bind -m visual ctrl-shift-right 'commandline -f begin-selection; commandline -f forward-word'
    bind -m visual \e\[1\;6D 'commandline -f begin-selection; commandline -f backward-word'
    bind -m visual \e\[1\;6C 'commandline -f begin-selection; commandline -f forward-word'
    bind -m visual shift-up 'commandline -f begin-selection; commandline -f up-line'
    bind -m visual shift-down 'commandline -f begin-selection; commandline -f down-line'
    bind -m visual shift-home 'commandline -f begin-selection; commandline -f beginning-of-line'
    bind -m visual shift-end 'commandline -f begin-selection; commandline -f end-of-line'

    bind -M visual shift-left backward-char
    bind -M visual shift-right forward-char
    bind -M visual ctrl-shift-left backward-word
    bind -M visual ctrl-shift-right forward-word
    bind -M visual \e\[1\;6D backward-word
    bind -M visual \e\[1\;6C forward-word
    bind -M visual shift-up up-line
    bind -M visual shift-down down-line
    bind -M visual shift-home beginning-of-line
    bind -M visual shift-end end-of-line

    bind -M visual -m default left 'commandline -f end-selection; commandline -f backward-char'
    bind -M visual -m default right 'commandline -f end-selection; commandline -f forward-char'
    bind -M visual -m default up 'commandline -f end-selection; up-or-search'
    bind -M visual -m default down 'commandline -f end-selection; down-or-search'
    bind -M visual -m default enter 'commandline -f end-selection; commandline -f execute'

    bind -M visual -m default ctrl-c 'fish_clipboard_copy; commandline -f end-selection; commandline -f end-of-line; commandline -f repaint'
    bind -M visual -m default ctrl-x 'fish_clipboard_copy; commandline -f kill-selection; commandline -f end-selection; commandline -f repaint'
    bind -M visual -m default backspace 'commandline -f kill-selection; commandline -f end-selection; commandline -f repaint'
    bind -M visual -m default delete 'commandline -f kill-selection; commandline -f end-selection; commandline -f repaint'
    bind -M visual -m default '' kill-selection end-selection self-insert repaint
    bind -M visual -m default space kill-selection end-selection self-insert expand-abbr repaint
end

fish_add_path $HOME/.local/bin
