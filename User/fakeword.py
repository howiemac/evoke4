# from http://www.evanfosmark.com/2009/07/creating-fake-words/
import random

vowels = ["a", "e", "i", "o", "u"]
consonants = ['b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'q',
              'r', 's', 't', 'v', 'w', 'x', 'y', 'z']

def _vowel():
    return random.choice(vowels)

def _consonant():
    return random.choice(consonants)

def _cv():
    return _consonant() + _vowel()

def _cvc():
    return _cv() + _consonant()

def _syllable():
    return random.choice([_vowel, _cv, _cvc])()

def create_fake_word():
    """ This function generates a fake word by creating between two and three
        random syllables and then joining them together.
    """
    syllables = []
    for x in range(random.randint(2,3)):
        syllables.append(_syllable())
    return "".join(syllables)

def fakeword():
  "find one at least 4 characters long"
  res = ''
  while len(res)<4:
    res = create_fake_word()
  return res

def fakepassword():
  "words, digits, numbers"
  res = ([fakeword().capitalize(), fakeword().capitalize(), str(int(random.uniform(0,100))), random.choice('!@#$%^&*(){}/=?+-_')])
  random.shuffle(res)
  return ''.join(res)


if __name__ == "__main__":
    print fakepassword()

