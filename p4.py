# Accept a paragraph from the user
paragraph = input("Enter a paragraph: ")

# Split paragraph into words and store them in a list
words = paragraph.split()

# Calculate required values
total_words = len(words)
unique_words = len(set(words))

# Find longest and shortest words
longest_word = max(words, key=len)
shortest_word = min(words, key=len)

# Display the results
print("\n--- Result ---")
print("Total number of words:", total_words)
print("Number of unique words:", unique_words)
print("Longest word:", longest_word)
print("Shortest word:", shortest_word)
