#!/usr/bin/python3

import argparse
import glob
import os
import platform
import shutil
import subprocess
import re

COMPILER = "latexmk"

LATEX_FLAGS = [ "-output-directory=build", "-pdf", "--shell-escape", "-interaction=nonstopmode", "-file-line-error" ]
MIKTEX_FLAGS = [ "--extra-mem-top=10000000", "--main-memory=10000000", "--extra-mem-bot=10000000" ]
SILENT_FLAGS = [ "-silent" ]

IMAGE_EXTENSIONS = [".pdf", ".png", ".jpg", ".jpeg", ".eps", ".svg"]

def printlog( message: str ):
  n_culumns = shutil.get_terminal_size().columns
  if len( message ) < 2 * n_culumns // 3:
    message = " " + message + " "
    print( f"{message:->{n_culumns}}", flush = True )
  else:
    n_split = int( len( message ) / (2 * n_culumns // 3) )
    for i in range( n_split + 1 ):
      submessage = message[ i * (2 * n_culumns // 3): (i + 1) * (2 * n_culumns // 3) ]
      submessage = " " + submessage + " "
      print( f"{submessage:->{n_culumns}}", flush = True )


def check_latex_installation():
  if platform.system() == "Windows":
    if shutil.which( COMPILER ):
      if shutil.which( "miktex-console.exe" ):
        return "miktex"
      elif shutil.which( "tlmgr.bat" ) or shutil.which( "tlmgr" ):
        return "texlive"
      else:
        return "latex"

  else:
    if os.path.exists( "/usr/share/texlive" ) or os.path.exists( "/usr/local/texlive" ) or os.path.exists(
        "/opt/texlive"
        ):
      return "texlive"

    if os.path.exists( "/usr/share/miktex-texmf" ) or os.path.exists( "/usr/local/miktex-texmf" ) or os.path.exists(
        "/opt/miktex-texmf"
        ):
      return "miktex"

    if os.path.exists( os.path.join( "/usr/share", COMPILER ) ) or os.path.exists(
        os.path.join( "/usr/bin", COMPILER )
        ):
      return "latex"

  return None


def ensure_output_directories():
  os.makedirs( "build/figures", exist_ok = True )
  os.makedirs( "build/build/figures", exist_ok = True )
  os.makedirs( "out", exist_ok = True )


def build_figure( name = None, verbose = False, dry_run = False, force_all = False ):
  ensure_output_directories()

  if name:
    figure_path = f"figures/{name}.tex"
    if not os.path.exists( figure_path ):
      printlog( f"file {figure_path} does not exist" )
      return False

    with open( "figure.tex", "r" ) as f:
      content = f.read()

    modified_content = content.replace( "PLACEHOLDER", name )

    with open( "figure.tex", "w" ) as f:
      f.write( modified_content )

    try:
      command = [ COMPILER ] + LATEX_FLAGS + (SILENT_FLAGS if not verbose else [ ]) + [ "figure.tex" ]
      printlog( f"building figure {name}" )
      if dry_run:
        printlog( f"dry run: {command}" )
      else:
        subprocess.run( command, check = True )
        printlog( f"figure {name} compiled" )

    except subprocess.CalledProcessError as e:
      printlog( f"error while building figure {name}: {e}" )
      
      # Save log files before they get overwritten
      log_file = f"build/figure.log"
      if os.path.exists(log_file):
        backup_log = f"build/figure_{name}_error.log"
        try:
          shutil.copy(log_file, backup_log)
          printlog(f"saved error log to {backup_log}")
        except Exception as move_error:
          printlog(f"failed to save log file: {move_error}")
      
      return False

    finally:
      with open( "figure.tex", "w" ) as f:
        f.write( content )

    return True

  else:

    if force_all: 
      files = ( os.path.splitext( os.path.basename( file ) )[ 0 ] for file in glob.glob( "figures/*.tex" ) )
    else: 
      files = collect_figure_tex_names() & collect_used_figures( collect_included_tex_files() )
    successes = [ ]

    if force_all: 
      printlog( "building all figures" )
    else:
      printlog( "building included figures" )

    for i, file in enumerate(files):
      printlog( f"{i + 1}/{len(files)}" )
      successes.append( build_figure( file, verbose = verbose, dry_run = dry_run ) )

    printlog( "summary of figure compilation:" )

    for success, file in zip( successes, files ):
      printlog( f"{file}: {'dry run' if dry_run else ('compiled' if success else '  failed')}" )

    return all( successes )


def build_chapter( name = None, remake = False, git_description = None, verbose = False, dry_run = False ):
  ensure_output_directories()

  if not remake:
    if not build_figure( verbose = verbose, dry_run = dry_run ):
      return False

  if name:
    chapter_path = f"chapters/{name}.tex"
    if not os.path.exists( chapter_path ):
      printlog( f"file {chapter_path} does not exist" )
      return False

    if git_description is None:
      try:
        command = [ "git", "describe", "--dirty" ]
        if dry_run:
          printlog( f"dry run: {command}" )
        else:
          git_description = subprocess.run( command, capture_output = True, check = True ).stdout.strip().decode()

      except subprocess.CalledProcessError as e:
        printlog( f"error while getting git commit info: {e}" )
    
    gitcommit_path = "gitdescription.tex"
    with open( gitcommit_path, "r" ) as f:
      original_content = f.read()

    with open( gitcommit_path, "w" ) as f:
      if dry_run:
        printlog( f"dry run: inserting {git_description} into {gitcommit_path}" )
      else:
        f.write( git_description or "" )

    printlog( f"preparing chapter template for {name}" )
    with open( "chapter.tex", "r" ) as f:
      content = f.read()

    modified_content = content.replace( "PLACEHOLDER", name )

    with open( "chapter.tex", "w" ) as f:
      f.write( modified_content )

    try:
      printlog( f"building chapter {name}" )
      command = [ COMPILER ] + LATEX_FLAGS + (SILENT_FLAGS if not verbose else [ ]) + [ "chapter.tex" ]
      if dry_run:
        printlog( f"dry run: {command}" )
      else:
        subprocess.run( command, check = True )
        printlog( f"chapter {name} compiled" )

    except subprocess.CalledProcessError as e:
      printlog( f"error while building chapter {name}: {e}" )
      
      # Save log files before they get overwritten
      log_file = f"build/chapter.log"
      if os.path.exists(log_file):
        backup_log = f"build/chapter_{name}_error.log"
        try:
          shutil.copy(log_file, backup_log)
          printlog(f"saved error log to {backup_log}")
        except Exception as move_error:
          printlog(f"failed to save log file: {move_error}")
      
      return False

    finally:
      with open( "chapter.tex", "w" ) as f:
        f.write( content )
      with open( gitcommit_path, "w" ) as f:
        f.write( original_content )

    try:
      destination = f"out/{name}_{git_description}.pdf"
      if dry_run:
        printlog( f"dry run: moving build/chapter.pdf to {destination}" )
      else:
        shutil.copy( "build/chapter.pdf", destination )
    except (FileNotFoundError, shutil.Error) as e:
      printlog( f"error moving output file: {e}" )
      return False

    printlog( f"chapter {name} compiled to out/{name}_{git_description}.pdf" )
    return True

  else:
    files = [ os.path.splitext( os.path.basename( file ) )[ 0 ] for file in glob.glob( "chapters/*.tex" ) ]
    successes = [ ]

    printlog( "building all chapters" )
    for i, file in enumerate(files):
      printlog( f"{i + 1}/{len(files)}" )
      successes.append(
          build_chapter(
              name = file, remake = True, git_description = git_description, verbose = verbose, dry_run = dry_run
              )
          )

    printlog( "summary of chapter compilation:" )
    for success, file in zip( successes, files ):
      printlog( f"{file}: {'dry run' if dry_run else ('compiled' if success else '  failed')}" )

    return all( successes )


def build_thesis( remake = False, git_description = None, verbose = False, dry_run = False ):
  ensure_output_directories()

  if not remake:
    # Only precompile figures that are actually referenced by the thesis
    success = build_figure( verbose = verbose, dry_run = dry_run )
    if not success:
      return False


  if git_description is None:
    try:
      command = [ "git", "describe", "--dirty", "--long" ]
      if dry_run:
        printlog( f"dry run: {command}" )
      else:
        git_description = subprocess.run( command, capture_output = True, check = True ).stdout.strip().decode()

    except subprocess.CalledProcessError as e:
      printlog( f"error while getting git commit info: {e}" )

  gitcommit_path = "gitdescription.tex"
  with open( gitcommit_path, "r" ) as f:
    original_content = f.read()

  with open( gitcommit_path, "w" ) as f:
    if dry_run:
      printlog( f"dry run: inserting {git_description} into {gitcommit_path}" )
    else:
      f.write( git_description or "" )

  try:
    printlog( "building thesis" )
    command = [ COMPILER ] + LATEX_FLAGS + (SILENT_FLAGS if not verbose else [ ]) + [ "thesis.tex" ]
    if dry_run:
      printlog( f"dry run: {command}" )
    else:
      subprocess.run( command, check = True )

  except subprocess.CalledProcessError as e:
    printlog( f"error while building thesis: {e}" )
    
    # Save log files before they get overwritten
    log_file = f"build/thesis.log"
    if os.path.exists(log_file):
      backup_log = f"build/thesis_error.log"
      try:
        shutil.copy(log_file, backup_log)
        printlog(f"saved error log to {backup_log}")
      except Exception as move_error:
        printlog(f"failed to save log file: {move_error}")
    
    return False

  finally:
    with open( gitcommit_path, "w" ) as f:
      f.write( original_content )

  try:
    destination = f"out/thesis_{git_description}.pdf"
    if dry_run:
      printlog( f"dry run: moving build/thesis.pdf to {destination}" )
    else:
      shutil.copy( "build/thesis.pdf", destination )
  except (FileNotFoundError, shutil.Error) as e:
    printlog( f"error moving output file: {e}" )
    return False

  printlog( f"thesis compiled to out/thesis_{git_description}.pdf" )
  return True


def clean( name = None ):
  if name:
    # TODO: also figure and chapter files
    for pattern in [ f"build/{name}.*", f"build/figures/{name}.*", f"build/build/figures/{name}.*" ]:
      for file in glob.glob( pattern ):
        try:
          os.remove( file )
          printlog( f"removed {file}" )
        except (FileNotFoundError, PermissionError) as e:
          printlog( f"error removing {file}: {e}" )
          return False
    printlog( f"build files cleaned for {name}" )
  else:
    for directory in [ "build" ]:
      if os.path.exists( directory ):
        try:
          shutil.rmtree( directory )
          printlog( f"removed {directory} directory" )
        except (FileNotFoundError, PermissionError) as e:
          printlog( f"error removing {directory}: {e}" )
          return False
  return True


def strip_tex_comments(content: str) -> str:
  """Remove LaTeX comments while preserving escaped percent signs."""
  processed_lines = []
  for line in content.splitlines():
    new_line = []
    i = 0
    while i < len(line):
      ch = line[i]
      if ch == '%':
        # If escaped, keep it
        if i > 0 and line[i - 1] == '\\':
          new_line.append(ch)
          i += 1
          continue
        else:
          # start of comment; discard rest
          break
      new_line.append(ch)
      i += 1
    processed_lines.append(''.join(new_line))
  return '\n'.join(processed_lines)


def collect_tex_files_for_usage() -> list[str]:
  # Main thesis file + chapters (exclude template helpers that contain PLACEHOLDER to avoid noise)
  tex_files = []
  if os.path.exists('thesis.tex'):
    tex_files.append('thesis.tex')
  if os.path.exists('front_cover.tex'):
    tex_files.append('front_cover.tex')
  if os.path.exists('back_cover.tex'):
    tex_files.append('back_cover.tex')
  tex_files.extend(sorted(glob.glob('chapters/*.tex')))
  return tex_files


def collect_used_citations(tex_files: list[str]) -> set[str]:
  cite_pattern = re.compile(r'\\[A-Za-z]*cite[a-zA-Z]*\*?\{([^}]*)\}')
  used: set[str] = set()
  for path in tex_files:
    try:
      with open(path, 'r', encoding='utf-8') as f:
        content = strip_tex_comments(f.read())
      for m in cite_pattern.finditer(content):
        keys_field = m.group(1)
        for key in re.split(r'\s*,\s*', keys_field.strip()):
          if key:
            used.add(key)
    except (FileNotFoundError, OSError):
      continue
  return used


def collect_bib_keys(bib_path: str = 'bib.bib') -> set[str]:
  if not os.path.exists(bib_path):
    return set()
  with open(bib_path, 'r', encoding='utf-8', errors='ignore') as f:
    bib_content = f.read()
  # Capture keys like @article{KeyName,
  pattern = re.compile(r'@\w+\{\s*([^,\s]+)\s*,')
  return {m.group(1) for m in pattern.finditer(bib_content)}


def collect_figure_tex_names() -> set[str]:
  return {os.path.splitext(os.path.basename(p))[0] for p in glob.glob('figures/*.tex')}



def collect_figure_image_names() -> set[str]:
  names = set()
  for ext in IMAGE_EXTENSIONS:
    for path in glob.glob(f'figures/*{ext}'):
      names.add(os.path.splitext(os.path.basename(path))[0])
  return names


def collect_used_figures(tex_files: list[str]) -> set[str]:
  # Detect \input{figures/name}, \includegraphics{figures/name(.pdf/.png)}, custom \inputtikz{figures/name}
  fig_pattern = re.compile(r'\\(?:input|includegraphics|inputtikz)(?:\[[^]]*\])?\{([^}]+)\}')
  used: set[str] = set()

  def figure_exists_by_name(name: str) -> bool:
    # Check both tex and image variants for existence inside figures directory
    if os.path.exists(os.path.join('figures', name + '.tex')):
      return True
    for ext in IMAGE_EXTENSIONS:
      if os.path.exists(os.path.join('figures', name + ext)):
        return True
    return False

  for path in tex_files:
    try:
      with open(path, 'r', encoding='utf-8') as f:
        content = strip_tex_comments(f.read())
      for m in fig_pattern.finditer(content):
        rel = m.group(1).replace('\\', '/')
        # Keep only last segment (ignore path components)
        last_segment = rel.split('/')[-1]
        root, ext = os.path.splitext(last_segment)
        base = root if ext.lower() in IMAGE_EXTENSIONS + ['.tex'] else last_segment

        # If explicit extension given, normalize by stripping it
        candidate = base

        if candidate and candidate != 'PLACEHOLDER':
          if 'figures/' in rel:
            used.add(candidate)
          else:
            # If no figures/ prefix, accept if file actually exists in figures directory
            if figure_exists_by_name(candidate):
              used.add(candidate)
    except (FileNotFoundError, OSError):
      continue
  return used


def collect_included_tex_files(entry: str = 'thesis.tex') -> list[str]:
  r"""Recursively collect actually included .tex files starting from entry.

  Follows \include{...} and \input{...} with paths resolved relative to the including file.
  Comments are stripped before scanning. Only existing non-figure files are returned.
  """
  include_pattern = re.compile(r'\\(?:include|input)\{([^}]+)\}')
  seen: set[str] = set()
  order: list[str] = []

  def resolve_and_add(base_file: str):
    if not os.path.exists(base_file):
      return
    norm = os.path.normpath(base_file)
    # Skip figure files in recursion set; we only want document sources
    parts = [p.lower() for p in norm.split(os.sep)]
    if 'figures' in parts:
      return
    if norm in seen:
      return
    seen.add(norm)
    order.append(norm)
    try:
      with open(norm, 'r', encoding='utf-8') as f:
        content = strip_tex_comments(f.read())
    except (FileNotFoundError, OSError):
      return
    base_dir = os.path.dirname(norm)
    for m in include_pattern.finditer(content):
      rel = m.group(1).strip()
      if not rel or rel.startswith('!'):
        continue
      # Ensure .tex extension
      rel_path = rel if os.path.splitext(rel)[1].lower() == '.tex' else rel + '.tex'
      child = os.path.normpath(os.path.join(base_dir, rel_path))
      resolve_and_add(child)

  resolve_and_add(entry)
  return order


def check(verbose: bool = False, remove_unused: bool = False, dry_run: bool = False) -> bool:
  """Check for unused bibliography and figure assets.

  If remove_unused is True, delete unused figure files and prune unused bib entries.
  A backup of bib.bib is created before modification. Honors dry_run for preview only.
  Always returns True (informational only / best-effort cleanup).
  """
  printlog('running project consistency checks' + (' (removal enabled)' if remove_unused else ''))

  tex_files = collect_tex_files_for_usage()
  if verbose:
    printlog(f'found {len(tex_files)} TeX source files to scan')

  # Citations
  bib_keys = collect_bib_keys()
  used_cites = collect_used_citations(tex_files)
  unused_bib = sorted(bib_keys - used_cites)
  undefined_cites = sorted(used_cites - bib_keys)

  printlog(f'bibliography entries: {len(bib_keys)} defined, {len(used_cites)} used')
  if unused_bib:
    printlog(f'unused bibliography entries ({len(unused_bib)}):')
    for key in unused_bib:
      print('  -', key)
  else:
    printlog('no unused bibliography entries found')

  if undefined_cites:
    printlog(f'WARNING: undefined citations used but not in bib ({len(undefined_cites)}):')
    for key in undefined_cites:
      print('  -', key)
  else:
    printlog('no undefined citations found')

  # Figures
  tex_figs = collect_figure_tex_names()
  image_figs = collect_figure_image_names()
  used_figs = collect_used_figures(tex_files)
  unused_tex_figs = sorted(tex_figs - used_figs)
  unused_image_figs = sorted(image_figs - used_figs)

  printlog(f'figure .tex files: {len(tex_figs)} available, {len(tex_figs - set(unused_tex_figs))} referenced')
  if unused_tex_figs:
    printlog(f'unused .tex figures ({len(unused_tex_figs)}):')
    for name in unused_tex_figs:
      print('  -', name)
  else:
    printlog('no unused .tex figures found')

  printlog(f'figure image files: {len(image_figs)} available, {len(image_figs - set(unused_image_figs))} referenced')
  if unused_image_figs:
    printlog(f'unused image figures ({len(unused_image_figs)}):')
    for name in unused_image_figs:
      print('  -', name)
  else:
    printlog('no unused image figures found')

  # Optional removal section
  if remove_unused:
    # Remove unused figure .tex files
    if unused_tex_figs:
      printlog(f'removing {len(unused_tex_figs)} unused .tex figure file(s)')
      for name in unused_tex_figs:
        path = os.path.join('figures', name + '.tex')
        if os.path.exists(path):
          if dry_run:
            print(f'  DRY: would remove {path}')
          else:
            try:
              os.remove(path)
              print(f'  removed {path}')
            except OSError as e:
              print(f'  failed to remove {path}: {e}')
    else:
      printlog('no unused .tex figures to remove')

    # Remove unused image figure files (all matching extensions)
    if unused_image_figs:
      printlog(f'removing images for {len(unused_image_figs)} unused figure base name(s)')
      for name in unused_image_figs:
        for ext in IMAGE_EXTENSIONS:
          path = os.path.join('figures', name + ext)
          if os.path.exists(path):
            if dry_run:
              print(f'  DRY: would remove {path}')
            else:
              try:
                os.remove(path)
                print(f'  removed {path}')
              except OSError as e:
                print(f'  failed to remove {path}: {e}')
    else:
      printlog('no unused image figures to remove')

    # Prune bib entries
    if unused_bib:
      bib_path = 'bib.bib'
      if not os.path.exists(bib_path):
        printlog('bib.bib not found, cannot prune bibliography')
      else:
        # Create backup
        if not dry_run:
          backup_base = bib_path + '.bak'
          backup_path = backup_base
          idx = 1
            # Ensure unique backup filename
          while os.path.exists(backup_path):
            idx += 1
            backup_path = f"{backup_base}.{idx}"
          try:
            shutil.copy2(bib_path, backup_path)
            printlog(f'backup created: {backup_path}')
          except OSError as e:
            printlog(f'failed to create backup of bib.bib: {e}')
        printlog(f'pruning {len(unused_bib)} unused bibliography entrie(s)')
        if dry_run:
          for k in unused_bib:
            print(f'  DRY: would remove entry {k}')
        else:
          try:
            with open(bib_path, 'r', encoding='utf-8', errors='ignore') as f:
              lines = f.readlines()
            output_lines = []
            i = 0
            while i < len(lines):
              line = lines[i]
              if line.lstrip().startswith('@'):
                # Attempt to capture key
                m = re.match(r'@\w+\{\s*([^,\s]+)', line.lstrip())
                if m:
                  key = m.group(1)
                  brace_depth = line.count('{') - line.count('}')
                  entry_lines = [line]
                  i += 1
                  while i < len(lines) and brace_depth > 0:
                    entry_lines.append(lines[i])
                    brace_depth += lines[i].count('{') - lines[i].count('}')
                    i += 1
                  if key in unused_bib:
                    print(f'  removed bib entry {key}')
                    continue  # skip adding to output
                  else:
                    output_lines.extend(entry_lines)
                  continue
              # default: keep line
              output_lines.append(line)
              i += 1
            with open(bib_path, 'w', encoding='utf-8') as f:
              f.writelines(output_lines)
          except OSError as e:
            printlog(f'failed pruning bibliography: {e}')
    else:
      printlog('no unused bibliography entries to prune')

  issues = (unused_bib or undefined_cites or unused_tex_figs or unused_image_figs)
  printlog('check finished: ' + ('issues detected' if issues else 'no issues detected'))
  if remove_unused:
    printlog('removal phase complete (dry run)' if dry_run else 'removal phase complete')
  return True


def main():
  parser = argparse.ArgumentParser( description = "LaTeX thesis build script" )
  subparsers = parser.add_subparsers( dest = "command" )

  thesis_parser = subparsers.add_parser( "thesis", help = "build the complete thesis" )
  thesis_parser.add_argument( "-r", "--remake", action = "store_true", help = "skip building figures" )
  thesis_parser.add_argument(
      "-gd", "--git-description", type = str, default = None, help = "git description to embed in the thesis"
      )

  chapters_parser = subparsers.add_parser( "chapters", help = "build all chapters as separate pdf files" )
  chapters_parser.add_argument( "-r", "--remake", action = "store_true", help = "skip rebuilding figures" )
  chapters_parser.add_argument(
      "-gd", "--git-description", type = str, default = None, help = "git description to embed in the thesis"
      )

  chapter_parser = subparsers.add_parser( "chapter", help = "build a specific chapter as separate pdf file" )
  chapter_parser.add_argument( "name", help = "name of the chapter to build" )
  chapter_parser.add_argument( "-r", "--remake", action = "store_true", help = "skip rebuilding figures" )
  chapter_parser.add_argument(
      "-gd", "--git-description", type = str, default = None, help = "git description to embed in the thesis"
      )

  subparsers.add_parser( "figures", help = "build all figures" )

  figure_parser = subparsers.add_parser( "figure", help = "build a specific figure" )
  figure_parser.add_argument( "name", help = "Name of the figure to build" )

  clean_parser = subparsers.add_parser( "clean", help = "clean build files" )
  clean_parser.add_argument( "name", nargs = "?", default = None, help = "clean files of that name" )

  all_parser = subparsers.add_parser( "all", help = "build thesis and all chapters" )
  all_parser.add_argument( "-r", "--remake", action = "store_true", help = "skip rebuilding figures" )
  all_parser.add_argument(
      "-gd", "--git-description", type = str, default = None, help = "git description to embed in the thesis"
      )

  check_parser = subparsers.add_parser( "check", help = "check for unused bibliography entries and figures" )
  check_parser.add_argument( "--remove-unused", action = "store_true", help = "delete unused figures and bib entries (makes backup of bib.bib)" )

  parser.add_argument( "-H", "--HELP", action = "store_true", help = "show verbose help message and exit" )
  parser.add_argument( "-v", "--verbose", action = "store_true", help = "enable verbose output" )
  parser.add_argument( "-d", "--dry-run", action = "store_true", help = "dry run, do not execute any commands" )

  help_msg = parser.format_help()
  for subparser in subparsers.choices.values():
    help_msg += "\n" + f"{'=' * 10 :^30}" + "\n\n"
    help_msg += subparser.format_help()

  args = parser.parse_args()

  if args.HELP:
    print( help_msg )
    return True

  if args.command == "clean":
    return clean( args.name )

  if args.command == "check":
    return check( verbose = args.verbose, remove_unused = getattr(args, 'remove_unused', False), dry_run = args.dry_run )

  latex_distribution = check_latex_installation()
  if latex_distribution is None:
    printlog( "latexmk not found, exiting" )
    return -1
  printlog( f"using {latex_distribution}" )

  if latex_distribution == "miktex":
    LATEX_FLAGS.extend( MIKTEX_FLAGS )

  if args.command == "thesis":
    return build_thesis(
        remake = args.remake, git_description = args.git_description, verbose = args.verbose, dry_run = args.dry_run
        )
  elif args.command == "chapters":
    return build_chapter(
        remake = args.remake, git_description = args.git_description, verbose = args.verbose, dry_run = args.dry_run
        )
  elif args.command == "chapter":
    return build_chapter(
        name = args.name,
        remake = args.remake,
        git_description = args.git_description,
        verbose = args.verbose,
        dry_run = args.dry_run
        )
  elif args.command == "figures":
    return build_figure( verbose = args.verbose, dry_run = args.dry_run )
  elif args.command == "figure":
    return build_figure( name = args.name, verbose = args.verbose, dry_run = args.dry_run )
  elif args.command == "all":
    return build_thesis(
        remake = args.remake, git_description = args.git_description, verbose = args.verbose, dry_run = args.dry_run
        ) and build_chapter(
        remake = True, git_description = args.git_description, verbose = args.verbose, dry_run = args.dry_run
        )
  else:
    print( help_msg )
    return True


if __name__ == "__main__":
  success = main()
  exit( 0 if success else 1 )
