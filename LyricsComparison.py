import re
from collections import Counter
import string
from difflib import SequenceMatcher

class LyricsComparator:
    def __init__(self):
        pass

    def preprocess_text(self, text):
        if not text:
            return []

        # Convert to lowercase
        text = text.lower()

        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))

        # Split into words and remove extra whitespace
        words = text.split()

        return words

    def calculate_wer(self, reference, hypothesis):
        ref_words = self.preprocess_text(reference)
        hyp_words = self.preprocess_text(hypothesis)

        if not ref_words:
            return 100.0 if hyp_words else 0.0

        # Calculate edit distance using dynamic programming
        d = [[0 for _ in range(len(hyp_words) + 1)] for _ in range(len(ref_words) + 1)]

        for i in range(len(ref_words) + 1):
            d[i][0] = i

        for j in range(len(hyp_words) + 1):
            d[0][j] = j

        for i in range(1, len(ref_words) + 1):
            for j in range(1, len(hyp_words) + 1):
                if ref_words[i-1] == hyp_words[j-1]:
                    d[i][j] = d[i-1][j-1]
                else:
                    substitution = d[i-1][j-1] + 1
                    insertion = d[i][j-1] + 1
                    deletion = d[i-1][j] + 1
                    d[i][j] = min(substitution, insertion, deletion)

        wer = (d[len(ref_words)][len(hyp_words)] / len(ref_words)) * 100
        return min(wer, 100.0)

    def calculate_bow_f1(self, reference, hypothesis):
        ref_words = self.preprocess_text(reference)
        hyp_words = self.preprocess_text(hypothesis)

        if not ref_words and not hyp_words:
            return 100.0

        if not ref_words or not hyp_words:
            return 0.0

        ref_counter = Counter(ref_words)
        hyp_counter = Counter(hyp_words)

        # Calculate intersection (common words with minimum count)
        intersection = ref_counter & hyp_counter
        intersection_count = sum(intersection.values())

        # Calculate precision and recall
        precision = intersection_count / sum(hyp_counter.values()) if sum(hyp_counter.values()) > 0 else 0
        recall = intersection_count / sum(ref_counter.values()) if sum(ref_counter.values()) > 0 else 0

        # Calculate F1 score
        if precision + recall == 0:
            return 0.0

        f1 = (2 * precision * recall) / (precision + recall)
        return f1 * 100

    def get_bigrams(self, words):
        if len(words) < 2:
            return []
        return [(words[i], words[i+1]) for i in range(len(words) - 1)]

    def calculate_bigram_f1(self, reference, hypothesis):
        ref_words = self.preprocess_text(reference)
        hyp_words = self.preprocess_text(hypothesis)

        ref_bigrams = self.get_bigrams(ref_words)
        hyp_bigrams = self.get_bigrams(hyp_words)

        if not ref_bigrams and not hyp_bigrams:
            return 100.0

        if not ref_bigrams or not hyp_bigrams:
            return 0.0

        ref_bigram_counter = Counter(ref_bigrams)
        hyp_bigram_counter = Counter(hyp_bigrams)

        # Calculate intersection
        intersection = ref_bigram_counter & hyp_bigram_counter
        intersection_count = sum(intersection.values())

        # Calculate precision and recall
        precision = intersection_count / sum(hyp_bigram_counter.values()) if sum(hyp_bigram_counter.values()) > 0 else 0
        recall = intersection_count / sum(ref_bigram_counter.values()) if sum(ref_bigram_counter.values()) > 0 else 0

        # Calculate F1 score
        if precision + recall == 0:
            return 0.0

        f1 = (2 * precision * recall) / (precision + recall)
        return f1 * 100

    def calculate_semantic_similarity(self, reference, hypothesis):
        ref_words = set(self.preprocess_text(reference))
        hyp_words = set(self.preprocess_text(hypothesis))

        if not ref_words and not hyp_words:
            return 100.0

        if not ref_words or not hyp_words:
            return 0.0

        # Simple Jaccard similarity
        intersection = len(ref_words & hyp_words)
        union = len(ref_words | hyp_words)

        if union == 0:
            return 0.0

        return (intersection / union) * 100

    def compare_lyrics(self, transcribed_lyrics, reference_lyrics):
        if not transcribed_lyrics and not reference_lyrics:
            return {
                'wer': 0.0,
                'bow_f1': 100.0,
                'bigram_f1': 100.0,
                'semantic_similarity': 100.0,
                'overall_score': 100.0,
                'detailed_analysis': "Both inputs are empty"
            }

        if not transcribed_lyrics:
            return {
                'wer': 100.0,
                'bow_f1': 0.0,
                'bigram_f1': 0.0,
                'semantic_similarity': 0.0,
                'overall_score': 0.0,
                'detailed_analysis': "No transcribed lyrics provided"
            }

        if not reference_lyrics:
            return {
                'wer': 100.0,
                'bow_f1': 0.0,
                'bigram_f1': 0.0,
                'semantic_similarity': 0.0,
                'overall_score': 0.0,
                'detailed_analysis': "No reference lyrics provided"
            }

        # Calculate all metrics
        wer = self.calculate_wer(reference_lyrics, transcribed_lyrics)
        bow_f1 = self.calculate_bow_f1(reference_lyrics, transcribed_lyrics)
        bigram_f1 = self.calculate_bigram_f1(reference_lyrics, transcribed_lyrics)
        semantic_similarity = self.calculate_semantic_similarity(reference_lyrics, transcribed_lyrics)

        # Calculate overall score (weighted average)
        wer_score = max(0, 100 - wer)  # Convert WER to accuracy score
        overall_score = (
            wer_score * 0.4 +           # 40% weight for WER accuracy
            bow_f1 * 0.3 +              # 30% weight for bag of words F1
            bigram_f1 * 0.2 +           # 20% weight for bigram F1
            semantic_similarity * 0.1    # 10% weight for semantic similarity
        )

        # Generate detailed analysis
        analysis_parts = []

        if wer <= 20:
            analysis_parts.append("Excellent word accuracy")
        elif wer <= 40:
            analysis_parts.append("Good word accuracy")
        elif wer <= 60:
            analysis_parts.append("Moderate word accuracy")
        else:
            analysis_parts.append("Low word accuracy")

        if bow_f1 >= 80:
            analysis_parts.append("strong vocabulary match")
        elif bow_f1 >= 60:
            analysis_parts.append("good vocabulary match")
        elif bow_f1 >= 40:
            analysis_parts.append("moderate vocabulary match")
        else:
            analysis_parts.append("weak vocabulary match")

        if bigram_f1 >= 70:
            analysis_parts.append("good phrase structure")
        elif bigram_f1 >= 40:
            analysis_parts.append("moderate phrase structure")
        else:
            analysis_parts.append("weak phrase structure")

        detailed_analysis = ", ".join(analysis_parts)

        return {
            'wer': wer,
            'bow_f1': bow_f1,
            'bigram_f1': bigram_f1,
            'semantic_similarity': semantic_similarity,
            'overall_score': overall_score,
            'detailed_analysis': detailed_analysis.capitalize(),
            'word_count_ref': len(self.preprocess_text(reference_lyrics)),
            'word_count_hyp': len(self.preprocess_text(transcribed_lyrics))
        }

    def get_performance_grade(self, overall_score):
        if overall_score >= 90:
            return "A+"
        elif overall_score >= 85:
            return "A"
        elif overall_score >= 80:
            return "A-"
        elif overall_score >= 75:
            return "B+"
        elif overall_score >= 70:
            return "B"
        elif overall_score >= 65:
            return "B-"
        elif overall_score >= 60:
            return "C+"
        elif overall_score >= 55:
            return "C"
        elif overall_score >= 50:
            return "C-"
        elif overall_score >= 45:
            return "D+"
        elif overall_score >= 40:
            return "D"
        else:
            return "F"

# Test function
def test_comparator():
    comparator = LyricsComparator()

    reference = "Hello world this is a test"
    hypothesis = "Hello world this is test"

    results = comparator.compare_lyrics(hypothesis, reference)

    print("=== Lyrics Comparison Test ===")
    print(f"Reference: {reference}")
    print(f"Hypothesis: {hypothesis}")
    print(f"WER: {results['wer']:.1f}%")
    print(f"Bag of Words F1: {results['bow_f1']:.1f}%")
    print(f"Bigram F1: {results['bigram_f1']:.1f}%")
    print(f"Overall Score: {results['overall_score']:.1f}%")
    print(f"Grade: {comparator.get_performance_grade(results['overall_score'])}")
    print(f"Analysis: {results['detailed_analysis']}")

if __name__ == "__main__":
    test_comparator()