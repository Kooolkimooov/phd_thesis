#!/usr/bin/python3

import os
import glob
import shutil
import subprocess
import argparse
import platform

# Configuration
COMPILER = "latexmk"
LATEX_FLAGS = ["-output-directory=build", "-pdf", "--shell-escape", 
               "-interaction=nonstopmode", "-file-line-error"]

def check_latex_installation():
    """Check if a LaTeX distribution is installed."""
    if platform.system() == "Windows":
        miktex_path = os.path.expanduser("~\\miktex")
        if os.path.exists(miktex_path):
            print("MiKTeX found")
            return "miktex"
        
        texlive_path = os.path.expanduser("~\\texlive")
        if os.path.exists(texlive_path):
            print("TeXLive found")
            return "texlive"
    else:
        # TODO: fix that check
        try:
            subprocess.run(["which", COMPILER], check=True, capture_output=True)
            return "latex"
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
    
    print("Warning: No LaTeX distribution found")
    return None

def ensure_output_directories():
    """Create necessary output directories if they don't exist."""
    os.makedirs("build/figures", exist_ok=True)
    os.makedirs("build/build/figures", exist_ok=True)
    os.makedirs("out", exist_ok=True)

def build_figure(name=None):
    """Build a specific figure or all figures."""
    ensure_output_directories()
    
    if name:
        figure_path = f"figures/{name}.tex"
        if not os.path.exists(figure_path):
            print(f"Error: Figure file {figure_path} does not exist")
            return False
        
        print(f"Building figure {name}...")
        
        with open("figure.tex", "r") as f:
            content = f.read()
        
        modified_content = content.replace("PLACEHOLDER", name)
        
        with open("figure.tex", "w") as f:
            f.write(modified_content)
        
        try:
            subprocess.run([COMPILER] + LATEX_FLAGS + ["figure.tex"], check=True)
            print(f"Figure {name} built successfully")
        except subprocess.CalledProcessError:
            print(f"Error: Failed to build figure {name}")
        
        with open("figure.tex", "w") as f:
            f.write(content)

    else:
        print("Prebuilding all figures...")
        
        for figure_file in glob.glob("figures/*.tex"):
            basename = os.path.splitext(os.path.basename(figure_file))[0]
            build_figure(basename)
        
def build_chapter(name=None, remake=False):
    """Build a specific chapter or all chapters."""
    ensure_output_directories()
    
    if not remake:
        build_figure()  
    
    if name:
        chapter_path = f"chapters/{name}.tex"
        if not os.path.exists(chapter_path):
            print(f"Error: Chapter file {chapter_path} does not exist")
            return False
        
        print(f"Building chapter {name}...")
        
        with open("chapter.tex", "r") as f:
            content = f.read()
        
        modified_content = content.replace("PLACEHOLDER", name)
        
        with open("chapter.tex", "w") as f:
            f.write(modified_content)
        
        try:
            subprocess.run([COMPILER] + LATEX_FLAGS + ["chapter.tex"], check=True)
        except subprocess.CalledProcessError:
            print(f"Error: Failed to build chapter {name}")
            
        with open("chapter.tex", "w") as f:
            f.write(content)
            
        try:
            shutil.move("build/chapter.pdf", f"out/{name}.pdf")
        except (FileNotFoundError, shutil.Error) as e:
            print(f"Error moving output file: {e}")
        
        with open("chapter.tex", "w") as f:
            f.write(content)

        print(f"Chapter {name} compiled successfully to out/{name}.pdf")
    
    else:
        print("Building all chapters...")
        
        for chapter_file in glob.glob("chapters/*.tex"):
            basename = os.path.splitext(os.path.basename(chapter_file))[0]
            build_chapter(basename)

        print(f"All chapters compiled successfully to out/*.pdf")
        
def build_thesis(remake=False):
    """Build the complete thesis."""
    ensure_output_directories()
    
    if not remake:
        build_figure()
    
    print("Compiling thesis...")
    
    try:
        subprocess.run([COMPILER] + LATEX_FLAGS + ["thesis.tex"], check=True)
    except subprocess.CalledProcessError:
        print("Error: Failed to build thesis")
        return False
    
    try:
        shutil.move("build/thesis.pdf", "out/thesis.pdf")
    except (FileNotFoundError, shutil.Error) as e:
        print(f"Error moving output file: {e}")
        return False
    
    print("Thesis compiled successfully to out/thesis.pdf")
    return True

def clean(name=None):
    """Clean up build files."""
    if name:
        for pattern in [f"build/{name}.*", f"out/{name}.*"]:
            for file in glob.glob(pattern):
                try:
                    os.remove(file)
                    print(f"Removed {file}")
                except (FileNotFoundError, PermissionError) as e:
                    print(f"Error removing {file}: {e}")
        print(f"Build files cleaned for {name}")
    else:
        for directory in ["build", "out"]:
            if os.path.exists(directory):
                try:
                    shutil.rmtree(directory)
                    print(f"Removed {directory} directory")
                except (FileNotFoundError, PermissionError) as e:
                    print(f"Error removing {directory}: {e}")

def main():
    """Parse arguments and run the appropriate command."""
    parser = argparse.ArgumentParser(description="LaTeX thesis build script")
    subparsers = parser.add_subparsers(dest="command", help="Build command")
    
    thesis_parser = subparsers.add_parser("thesis", help="Build the complete thesis")
    thesis_parser.add_argument("--remake", action="store_true", 
                              help="Skip rebuilding figures")
    
    chapters_parser = subparsers.add_parser("chapters", help="Build all chapters as separate pdf files")
    chapters_parser.add_argument("--remake", action="store_true", 
                              help="Skip rebuilding figures")
    
    chapter_parser = subparsers.add_parser("chapter", help="Build a specific chapter")
    chapter_parser.add_argument("name", help="Name of the chapter to build")
    chapter_parser.add_argument("--remake", action="store_true",
                                help="Skip rebuilding figures")
    
    subparsers.add_parser("figures", help="Build all figures")
    
    figure_parser = subparsers.add_parser("figure", help="Build a specific figure")
    figure_parser.add_argument("name", help="Name of the figure to build")
    
    clean_parser = subparsers.add_parser("clean", help="Clean build files")
    clean_parser.add_argument("name", nargs="?", default=None, help="Clean files of that name")
    
    all_parser = subparsers.add_parser("all", help="Build thesis and all chapters")
    all_parser.add_argument("--remake", action="store_true", 
                              help="Skip rebuilding figures")

    args = parser.parse_args()
    

    if args.command == "clean":
        clean(args.name)
        return
    
    latex_distribution = check_latex_installation()
    print(f"Using LaTeX distribution: {latex_distribution}")

    if latex_distribution == "miktex":
        LATEX_FLAGS.extend(["--extra-mem-top=10000000", "--main-memory=10000000", 
                           "--extra-mem-bot=10000000"])
    
    if args.command == "thesis":
        build_thesis(remake=args.remake)
    elif args.command == "chapters":
        build_chapter(remake=args.remake)
    elif args.command == "chapter":
        build_chapter(name=args.name, remake=args.remake)
    elif args.command == "figures":
        build_figure()
    elif args.command == "figure":
        build_figure(name=args.name)
    elif args.command == "all":
        build_thesis(remake=args.remake)
        build_chapter(remake=True)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()