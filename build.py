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
SILENT_FLAGS = ["-silent"]

def printlog(message: str): 
    message = " " + message + " "
    print(f"{message:->{shutil.get_terminal_size().columns}}", flush=True)

def check_latex_installation():
    if platform.system() == "Windows":
        if shutil.which(COMPILER):
            if shutil.which("miktex-console.exe"):
                return "miktex"
            elif shutil.which("tlmgr.bat") or shutil.which("tlmgr"):
                return "texlive"
            else:
                return "latex"
        
    else:
        if os.path.exists("/usr/share/texlive") or os.path.exists("/usr/local/texlive") or os.path.exists("/opt/texlive"):
            return "texlive"
        
        if os.path.exists("/usr/share/miktex-texmf") or os.path.exists("/usr/local/miktex-texmf") or os.path.exists("/opt/miktex-texmf"):
            return "miktex"
        
        if os.path.exists(os.path.join("/usr/share", COMPILER)) or os.path.exists(os.path.join("/usr/bin", COMPILER)):
            return "latex"
  
    return None

def ensure_output_directories():
    os.makedirs("build/figures", exist_ok=True)
    os.makedirs("build/build/figures", exist_ok=True)
    os.makedirs("out", exist_ok=True)

def build_figure(name=None):
    ensure_output_directories()
    
    if name:
        figure_path = f"figures/{name}.tex"
        if not os.path.exists(figure_path):
            printlog(f"file {figure_path} does not exist")
            return False
        
        printlog(f"building figure {name}")
        
        with open("figure.tex", "r") as f:
            content = f.read()
        
        modified_content = content.replace("PLACEHOLDER", name)
        
        with open("figure.tex", "w") as f:
            f.write(modified_content)
        
        try:
            subprocess.run([COMPILER] + LATEX_FLAGS + ["figure.tex"], check=True)
            printlog(f"figure {name} compiled")

        except subprocess.CalledProcessError as e:
            printlog(f"error while building figure {name}: {e}")
            return False
        
        finally:
            with open("figure.tex", "w") as f:
                f.write(content)

        return True

    else:
        printlog("building all figures")
        
        files = [os.path.splitext(os.path.basename(file))[0] for file in glob.glob("figures/*.tex")]
        successes = []

        for file in files:
            successes.append(build_figure(file))

        for success, file in zip(successes, files):
            printlog(f"{file}: {'compiled' if success else '  failed'}")
        
        return all(successes)
        
def build_chapter(name=None, remake=False, git_description=None):
    ensure_output_directories()
    
    if not remake:
        success = build_figure()
        if not success:
            return False
    
    if name:
        chapter_path = f"chapters/{name}.tex"
        if not os.path.exists(chapter_path):
            printlog(f"file {chapter_path} does not exist")
            return False
        
        gitcommit_path = "gitdescription.tex"
        with open(gitcommit_path, "r") as f:
            original_content = f.read()

        if git_description is None:
            try:
                git_description = subprocess.run(["git", "describe", "--dirty"], capture_output=True, check=True).stdout.strip().decode()
        
            except subprocess.CalledProcessError as e:
                printlog(f"error while getting git commit info: {e}")
        
        printlog(f"building chapter {name}")
        
        with open("chapter.tex", "r") as f:
            content = f.read()
        
        modified_content = content.replace("PLACEHOLDER", name)
        
        with open("chapter.tex", "w") as f:
            f.write(modified_content)
        
        try:
            subprocess.run([COMPILER] + LATEX_FLAGS + ["chapter.tex"], check=True)

        except subprocess.CalledProcessError as e:
            printlog(f"error while building chapter {name}: {e}")
            return False
        
        finally:
            with open("chapter.tex", "w") as f:
                f.write(content)
            
        try:
            shutil.move("build/chapter.pdf", f"out/{name}_{git_description}.pdf")
        except (FileNotFoundError, shutil.Error) as e:
            printlog(f"error moving output file: {e}")
            return False

        printlog(f"chapter {name} compiled to out/{name}.pdf")
        return True
    
    else:
        printlog("building all chapters")
        
        files = [os.path.splitext(os.path.basename(file))[0] for file in glob.glob("chapters/*.tex")]
        successes = []
        for file in files:
            successes.append(build_chapter(name=file, remake=True))

        for success, file in zip(successes, files):
            printlog(f"{file}: {'compiled' if success else '  failed'}")
        
        return all(successes)
            
def build_thesis(remake=False, git_description=None):
    ensure_output_directories()
    
    if not remake:
        success = build_figure()
        if not success:
            return False
    
    printlog("building thesis")

    gitcommit_path = "gitdescription.tex"
    with open(gitcommit_path, "r") as f:
        original_content = f.read()

    if git_description is None:
        try:
            git_description = subprocess.run(["git", "describe", "--dirty"], capture_output=True, check=True).stdout.strip().decode()
        
        except subprocess.CalledProcessError as e:
            printlog(f"error while getting git commit info: {e}")
    
    with open(gitcommit_path, "w") as f:
        f.write(git_description)

    try:
        subprocess.run([COMPILER] + LATEX_FLAGS + ["thesis.tex"], check=True)

    except subprocess.CalledProcessError as e:
        printlog(f"error while building thesis: {e}")
        return False
    
    finally:
        with open(gitcommit_path, "w") as f:
            f.write(original_content)
    
    try:
        shutil.move("build/thesis.pdf", f"out/thesis_{git_description}.pdf")
    except (FileNotFoundError, shutil.Error) as e:
        printlog(f"error moving output file: {e}")
        return False
    
    printlog("thesis compiled to out/thesis.pdf")
    return True

def clean(name=None):
    if name:
        for pattern in [f"build/{name}.*", f"out/{name}.*", f"build/figures/{name}.*", f"build/build/figures/{name}.*"]:
            for file in glob.glob(pattern):
                try:
                    os.remove(file)
                    printlog(f"removed {file}")
                except (FileNotFoundError, PermissionError) as e:
                    printlog(f"error removing {file}: {e}")
                    return False
        printlog(f"build files cleaned for {name}")
    else:
        for directory in ["build", "out"]:
            if os.path.exists(directory):
                try:
                    shutil.rmtree(directory)
                    printlog(f"removed {directory} directory")
                except (FileNotFoundError, PermissionError) as e:
                    printlog(f"error removing {directory}: {e}")
                    return False
    return True

def main():
    parser = argparse.ArgumentParser(description="LaTeX thesis build script")
    subparsers = parser.add_subparsers(dest="command")
    
    thesis_parser = subparsers.add_parser("thesis", help="build the complete thesis")
    thesis_parser.add_argument("-r", "--remake", action="store_true", help="skip building figures")
    thesis_parser.add_argument("-gd", "--git-description", type=str, default=None, help="git description to embed in the thesis")
    
    chapters_parser = subparsers.add_parser("chapters", help="build all chapters as separate pdf files")
    chapters_parser.add_argument("-r", "--remake", action="store_true", help="skip rebuilding figures")
    chapters_parser.add_argument("-gd", "--git-description", type=str, default=None, help="git description to embed in the thesis")
    
    chapter_parser = subparsers.add_parser("chapter", help="build a specific chapter as separate pdf file")
    chapter_parser.add_argument("name", help="name of the chapter to build")
    chapter_parser.add_argument("-r", "--remake", action="store_true", help="skip rebuilding figures")
    chapter_parser.add_argument("-gd", "--git-description", type=str, default=None, help="git description to embed in the thesis")
    
    subparsers.add_parser("figures", help="build all figures")
    
    figure_parser = subparsers.add_parser("figure", help="build a specific figure")
    figure_parser.add_argument("name", help="Name of the figure to build")
    
    clean_parser = subparsers.add_parser("clean", help="clean build files")
    clean_parser.add_argument("name", nargs="?", default=None, help="clean files of that name")
    
    all_parser = subparsers.add_parser("all", help="build thesis and all chapters")
    all_parser.add_argument("-r", "--remake", action="store_true", help="skip rebuilding figures")
    all_parser.add_argument("-gd", "--git-description", type=str, default=None, help="git description to embed in the thesis")
    
    parser.add_argument("-H", "--HELP", action="store_true", help="show verbose help message and exit")
    parser.add_argument("-v", "--verbose", action="store_true", help="enable verbose output")

    help_msg = parser.format_help()
    for subparser in subparsers.choices.values():
        help_msg += "\n" + f"{'=' * 10 :^30}" + "\n\n"
        help_msg += subparser.format_help()

    args = parser.parse_args()

    if args.HELP:
        print(help_msg)
        return True

    if args.command == "clean":
        return clean(args.name)
    
    latex_distribution = check_latex_installation()
    if latex_distribution is None: 
        printlog("latexmk not found, exiting")
        return -1
    printlog(f"using {latex_distribution}")

    if not args.verbose:
        LATEX_FLAGS.extend(SILENT_FLAGS)
    if latex_distribution == "miktex":
        LATEX_FLAGS.extend(["--extra-mem-top=10000000", "--main-memory=10000000", "--extra-mem-bot=10000000"])
    
    if args.command == "thesis":
        return build_thesis(remake=args.remake, git_description=args.git_description)
    elif args.command == "chapters":
        return build_chapter(remake=args.remake, git_description=args.git_description)
    elif args.command == "chapter":
        return build_chapter(name=args.name, remake=args.remake, git_description=args.git_description)
    elif args.command == "figures":
        return build_figure()
    elif args.command == "figure":
        return build_figure(name=args.name)
    elif args.command == "all":
        return build_thesis(remake=args.remake, git_description=args.git_description) and build_chapter(remake=True, git_description=args.git_description)
    else:
        print(help_msg)
        return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)