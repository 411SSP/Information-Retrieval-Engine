def edit_distance(s1, s2):
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0:
                dp[i][j] = j
            elif j == 0:
                dp[i][j] = i
            elif s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(dp[i][j-1], dp[i-1][j], dp[i-1][j-1])
                
    return dp[m][n]

class SpellingCorrector:
    def __init__(self, vocabulary):
        self.vocabulary = set(vocabulary)

    def correct(self, word):
        if word in self.vocabulary:
            return word
            
        best_match = word
        min_dist = float('inf')
        
        for vocab_word in self.vocabulary:
            dist = edit_distance(word, vocab_word)
            if dist < min_dist:
                min_dist = dist
                best_match = vocab_word
                
        # Only correct if it's reasonably close (distance <= 2)
        if min_dist <= 2:
            return best_match
        return word
