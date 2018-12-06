#!/bin/bash

# Author: Hannah O'Sullivan h.osullivan18@imperial.ac.uk
# Script: CompileLatex.sh
# Desc: General shell script to compile latex documents
# Output: PDF
# Arguments: --
# Date: Dec 2018

#First remove extention
filename="${1//.tex/}"
echo $filename

#Compile PDF
pdflatex $1
pdflatex $1
bibtex $filename
pdflatex $1
pdflatex $1
#evince $1.pdf &

#Cleanup
rm *~
rm *.aux
rm *.dvi
rm *.log
rm *.nav
rm *.out
rm *.snm
rm *.toc
rm *.bbl
rm *.blg

#Move to results directory
mv $filename.pdf ../Results/$filename.pdf
