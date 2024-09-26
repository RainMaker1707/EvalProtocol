# Evaluation metrics for C2 detection from LLM
## Introduction

## Tools
### main.py


filename

-r --retrieve

-c --custom

Incompatible options -r and -c

### plots/plot.py
The purpose of this tools is to generate plots from data we get with the main.py
This tool will only generate plots, and save it as pdf.
This tool has only one argument, which is the filepath of the scores csv.
If there is a need to change the plotting (for example using boxplot instead of violin plot) you will need to change the code directly.
All the parameters to plot it are hardcoded.


## Tests files
### Prompt

- *prompt0.md*:
- *prompt1.md*:
- *prompt2.md*:
- *prompt3.md*:
- *prompt4.md*: Is prompt 3 but using gpt-4o-mini instead of gpt-4o


### Documentation:
- *slimper0.md*: Basic and full documentation
- *slimper1.md*: Documentation without execution example
- *slimper2.md*: Documentation without heartbeat explanation.
- *slimper3.md*: DOcumentation without heartbeat explanation and without execution example



## Tests

### ChatGPT threads
### Template filling 
### Splitting
### Scoring
