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
usage: build.py [-h] [-H] [-v] {thesis,chapters,chapter,figures,figure,clean,all} ...

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

optional arguments:
  -h, --help            show this help message and exit
  -H, --HELP            show verbose help message and exit
  -v, --verbose         enable verbose output

          ==========

usage: build.py thesis [-h] [-r]

optional arguments:
  -h, --help    show this help message and exit
  -r, --remake  skip building figures

          ==========

usage: build.py chapters [-h] [-r]

optional arguments:
  -h, --help    show this help message and exit
  -r, --remake  skip rebuilding figures

          ==========

usage: build.py chapter [-h] [-r] name

positional arguments:
  name          name of the chapter to build

optional arguments:
  -h, --help    show this help message and exit
  -r, --remake  skip rebuilding figures

          ==========

usage: build.py figures [-h]

optional arguments:
  -h, --help  show this help message and exit

          ==========

usage: build.py figure [-h] name

positional arguments:
  name        Name of the figure to build

optional arguments:
  -h, --help  show this help message and exit

          ==========

usage: build.py clean [-h] [name]

positional arguments:
  name        clean files of that name

optional arguments:
  -h, --help  show this help message and exit

          ==========

usage: build.py all [-h] [-r]

optional arguments:
  -h, --help    show this help message and exit
  -r, --remake  skip rebuilding figures
```

This will compile the LaTeX files in the `build/` directory and output the final result in the `out/` directory.

## License

See the LICENSE file for details.