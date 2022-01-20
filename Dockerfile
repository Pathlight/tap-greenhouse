# `dw-base` comes from `base_image/Dockerfile`. This step sets up the postgres target.
FROM dw-base:latest

# TODO fill in the tap command here
ENV TAP_COMMAND tap-greenhouse

USER root

ADD ./tap-greenhouse tap-greenhouse

RUN python -m venv tap-venv \
    # Need to install singer from our git repo before the tap to avoid install issues.
    # This is optional, as it may not work for taps that rely on a very old singer version.
    && tap-venv/bin/pip install "git+https://github.com/Pathlight/singer-python.git@v5.7.1#egg=singer-python" \
    # TODO install the tap here
    && tap-venv/bin/pip install -e "./tap-greenhouse"
# Set up logging for singer in `tap-venv`. `logging.conf` comes from the base image.
RUN cp logging.conf tap-venv/lib/python3.7/site-packages/singer/logging.conf

USER $MY_USER