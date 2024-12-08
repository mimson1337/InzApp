import Levenshtein


def calculate_similarity_levenshtein(text1, text2):
    return Levenshtein.ratio(text1, text2) * 100


# Texts for comparison
text1 = "Original transcription text"
text2 = "Whisper model transcription"

# Calculating similarity
similarity = calculate_similarity_levenshtein(text1, text2)
print(f"Podobieństwo: {similarity:.2f}%")
