# It seems I forgot to import the required libraries. Let's do that and continue.
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from argparse import ArgumentParser



parser = ArgumentParser()
parser.add_argument("filename")

args = parser.parse_args()

# Load the new data containing the Temp = 0.6
data = pd.read_csv(args.filename)

# Replotting the boxplot for HeadScore (binary) by Temp with the new data including Temp = 0.6
plt.figure(figsize=(10, 6))
ax = sns.violinplot(x='PromptID', y='HeadScore', data=data)
ax.set_xticklabels(['Basic', 'Context', 'Constrained', 'Few Shot GPT-4o', "Few shot GPT-4o-mini"])

# Set the title and labels
plt.title('HeadScore  vs Prompts, Temp = 0.4')
plt.xlabel('Prompts')
plt.ylabel('HeadScore')

# Save the plot
plt.savefig("BERT/one_file_vector/plots/HeadScorePrompt.pdf", format="pdf")

# Let's create boxplots for UT, UT1, and UT2 by Temp with the new dataset including Temp = 0.6

# Plot the boxplot for UT by Temp
plt.figure(figsize=(12, 8))


plt.subplot(3, 1, 1)
ax = sns.violinplot(x='PromptID', y='UT', data=data)
ax.set_xticklabels(['Basic', 'Context', 'Constrained', 'Few Shot GPT-4o', "Few shot GPT-4o-mini"])
plt.title('UT vs Prompts, Temp = 0.4')
plt.xlabel('Prompt')
plt.ylabel('UT')

# Plot the boxplot for UT1 by Temp
plt.subplot(3, 1, 2)
ax = sns.violinplot(x='PromptID', y='UT1', data=data)
ax.set_xticklabels(['Basic', 'Context', 'Constrained', 'Few Shot GPT-4o', "Few shot GPT-4o-mini"])
plt.title('UT1 vs Prompts, Temp=0.4')
plt.xlabel('Prompt')
plt.ylabel('UT1')

# Plot the boxplot for UT2 by Temp
plt.subplot(3, 1, 3)
ax = sns.violinplot(x='PromptID', y='UT2', data=data)
ax.set_xticklabels(['Basic', 'Context', 'Constrained', 'Few Shot GPT-4o', "Few shot GPT-4o-mini"])
plt.title('UT2 vs Prompts, Temp=0.4')
plt.xlabel('Prompt ID')
plt.ylabel('UT2')


# Adjust layout to avoid overlap
plt.tight_layout()
plt.savefig("BERT/one_file_vector/plots/UTPrompt.pdf", format="pdf")
