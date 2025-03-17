compiler = latexmk

TEXLIVE := $(shell if ls -la ~ | grep -q texlive; then echo yes; else echo no; fi)
MIKTEX := $(shell if ls -la ~ | grep -q miktex; then echo yes; else echo no; fi)

latex_flags = 

ifeq ($(TEXLIVE),yes)
latex_flags = -output-directory="build" --shell-escape -interaction=nonstopmode -file-line-error
endif

ifeq ($(MIKTEX),yes)
latex_flags = -output-directory="build" -pdf --shell-escape -interaction=nonstopmode -file-line-error --max-print-line=10000 --extra-mem-top=10000000 --main-memory=10000000 --extra-mem-bot=10000000
endif

all: thesis chapters

thesis: thesis.tex ensure_compiler ensure_output_directories 
	@echo compiling thesis ...
	@$(compiler) thesis.tex $(latex_flags)
	@mv build/thesis.pdf out/thesis.pdf
	@echo thesis compiled successfully to out/thesis.pdf

chapters: chapters/*.tex chapter.tex ensure_compiler ensure_output_directories 
	@for file in chapters/*.tex; do 								\
		echo compiling chapter $$basename ...; 						\
		basename=$$(basename "$$file" .tex); 						\
		sed -i "s/PLACEHOLDER/$$basename/g" chapter.tex; 			\
		$(compiler) chapter.tex $(latex_flags); 					\
		sed -i "s/$$basename/PLACEHOLDER/g" chapter.tex; 			\
		mv build/chapter.pdf out/$$basename.pdf; 					\
		echo thesis compiled successfully to out/$$basename.pdf; 	\
	done

chapter: chapter.tex ensure_compiler ensure_output_directories
	@if [ -z "$(CHAPTER)" ]; then 											\
		echo "Error: Please specify a chapter with CHAPTER=chapter_name"; 	\
		echo "Example: make chapter CHAPTER=introduction"; 					\
		exit 1; 															\
	fi
	@if [ ! -f "chapters/$(CHAPTER).tex" ]; then 							\
		echo "Error: Chapter file chapters/$(CHAPTER).tex does not exist"; 	\
		exit 1; 															\
	fi
	@echo compiling chapter $(CHAPTER) ...
	@sed -i "s/PLACEHOLDER/$(CHAPTER)/g" chapter.tex
	@$(compiler) chapter.tex $(latex_flags)
	@mv build/chapter.pdf out/$(CHAPTER).pdf
	@sed -i "s/$(CHAPTER)/PLACEHOLDER/g" chapter.tex
	@echo thesis compiled successfully to out/$(CHAPTER).pdf

clean:
	@rm -r build
	@rm -r out

cleanup:
	@rm -r build

ensure_output_directories:
	@mkdir -p build out

ensure_compiler:
	@if [ "$(TEXLIVE)" = "no" ] && [ "$(MIKTEX)" = "no" ]; then 	\
		echo "Error: No LaTeX distribution found"; 					\
		echo "Please install either TeXLive or MikTeX"; 			\
		exit 1; 													\
	fi
