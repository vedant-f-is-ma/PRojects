beginWord = 'hit'
endWord = 'cog'
wordlist = ['hot', 'dot', 'dog', 'lot', 'log', 'cog']

beginwordlist = list(beginWord)
endwordlist = list(endWord)
counter = 0
dummylist = list()

def words_similar(string1: str, string2: str) -> bool:
    string1elements = list(string1)
    string2elements = list(string2)

    match_count = 0

    for s1 in string1elements:
        if s1 in string2elements:
                match_count += 1

    if match_count >= 2:
        return True
        
    return False

def find_matching_word(target: str, word_list: list[str]) -> str:
    for word in word_list:
        if words_similar(target, word):
            return word
    return ""

def getmatchinglist():
    counter = 0
    answerlist = list()
    for word in wordlist:
        wordelementlist = list(word)
        for letter in beginwordlist:
            if letter in wordelementlist:
                counter += 1
        if counter >= 2:
            answerlist.append(word)
        counter = 0
    return(answerlist)

getmatchinglist()
































x = '''for word in wordlist:
    print(word)
    wordlistelementlist = list(word)
    for index in range(len(wordlistelementlist)):
        print(wordlistelementlist[index])
        for letter in endwordlist:
            if letter in wordlistelementlist:
                counter += 1
                print(counter, wordlistelementlist)
        if counter == 2 and word not in dummylist:
            endwordlist = list(word)
            dummylist.append(word)
        counter = 0
        print(endwordlist)'''