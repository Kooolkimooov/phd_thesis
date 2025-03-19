compiler = latexmk

TEXLIVE := $(shell if ls -la ~ | grep -q texlive; then echo yes; else echo no; fi)
MIKTEX := $(shell if ls -la ~ | grep -q miktex; then echo yes; else echo no; fi)

latex_flags = -output-directory="build" -pdf --shell-escape -interaction=nonstopmode -file-line-error

ifeq ($(MIKTEX),yes)
latex_flags = -output-directory="build" -pdf --shell-escape -interaction=nonstopmode -file-line-error --extra-mem-top=10000000 --main-memory=10000000 --extra-mem-bot=10000000
endif

all: thesis chapters

thesis: thesis.tex figures ensure_compiler ensure_output_directories 
	@echo compiling thesis ...
	@$(compiler) thesis.tex $(latex_flags)
	@mv build/thesis.pdf out/thesis.pdf
	@echo thesis compiled successfully to out/thesis.pdf

chapters: chapter.tex figures ensure_compiler ensure_output_directories 
	@for file in chapters/*.tex; do 								\
		echo compiling chapter $$basename ...; 						\
		basename=$$(basename "$$file" .tex); 						\
		sed -i "s/PLACEHOLDER/$$basename/g" chapter.tex; 			\
		$(compiler) chapter.tex $(latex_flags); 					\
		sed -i "s/$$basename/PLACEHOLDER/g" chapter.tex; 			\
		mv build/chapter.pdf out/$$basename.pdf; 					\
		echo thesis compiled successfully to out/$$basename.pdf; 	\
	done

chapter: chapter.tex figures ensure_compiler ensure_output_directories
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

figures: figure.tex ensure_compiler ensure_output_directories
	@echo "Prebuilding all figures..."
	@for file in figures/*.tex; do 							\
		basename=$$(basename "$$file" .tex); 				\
		echo "Building figure $$basename..."; 				\
		sed -i "s/PLACEHOLDER/$$basename/g" figure.tex; 	\
		$(compiler) figure.tex $(latex_flags); 				\
		sed -i "s/$$basename/PLACEHOLDER/g" figure.tex; 	\
		echo "Figure $$basename built successfully"; 		\
	done

figure: figure.tex ensure_compiler ensure_output_directories
	@if [ -z "$(FIGURE)" ]; then 										\
		echo "Error: Please specify a figure with FIGURE=figure_name"; 	\
		echo "Example: make figure FIGURE=catenary"; 					\
		exit 1; 														\
	fi
	@if [ ! -f "figures/$(FIGURE).tex" ]; then 								\
		echo "Error: Figure file figures/$(FIGURE).tex does not exist"; 	\
		exit 1; 															\
	fi
	@echo "Building figure $(FIGURE)..."
	@sed -i "s/PLACEHOLDER/$(FIGURE)/g" figure.tex
	@$(compiler) figure.tex $(latex_flags)
	@sed -i "s/$(FIGURE)/PLACEHOLDER/g" figure.tex
	@echo "Figure $(FIGURE) built successfully to out/figures/$(FIGURE).pdf"

clean:
	@rm -r build
	@rm -r out

cleanup:
	@rm -r build

ensure_output_directories:
	@mkdir -p build/figures build/build/figures out

ensure_compiler:
	@if [ "$(TEXLIVE)" = "no" ] && [ "$(MIKTEX)" = "no" ]; then 	\
		echo "Warning: No LaTeX distribution found"; 				\
	fi
