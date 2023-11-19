# Use the base LaTeX image
FROM blang/latex

# Set a working directory within the container
WORKDIR /app

# Copy your LaTeX document into the container
COPY main.tex developercv.cls /app/

# Compile the LaTeX document using pdflatex
CMD ["pdflatex", "main.tex"]
