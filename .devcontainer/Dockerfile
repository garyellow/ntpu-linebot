ARG VARIANT="3.12"

FROM mcr.microsoft.com/devcontainers/python:${VARIANT}

ARG DOCKER_IN_DOCKER=0
ARG OH_MY_POSH=0
ARG BASHRC_PATH=/etc/bash.bashrc
ARG ZSHRC_PATH=/etc/zsh/zshrc
ARG BASH_COMPLETION_DIR=/usr/share/bash-completion/completions
ARG ZSH_COMPLETION_DIR=/usr/share/zsh/vendor-completions
ARG DOCKER_COMPLETION_URL=https://raw.githubusercontent.com/docker/cli/master/contrib/completion
ARG DOCKER_COMPOSE_COMPLETION_URL=https://raw.githubusercontent.com/docker/compose/master/contrib/completion

RUN \
    # Update to latest packages and install fontconfig, bash-completion
    apt update && \
    apt install -y \
    bash-completion && \
    apt dist-upgrade -y && \
    rm -rf /var/lib/apt/lists/* && \
    # Install poetry and set completions
    pipx install poetry && \
    poetry completions bash > ${BASH_COMPLETION_DIR}/poetry && \
    poetry completions zsh > ${ZSH_COMPLETION_DIR}/_poetry && \
    # Set docker and docker-compose completions
    if [ "${DOCKER_IN_DOCKER}" = "1" ]; then \
    curl -sSL ${DOCKER_COMPLETION_URL}/bash/docker -o ${BASH_COMPLETION_DIR}/docker && \
    curl -sSL ${DOCKER_COMPLETION_URL}/zsh/_docker -o ${ZSH_COMPLETION_DIR}/_docker && \
    curl -sSL ${DOCKER_COMPOSE_COMPLETION_URL}/bash/docker-compose -o ${BASH_COMPLETION_DIR}/docker-compose && \
    curl -sSL ${DOCKER_COMPOSE_COMPLETION_URL}/zsh/_docker-compose -o ${ZSH_COMPLETION_DIR}/_docker-compose; \
    fi && \
    # Install oh-my-posh
    if [ "${OH_MY_POSH}" = "1" ]; then \
    curl -sSL https://ohmyposh.dev/install.sh | bash -s && \
    echo 'eval "$(oh-my-posh init bash --config .devcontainer/theme.omp.json)"' >> ${BASHRC_PATH} && \
    echo 'eval "$(oh-my-posh init zsh --config .devcontainer/theme.omp.json)"' >> ${ZSHRC_PATH}; \
    fi
