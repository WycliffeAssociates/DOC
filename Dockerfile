FROM python:3.12-slim-bookworm

# Create a non-root user and group
RUN groupadd -r appgroup && useradd -m -r -g appgroup appuser

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


# Create a directory for Calibre
RUN mkdir -p /home/appuser/calibre-bin

# Get and install calibre for use of its ebook-convert binary for HTML to ePub conversion.
RUN wget -nv -O- https://download.calibre-ebook.com/linux-installer.sh | sh /dev/stdin install_dir=/home/appuser/calibre-bin isolated=y

WORKDIR /app

RUN wget https://dot.net/v1/dotnet-install.sh -O dotnet-install.sh \
    && chmod +x ./dotnet-install.sh

# Create a directory for .NET SDK
RUN mkdir -p /home/appuser/.dotnet

# Install .NET SDK to the created directory
RUN ./dotnet-install.sh --channel 8.0 --install-dir /usr/share/dotnet

COPY dotnet ./

# Set environment variables for .NET
ENV DOTNET_ROOT=/usr/share/dotnet
ENV PATH=$PATH:$DOTNET_ROOT:$DOTNET_ROOT/tools
ENV DOTNET_CLI_TELEMETRY_OPTOUT=1

# Install dependencies and build the .NET project
RUN cd USFMParserDriver && \
    ${DOTNET_ROOT}/dotnet restore && \
    ${DOTNET_ROOT}/dotnet build --configuration Release

# Make the output directory where resource asset files are cloned or downloaded and unzipped.
RUN mkdir -p /app/working/temp
# Make the output directory where generated HTML and PDFs are placed.
RUN mkdir -p /app/working/output
# Make the output directory where generated documents (PDF, ePub, Docx) are copied to.
RUN mkdir -p /app/document_output

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
# Next two lines are useful when the data (graphql) API are down so
# that we can still test
COPY resources.json working/temp/resources.json
RUN touch working/temp/resources.json

# Make sure Python can find the code to run
ENV PYTHONPATH=/app/backend:/app/tests

# Inside the Python virtual env: install any missing mypy type packages and check types in strict mode.
RUN mypy --strict --install-types --non-interactive backend/document/**/*.py
RUN mypy --strict --install-types --non-interactive tests/**/*.py

# Change ownership of app specific directories to the non-root user
RUN chown -R appuser:appgroup /app /home/appuser/calibre-bin /usr/share/dotnet

# Switch to the non-root user
USER appuser

# Expose necessary ports (if any)
EXPOSE 8000

# Command to run the application
CMD ["python", "backend/main.py"]
