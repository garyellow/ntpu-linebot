ARG VARIANT="3.12"

FROM mcr.microsoft.com/devcontainers/python:${VARIANT}

ARG DOCKER_IN_DOCKER=0
ARG OH_MY_POSH=0
ARG BASHRC_PATH=/etc/bash.bashrc
ARG ZSHRC_PATH=/etc/zsh/zshrc
ARG BASH_COMPLETION_DIR=/usr/share/bash-completion/completions
ARG ZSH_COMPLETION_DIR=/usr/share/zsh/vendor-completions
ARG DOCKER_COMPLETION_URL=https://raw.githubusercontent.com/docker/cli/master/contrib/completion

RUN \
    # Update to latest packages and install bash-completion
    apt update; \
    apt install -y \
    bash-completion; \
    apt dist-upgrade -y; \
    rm -rf /var/lib/apt/lists/*; \
    # Add hilighting support to zsh
    git clone https://github.com/zdharma-continuum/fast-syntax-highlighting /usr/share/zsh/fast-syntax-highlighting && \
    echo "source /usr/share/zsh/fast-syntax-highlighting/fast-syntax-highlighting.plugin.zsh" >> ${ZSHRC_PATH}; \
    # Add suggestions support to zsh
    git clone https://github.com/zsh-users/zsh-autosuggestions.git /usr/share/zsh/zsh-autosuggestions && \
    echo "source /usr/share/zsh/zsh-autosuggestions/zsh-autosuggestions.zsh" >> ${ZSHRC_PATH}; \
    echo "export ZSH_AUTOSUGGEST_STRATEGY=(history completion)" >> ${ZSHRC_PATH}; \
    # Add oh-my-zsh plugins
    mkdir ${ZSH_CACHE_DIR}; \
    echo "source ~/.oh-my-zsh/plugins/git/git.plugin.zsh" >> ${ZSHRC_PATH}; \
    echo "source ~/.oh-my-zsh/plugins/poetry-env/poetry-env.plugin.zsh" >> ${ZSHRC_PATH}; \
    # Install poetry and set completions
    pipx install poetry && \
    poetry completions bash > ${BASH_COMPLETION_DIR}/poetry; \
    poetry completions zsh > ${ZSH_COMPLETION_DIR}/_poetry; \
    # Add docker completions
    if [ "${DOCKER_IN_DOCKER}" = "1" ]; then \
    curl -fsSL ${DOCKER_COMPLETION_URL}/bash/docker -o ${BASH_COMPLETION_DIR}/docker; \
    curl -fsSL ${DOCKER_COMPLETION_URL}/zsh/_docker -o ${ZSH_COMPLETION_DIR}/_docker; \
    fi; \
    # Install oh-my-posh and set theme
    if [ "${OH_MY_POSH}" = "1" ]; then \
    curl -fsSL https://ohmyposh.dev/install.sh | bash && \
    echo 'eval "$(oh-my-posh init bash --config https://raw.githubusercontent.com/garyellow/omp-config/refs/heads/main/theme.omp.yaml)"' >> ${BASHRC_PATH}; \
    echo 'eval "$(oh-my-posh init zsh --config https://raw.githubusercontent.com/garyellow/omp-config/refs/heads/main/theme.omp.yaml)"' >> ${ZSHRC_PATH}; \
    fi
