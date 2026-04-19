FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm

RUN rm -f /etc/apt/sources.list.d/yarn.list \
    && rm -f /etc/apt/sources.list.d/yarn.list.save

RUN curl -LsSf https://getbruin.com/install/cli | sh \
    && mv ~/.local/bin/bruin /usr/local/bin/bruin \
    && chmod +x /usr/local/bin/bruin