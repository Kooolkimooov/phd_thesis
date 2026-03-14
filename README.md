# My PhD Thesis repository

## Project Structure

- `thesis.tex` - Main document file
- `preamble.tex` - LaTeX configuration and package imports
- `front_cover.tex` - Front cover page formatting and content
- `back_cover.tex` - Back cover page formatting and content
- `chapters/` - Directory containing individual chapter files
- `figures/` - Directory for figures and diagrams
- `bib.bib` - Bibliography file
- `build.py` - Python script for building the thesis
- `chapter.tex` - Template used by the script to programmatically compile individual chapters
- `figure.tex` - Template used by the script to programmatically compile individual tikz  figures
- `gitdescription.tex` - Empty file used by the script to embed git information in the thesis

## Requirements

1. A LaTeX distribution:
   - Windows: MiKTeX or TeX Live
   - MacOS: MacTeX
   - Linux: TeX Live
2. Python 3.x (required for the build script)

## Building the Thesis

You can build the thesis using the included Python script:

```usage: build.py [-h] [-H] [-v] [-d] {thesis,chapters,chapter,figures,figure,clean,all,check} ...

LaTeX thesis build script

positional arguments:
  {thesis,chapters,chapter,figures,figure,clean,all,check}
    thesis              build the complete thesis
    chapters            build all chapters as separate pdf files
    chapter             build a specific chapter as separate pdf file
    figures             build all figures
    figure              build a specific figure
    clean               clean build files
    all                 build thesis and all chapters
    check               check for unused bibliography entries and figures

options:
  -h, --help            show this help message and exit
  -H, --HELP            show verbose help message and exit
  -v, --verbose         enable verbose output
  -d, --dry-run         dry run, do not execute any commands

          ==========

usage: build.py thesis [-h] [-r] [-gd GIT_DESCRIPTION]

options:
  -h, --help            show this help message and exit
  -r, --remake          skip building figures
  -gd, --git-description GIT_DESCRIPTION
                        git description to embed in the thesis

          ==========

usage: build.py chapters [-h] [-r] [-gd GIT_DESCRIPTION]

options:
  -h, --help            show this help message and exit
  -r, --remake          skip rebuilding figures
  -gd, --git-description GIT_DESCRIPTION
                        git description to embed in the thesis

          ==========

usage: build.py chapter [-h] [-r] [-gd GIT_DESCRIPTION] name

positional arguments:
  name                  name of the chapter to build

options:
  -h, --help            show this help message and exit
  -r, --remake          skip rebuilding figures
  -gd, --git-description GIT_DESCRIPTION
                        git description to embed in the thesis

          ==========

usage: build.py figures [-h]

options:
  -h, --help  show this help message and exit

          ==========

usage: build.py figure [-h] name

positional arguments:
  name        Name of the figure to build

options:
  -h, --help  show this help message and exit

          ==========

usage: build.py clean [-h] [name]

positional arguments:
  name        clean files of that name

options:
  -h, --help  show this help message and exit

          ==========

usage: build.py all [-h] [-r] [-gd GIT_DESCRIPTION]

options:
  -h, --help            show this help message and exit
  -r, --remake          skip rebuilding figures
  -gd, --git-description GIT_DESCRIPTION
                        git description to embed in the thesis

          ==========

usage: build.py check [-h] [--remove-unused]

options:
  -h, --help       show this help message and exit
  --remove-unused  delete unused figures and bib entries (makes backup of bib.bib)
```

This will compile the LaTeX files in the `build/` directory and output the final result in the `out/` directory.

## License

See the LICENSE file for details.
