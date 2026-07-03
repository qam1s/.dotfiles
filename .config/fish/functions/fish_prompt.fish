function fish_prompt
    printf '%s%s > ' (prompt_pwd) (fish_git_prompt)
end
