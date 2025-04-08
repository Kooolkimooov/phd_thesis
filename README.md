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

```bash
usage: build.py [-h] {thesis,chapters,chapter,figures,figure,clean,all} ...

LaTeX thesis build script

positional arguments:
  {thesis,chapters,chapter,figures,figure,clean,all}
                        Build command
    thesis              Build the complete thesis
    chapters            Build all chapters as separate pdf files
    chapter             Build a specific chapter as separate pdf file
    figures             Build all figures
    figure              Build a specific figure
    clean               Clean build files
    all                 Build thesis and all chapters

options:
  -h, --help            show this help message and exit
```

This will compile the LaTeX files in the `build/` directory and output the final result in the `out/` directory.

## License

See the LICENSE file for details.