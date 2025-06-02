from spellchecker import SpellChecker

class SpellingCorrector:
    def __init__(self, custom_words=None):
        self.spell = SpellChecker()
        if custom_words:
            self.spell.word_frequency.load_words(custom_words)

    def correct(self, query):
        words = query.split()
        corrected_words = []
        for w in words:
            if w in self.spell:
                corrected_words.append(w)
            else:
                suggestion = self.spell.correction(w)
                if suggestion is not None:
                    corrected_words.append(suggestion)
                else:
                    corrected_words.append(w)
        return " ".join(corrected_words)
