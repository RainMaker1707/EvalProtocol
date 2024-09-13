# Testing protocol
## Introduction
This scoring method was designed to score prompts for my master thesis.\
It will allows to compare improvement of the different version of the prompts, documents, and data used in my research.
The expected score should be 1 if all the LLM answers are expected for a certain data using a certain prompt with certain document.
All of these variables will be defined in the following document.

Also the score should be 0 if all the answer are hallucinations.
The scoring formula uses aims to penalize the hallucination against bad answers.
But a full bunch of bad answers will lead to a score of 0 too.


## Protocol
### Sample
A sample is a file used to test the LLM.
In the case of the HTTP understanding, the samples will be CSV files.
These CSV files contains an HTTP network flow containing all packet exchanged.
These sample will be forged by using WireShark to sniff the network while the requests are made.
Then the resulting PCAP files will be converted in CSV files using a PyShark script to extract the relevant information.
These data represent representative and typical network flow and some edge-cases but not all possible edge cases.

### Methods
The methods are defined by:
- The prompt used
- The sample used
- The LLM model

### Experiment
An experiment is a one shot test against the LLM using a predefined method.
So it use the same sample, prompt and LLM model.\
One shot denote a one trial experiments


### Tests
A test is based on one method. A test is the result of 10 same experiments.\
A test produces 3 variables:
- $I_1$ the number of expected answers
- $I_0$ the number of unexpected answers
- $H$ the number of hallucinations

The sum of these is equal to the total number of the tests, noted *N*.
The number 10 was chosen randomly. This number is not statically related to the results.


### Score
We can score a test *X* using the following formula:
- $Score(X) = w_0 * /frac{I_1}{N} + w_1 * /frac{I_0}{N} + w_2 * /frac{I_1}/N$
with:
- $w_0 = 1$ Full credit for good answers 
- $w_1 = 0$ No credit for bad answers
- $w_2 = -.5$ Penalty for hallucinations 