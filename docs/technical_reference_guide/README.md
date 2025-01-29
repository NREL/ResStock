# ResStock Technical Reference Guide

This folder contains the LaTeX project for the ResStock Technical Reference Guide.
The main file is the `ResStockTechnicalReferenceGuide.tex` file and when compiled produces `ResStockTechnicalReferenceGuide.pdf` in this directory. 

## GitHub Actions
In the `.github/workflows/config.yml` file, the `updates-results` job `Build technical reference guide` task compiles the project into the `ResStockTechnicalReferenceGuide.pdf` file.
This file is then committed in the "Latest results" commit in the `Commit latest results` task.
These actions will help keep the document up to date with any changes and fail in the tests if the document does not compile.

## Building Technical Reference Guide Locally
Docker can be used to compile the ResStock Technical Reference Guide locally. First install [Docker](https://www.docker.com/) and follow the steps below.

1. With the terminal/command prompt navigate to the resstock repository technical reference guide directory.

```
cd <RESSTOCK_DIR>/docs/technical_reference_guide
```

2. Pull a docker container with the full version of textlive (only needs to be done once)

```
$ docker run --rm -it -v $(pwd):/data mfisherman/texlive-full /bin/sh
```

3. Run the container and mount the current directory contents in the workspace directory of the container. Use /bin/bash as the default shell.

```
docker run --rm -it -v $(pwd):/workspace mfisherman/texlive-full /bin/bash
```

4. Go to the workspace

```
cd workspace
```

6. Create a _build directory for the output of `pdflatex` to be stored.
```
mkdir _build
```

5. Compile the documentation (this command may need to be run two times for some parts of the documentation to show up in the output pdf)

```
pdflatex --interaction=nonstopmode --file-line-error -output-directory=_build ResStockTechnicalReferenceGuide.tex
```
