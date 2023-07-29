from random import randrange

alphabet = 'abcdefghijklmnopqrstuvwxyz'

Word = 'aaaaaa'

length = len(Word)

while 1:
    word = ''
    for j in range(length):
        word += alphabet[randrange(len(alphabet))]

    if word == Word:
        print('Found %s:%s' % (Word, word))
        break
