__author__ = 'bwall'
import markovobfuscate.obfuscation as obf
import logging
import re
import random

"""
In some cases, the shared data (book) by both models will not be robust enough to provide enough transitions in states.
This can be caused by very short books, or by books with a very sparse vocabulary.  To test this, we simply push random
values through the engine.  There is probably a nice scientific way to do this, but I've been holding off of pushing
to this project until I resolved this, and its been quite a while.
"""

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    from argparse import ArgumentParser

    parser = ArgumentParser(
        prog=__file__,
        description="Random testing on datasets for markovobfuscate",
    )
    parser.add_argument('book', metavar='path', type=str, default="datasets/98.txt",
                        help="Paths to files or directories to scan")
    parser.add_argument('split', metavar='regex', type=str, default=r'\n')

    args = parser.parse_args()

    for y in xrange(256):
        for x in xrange(256):
            p = obf.MarkovKeyState.char_to_base(x, 16) + obf.MarkovKeyState.char_to_base(y, 16)
            o = obf.MarkovKeyState.base_to_chars(p, 16)
            if o != [x, y]:
                print p
                print o
                print x
                raise

    # Regular expression to split our training files on
    split_regex = args.split

    # File/book to read for training the Markov model (will be read into memory)
    training_file = args.book

    # Obfuscating Markov engine
    m1 = obf.MarkovKeyState()
    m2 = obf.MarkovKeyState()

    # Read the shared key into memory
    with open(training_file, "r") as f:
        text = f.read()

    # Split learning data into sentences, in this case, based on periods.
    map(m1.learn_sentence, re.split(split_regex, text))
    map(m2.learn_sentence, re.split(split_regex, text))

    try:
        logging.info("Hit CTRL-C to stop testing")
        passed = 0
        while True:
            # Run a random test
            rand_string = "".join([chr(random.randint(0, 255)) for k in xrange(random.randint(1, 1024))])
            p = m1.obfuscate_string(rand_string)
            if rand_string != m2.deobfuscate_string(p):
                print [rand_string], [m2.deobfuscate_string(p)]
                logging.info("Failed integrity test")
                raise
            else:
                passed += 1
                logging.info("Passed {0} tests".format(passed))
    except KeyboardInterrupt:
        pass