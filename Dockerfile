FROM python:3.12-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    curl \
    git \
    unzip \
    # For additional fonts needed, specifically Chinese
    texlive-fonts-recommended \
    # For usfm_tools and mypyc
    gcc \
    # For ebook-convert
    xz-utils \
    xdg-utils \
    libegl1 \
    libopengl0 \
    libegl1 \
    libopengl0 \
    libxcb-cursor0 \
    libxcb-xinerama0 \
    libxkbcommon0 \
    libglx0 \
    libnss3 \
    # For weasyprint
    pango1.0-tools \
    # For fc-cache
    fontconfig

# Get and install needed fonts.
RUN cd /tmp \
    && git clone --depth 1 https://github.com/Bible-Translation-Tools/ScriptureAppBuilder-pipeline \
    && cp /tmp/ScriptureAppBuilder-pipeline/ContainerImage/home/fonts/*.ttf /usr/share/fonts/
# Refresh system font cache.
RUN fc-cache -f -v

# Get and install calibre for use of its ebook-convert binary for HTML
# to ePub conversion.
RUN wget -nv -O- https://download.calibre-ebook.com/linux-installer.sh | sh /dev/stdin install_dir=/calibre-bin isolated=y

WORKDIR /app

RUN wget https://dot.net/v1/dotnet-install.sh -O dotnet-install.sh \
    && chmod +x ./dotnet-install.sh \
    && ./dotnet-install.sh --channel 8.0

COPY dotnet ./

RUN export DOTNET_ROOT=/root/.dotnet \
    && export PATH=$PATH:$DOTNET_ROOT:$DOTNET_ROOT/tools \
    && export DOTNET_CLI_TELEMETRY_OPTOUT=1

# Install dependencies and build the .NET project
RUN cd USFMParserDriver && /root/.dotnet/dotnet restore


# Make the output directory where resource asset files are cloned or
# downloaded and unzipped.
RUN mkdir -p working/temp
# Make the output directory where generated HTML and PDFs are placed.
RUN mkdir -p working/output
# Make the output directory where generated documents (PDF, ePub, Docx) are copied too.
RUN mkdir -p document_output

COPY pyproject.toml .
COPY ./backend/requirements.txt .
COPY ./backend/requirements-prod.txt .

# See https://pythonspeed.com/articles/activate-virtualenv-dockerfile/
# for why a Python virtual env is used inside Docker.
ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv ${VIRTUAL_ENV}
ENV PATH=${VIRTUAL_ENV}/bin:${PATH}

RUN pip install -v --upgrade pip
RUN pip install -v -r requirements.txt
RUN pip install -v -r requirements-prod.txt

COPY ./backend ./backend
COPY ./tests ./tests
COPY .env .
COPY template.docx .
COPY template_compact.docx .

# Make sure Python can find the code to run
ENV PYTHONPATH=/app/backend:/app/tests

# Inside the Python virtual env: install any missing mypy
# type packages and check types in strict mode.
RUN mypy --strict --install-types --non-interactive backend/document/**/*.py
RUN mypy --strict --install-types --non-interactive tests/**/*.py

# No longer using mypyc as the resulting executable code is now
# actually slower than non-transpiled python.
# Inside the Python virtual env: check types, install any missing mypy stub
# types packages, and transpile most modules into C using mypyc which
# in turn build them with the resident C compiler, usually clang or
# gcc.
# RUN cd backend && mypyc --strict --install-types --non-interactive document/domain/assembly_strategies/assembly_strategies.py document/domain/parsing.py document/domain/resource_lookup.py # document/domain/document_generator.py
