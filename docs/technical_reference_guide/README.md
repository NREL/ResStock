# ResStock Technical Reference Guide

This folder contains the LaTeX project for the ResStock Technical Reference Guide.
The main file is the `ResStockTechnicalReferenceGuide.tex` file and when compiled produces `ResStockTechnicalReferenceGuide.pdf` in this directory. 

## GitHub Actions
In the `.github/workflows/config.yml` file, the `updates-results` job `Build technical reference guide` task compiles the project into the `ResStockTechnicalReferenceGuide.pdf` file.
This file is then committed in the "Latest results" commit in the `Commit latest results` task.
These actions will help keep the document up to date with any changes and fail in the tests if the document does not compile.

## Building Technical Reference Guide Locally
To compile the ResStock Technical Reference Guide locally it is recommended to use the same environment as the GitHub Action (currently ubuntu 22.04). To get this enviornment install [Docker](https://www.docker.com/) and follow the steps below. After the first time running through this process, where docker container is built and texlive is installed steps #2 and #4 can be skipped.

1. With the terminal/command prompt navigate to the resstock repository technical reference guide directory.

```
cd <RESSTOCK_DIR>/docs/technical_reference_guide
```

2. Build an ubuntu container similar to GitHub Actions ubuntu 22.04 (only needs to be done the first time)

```
docker build -t github-actions-ubuntu22 .
```

3. Run the newly built container and mount the current directory contents in the workspace directory of the container.

```
docker run -it -v $(pwd):/workspace github-actions-ubuntu22
```

4. Install the full texlive package (only needs to be done the first time and might take a few minutes)

```
apt-get install texlive-full
```

5. Go to the workspace

```
cd workspace
```

6. Compile the documentation (this command may need to be run two times for some parts of the documentation to show up in the output pdf)

```
pdflatex ResStockTechnicalReferenceGuide.tex -file-line-error -interaction=nonstopmode
```
