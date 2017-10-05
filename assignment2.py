



if __name__ == '__main__':

    e = open("en.txt", 'r')
    d = open("de.txt", 'r')
    a = open("aligned.txt", 'r')
    en_txt = e.readlines()
    de_txt = d.readlines()
    alignments = a.readlines()