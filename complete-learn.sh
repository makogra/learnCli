_learn_complete()
{
    local cur prev
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[1]}"

    commands="list goal hint check ok skip"

    if [[ ${COMP_CWORD} == 1 ]]; then
        COMPREPLY=( $(compgen -W "${commands}" -- ${cur}) )
        return 0
    fi

    if [[ ${prev} == "goal" || ${prev} == "list" ]]; then
        local cats=$(ls categories 2>/dev/null | sed 's/.json//')
        COMPREPLY=( $(compgen -W "${cats}" -- ${cur}) )
        return 0
    fi
}

complete -F _learn_complete learn
