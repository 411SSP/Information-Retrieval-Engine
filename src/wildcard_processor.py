class PermutermIndex:
    def __init__(self):
        self.index = {}

    def add_term(self, term):
        term_dollar = term + "$"
        for i in range(len(term_dollar)):
            rotation = term_dollar[i:] + term_dollar[:i]
            self.index[rotation] = term

    def get_matches(self, wildcard_query):
        # Handles queries with a single '*' like 'mach*' or '*ing'
        parts = wildcard_query.split('*')
        if len(parts) != 2:
            return [wildcard_query]
            
        prefix = parts[1] + "$" + parts[0]
        
        matches = set()
        for rotation, original in self.index.items():
            if rotation.startswith(prefix):
                matches.add(original)
        return list(matches)
