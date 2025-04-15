# My PhD Thesis repository

## Project Structure

- `thesis.tex` - Main document file
- `preamble.tex` - LaTeX configuration and package imports
- `title.tex` - Title page formatting and content
- `bib.bib` - Bibliography file
- `build.py` - Python script for building the thesis
- `chapter.tex` - Template used to programmatically compile individual chapters
- `figure.tex` - Template used to programmatically compile individual figures
- `chapters/` - Directory containing individual chapter files
- `figures/` - Directory for figures and diagrams

## Requirements

1. A LaTeX distribution:
   - Windows: MiKTeX or TeX Live
   - MacOS: MacTeX
   - Linux: TeX Live
2. Python 3.x (required for the build script)

## Building the Thesis

You can build the thesis using the included Python script:

```
usage: build.py [-h] [--verbose] [--HELP] {thesis,chapters,chapter,figures,figure,clean,all} ...

LaTeX thesis build script

positional arguments:
  {thesis,chapters,chapter,figures,figure,clean,all}
    thesis              build the complete thesis
    chapters            build all chapters as separate pdf files
    chapter             build a specific chapter as separate pdf file
    figures             build all figures
    figure              build a specific figure
    clean               clean build files
    all                 build thesis and all chapters

options:
  -h, --help            show this help message and exit
  --verbose, -v         enable verbose output
  --HELP, -H            show verbose help message and exit

          ==========

usage: build.py thesis [-h] [--remake]

options:
  -h, --help    show this help message and exit
  --remake, -r  skip building figures

          ==========

usage: build.py chapters [-h] [--remake]

options:
  -h, --help    show this help message and exit
  --remake, -r  skip rebuilding figures

          ==========

usage: build.py chapter [-h] [--remake] name

positional arguments:
  name          name of the chapter to build

options:
  -h, --help    show this help message and exit
  --remake, -r  skip rebuilding figures

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

usage: build.py all [-h] [--remake]

options:
  -h, --help    show this help message and exit
  --remake, -r  skip rebuilding figures
```

This will compile the LaTeX files in the `build/` directory and output the final result in the `out/` directory.

## License

See the LICENSE file for details.