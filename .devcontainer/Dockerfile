ARG VARIANT="3.12"

FROM mcr.microsoft.com/devcontainers/python:${VARIANT}

ARG DOCKER_IN_DOCKER=0
ARG BASH_COMPLETTION_DIR=/etc/bash_completion.d
ARG ZSH_COMPLETTION_DIR=/usr/share/zsh/vendor-completions
ARG DOCKER_COMPLETION_URL=https://raw.githubusercontent.com/docker/cli/master/contrib/completion
ARG DOCKER_COMPOSE_COMPLETION_URL=https://raw.githubusercontent.com/docker/compose/master/contrib/completion

# Install fonts
COPY fonts /usr/local/share/fonts

RUN \
    # Update to latest packages and install fontconfig, bash-completion
    apt update && \
    apt install -y \
    fontconfig \
    bash-completion && \
    apt dist-upgrade -y && \
    rm -rf /var/lib/apt/lists/* && \
    # Install poetry and set completions
    pipx install poetry && \
    poetry completions bash >> ${BASH_COMPLETTION_DIR}/poetry && \
    poetry completions zsh > ${ZSH_COMPLETTION_DIR}/_poetry && \
    # Set docker and docker-compose completions
    if [ "${DOCKER_IN_DOCKER}" = "1" ]; then \
    curl -sSL ${DOCKER_COMPLETION_URL}/bash/docker -o ${BASH_COMPLETTION_DIR}/docker && \
    curl -sSL ${DOCKER_COMPLETION_URL}/zsh/_docker -o ${ZSH_COMPLETTION_DIR}/_docker && \
    curl -sSL ${DOCKER_COMPOSE_COMPLETION_URL}/bash/docker-compose -o ${BASH_COMPLETTION_DIR}/docker-compose && \
    curl -sSL ${DOCKER_COMPOSE_COMPLETION_URL}/zsh/_docker-compose -o ${ZSH_COMPLETTION_DIR}/_docker-compose; \
    fi && \
    # Apply fonts (JetBrains Mono Nerd Font)
    fc-cache -f -v && \
    # Install oh-my-posh
    curl -sSL https://ohmyposh.dev/install.sh | bash -s
