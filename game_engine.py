import pandas as pd
from collections import Counter
import pprint as pp
import datetime as dt

class wordle_game:
    
    def __init__(
            self,
            game_num: int,
            folder: str = None,
            filename: str = "wordle_scores.csv",
    ):
        self.game_num = game_num
        self.round_num = 0
        self.word_letters = {
            0: { 'is': None, 'is_not': [] },
            1: { 'is': None, 'is_not': [] },
            2: { 'is': None, 'is_not': [] },
            3: { 'is': None, 'is_not': [] },
            4: { 'is': None, 'is_not': [] },           
        }
        self.good_letters = []
        self.bad_letters = []
        self.letter_freq = []
        self.filename = folder + ("\\" if folder else "") + filename
        self.new_words = pd.DataFrame()
        self.words = pd.DataFrame()
        self.results = {
            "date": "",
            "winning_round": 0,
            "word1": "",
            "w1_score": "",
            "word2": "",
            "w2_score": "",
            "word3": "",
            "w3_score": "",
            "word4": "",
            "w4_score": "",
            "word5": "",
            "w5_score": "",
            "word6": "",
            "w6_score": "",
        }
        
    def load_data(self, folder: str, filename: str):
        self.words = pd.read_csv(f"{folder}/{filename}")
        print(f"Words in corpus {self.words.shape[0]}")

    def prep_data(self):
        self.new_words = self.words[self.words['word'].str.len() == 5].copy().reset_index()

        total_count = sum(self.new_words['count'])
        probs = [x / total_count for x in self.new_words['count']]
        self.new_words['prob'] = probs

        print(f"Count of 5 Letter Words {self.new_words.shape[0]}")
        print("Highest frequency 5 letter words")
        print(self.new_words.head(10))

        self.get_letter_freq()
        print("Highest frequency letters")
        print(self.letter_freq.most_common(10))
        
    def recommend_next(
            self,
            dupe_letters: bool = True,
            options: int = 50,
            display: int = 10
    ):
        # compute score for each of the top X words
        ranked_words = []
        print(f"\nRemaining word count {self.new_words.shape[0]}")
        
        for index, this_row in self.new_words[:options].iterrows():
            score = 0
            this_word = this_row['word']

            c = Counter(this_word)
            if dupe_letters or max(c.values()) == 1:
                for this_letter in this_word:
                    score += self.letter_freq[this_letter]

            score = round(score * this_row['prob'], 2)
            ranked_words.append([this_word, score])
            
        pp.pprint(ranked_words[:display])
              
    def get_letter_freq(self):
        """
        Get all words and combine them into one long string
        Then use Counter to get the frequency of each letter
        """
        all_words = "".join(self.new_words['word'])
        self.letter_freq = Counter(all_words)

    def build_rules(self, guess):
        word = guess[0]
        results = guess[1]

        assert len(word) == 5; f"{word} is not 5 letters long"
        assert len(results) == 5; f"{results} is not 5 positions long"
        for i in range(5):
            result = results[i]
            letter = word[i]
            error_msg = (
                f"scoring letter {letter} invalid; "
                "allowed:\n"
                "\tx: letter not in word\n"
                "\ty: letter in word, wrong position\n"
                "\tc: letter in the correct position"
            )
            assert result in ['g', 'y', 'c'], error_msg

            if result == 'c':
                self.word_letters[i]['is'] = letter
                if letter not in self.good_letters:
                    self.good_letters.append(letter)
            elif result == 'y':
                self.word_letters[i]['is_not'].append(letter)
                if letter not in self.good_letters:
                    self.good_letters.append(letter)
            else:
                if letter not in self.bad_letters:
                    self.bad_letters.append(letter)

    def remove_bad_words(self):
        pattern = ""
        for i in range(len(self.bad_letters)-1):
            pattern += f"{self.bad_letters[i]}|"
        pattern += f"{self.bad_letters[-1]}"
        self.new_words = self.new_words[~self.new_words['word'].str.contains(pattern, case=False)]

    def words_with_good_letters(self):
        # cut down to only the words containing all of the good letters
        for i in range(len(self.good_letters)):
            self.new_words = self.new_words[self.new_words['word'].str.contains(self.good_letters[i], case=False)]
        # self.new_words.reset_index(inplace=True)
        
    def letters_in_correct_place(self):
        # now we can iterate across this smaller list to check placement of the correct letters
        keep_rows = []
        for _, row in self.new_words.iterrows():
            keep = True
            for i in range(5):
                if self.word_letters[i]['is'] is not None:
                    if row['word'][i] != self.word_letters[i]['is']:
                         keep = False
                elif row['word'][i] in self.word_letters[i]['is_not']:
                    keep=False

            if keep:
                keep_rows.append(row)

        self.new_words = pd.DataFrame(keep_rows)

    def show_results(self):
        print(f"\nRound Number {self.round_num}")
        print("\n")
        pp.pprint(f"Correct= {self.word_letters}")
        pp.pprint(f"Good\t= {self.good_letters}")
        pp.pprint(f"Bad\t= {self.bad_letters}")
        # print(f"\tRemaining Words = {self.new_words.shape[0]}")
        # print(self.letter_freq.most_common(10))
        # print(self.new_words.head(10))
    
    def save_results(self, first_round: bool = False):
        this_results_df = pd.DataFrame(self.results, index=[self.game_num])
        try:
            with pd.read_csv(self.filename) as df:
                if self.round_num > 1:
                    df.iloc[-1].drop()
                df = pd.concat([df, this_results_df])
                if self.round_num > 1:
                    df = df.iloc[:-1 , :]
                df.to_csv(self.filename)
        except:
            this_results_df.to_csv(self.filename)
    
    def new_round(self, guesses: dict, round_num: int = None):
        if round_num:
            self.round_num = round_num
        else:
            self.round_num += 1

        guess = guesses[self.round_num]
        word, results = guess
        self.results["date"]=dt.date.today()
        self.results[f"word{self.round_num}"] = word
        self.results[f"w{self.round_num}_score"] = results
        
        if results != 'ccccc':
            if self.round_num < 6:
                self.build_rules(guess)
                self.remove_bad_words()
                self.words_with_good_letters()
                self.letters_in_correct_place()
                self.get_letter_freq()
                self.show_results()
            else:
                print(
                    f"\nFailed to find word in 6 round limit :(\n"
                    # f"Win ratio is {}
                )
        else:
            self.results["winning_round"] = self.round_num
            print(f"\nCongrats!  Victory in round {self.round_num}")

        self.save_results()
