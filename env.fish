if not contains "$HOME/coral/coral-orchestrator/Coral-Monzo-Agent" $PATH
    # Prepending path in case a system-installed binary needs to be overridden
    set -x PATH "$HOME/coral/coral-orchestrator/Coral-Monzo-Agent" $PATH
end
