import datetime
import linecache
import time
from os import path
from random import choice
from tkinter import Tk
from tkinter.filedialog import askopenfilename

import matplotlib.pyplot as plt
import numpy
from matplotlib.dates import datestr2num
from scipy import stats


# Compares two strings taking in count small errors
def compare(first, second):
    score = 0
    first = [i for i in first]
    second = [i for i in second]
    lengfi = len(first)  # lenght of the first string
    lengse = len(second)  # lenght of the second string

    # We need to prevent out of index error by appending blank spaces
    while lengfi < lengse:
        first.append(" ")
        lengfi = len(first)

    while lengse < lengfi:
        second.append(" ")
        lengse = len(second)

    for i, j in zip(range(lengfi), range(lengse)):
        if first[i] == second[j]:
            score += 1
        elif i+1 <= lengse - 1:
            if first[i+1] == second[j]:
                score += 0.5
                i += 1
        elif i > 0:
            if first[i-1] == second[j]:
                score += (1/3)
                i -= 1
    try:
        return score/lengfi
    except ZeroDivisionError:
        print("No phrase")
        return -1


# Function for adding new string to the storage
def add_word():
    while 1:
        phrase = input("Enter new phrase: ")
        i = volume_storage()

        with open("storage.txt", "a") as file:
            new_word = ";".join([str(i+1), phrase, "1", "\n"])
            file.write(new_word)

        command = input("another phrase?(y/n): ")

        if command == "n" or command == "N":
            break


# Deletes word from the storage
def del_word():
    while 1:
        index = int(input("Enter index of phrase you want delete: "))
        if type(index) == int:
            break
        print("You need to enter the intiger...\n")

    with open("storage.txt", "r") as file:
        lines = file.readlines()

    with open("storage.txt", "w") as file:
        for line in lines:
            line = line.split(";")

            if int(line[0]) < index:
                file.write(';'.join(line))
            elif int(line[0]) > index:
                rest = ';'.join(line[1:])
                line = ';'.join([str(int(line[0])-1), rest])
                file.write(line)


def add_score(score):
    today = str(datetime.date.today())

    if path.isfile("scores.txt"):
        with open("scores.txt", "a") as f:
            f.write(''.join([today, ';', score, ';\n']))
    else:
        with open("scores.txt", "+a") as f:
            f.write(''.join([today, ';', score, ';\n']))


# main fuction for gameplay
def game():
    timed = []
    accuracy = []
    print("Repeat the sentence the fastest you can!")
    volume = volume_storage()
    weighteddecision = weightedseed()

    if volume == 0:
        print("Storage is empty!")
    else:
        i = 1
        while i <= 5:
            index = choice(weighteddecision)
            line = linecache.getline("storage.txt", index)
            mark = 0
            lst = []

            for vovel in line:
                if vovel == ";":
                    mark += 1
                else:
                    while mark == 1:
                        lst.append(vovel)
                        break

            string = ''.join(lst)
            print("Round#" + str(i))
            start = time.time()
            round = input(string+": \n")

            end = time.time()

            i += 1
            if compare(string, round) == -1:
                accuracy.append(0)
            else:
                accuracy.append(compare(string, round))
                print(compare(string, round))
                if compare(string, round) != 1:
                    with open("storage.txt", "r") as f:
                        data = f.readlines()

                    with open("storage.txt", "w") as f:
                        for line in data:
                            whole = line.split(";")
                            if string == whole[1]:
                                whole[2] = str(int(whole[2]) + 1)
                            whole = ";".join(whole)
                            f.write(whole)

            timed.append(end - start)

        t = numpy.mean(timed)+1
        a = numpy.mean(accuracy)
        points = "{0:.2f}".format((numpy.exp(-2*a+10)*10*a)/t)
        print(points)
        add_score(points)


# Check volume of storage
def volume_storage():
    with open("storage.txt", "r") as file:
        i = 0
        for line in file:
            i += 1
    return i


def print_volume():
    print(volume_storage())


# imports storage
def imp_storage():
    print("Choose your storage file in txt")
    print("Importer can manage to variactions of file structure: "
          "\n\t1# proper indexed words/phrases separated by semicolons"
          "\n\t2# words/phrases listed in up-down manner without any semicolons")
    Tk().withdraw()
    file = askopenfilename()
    with open("storage.txt", "w+") as primal:
        with open("{}".format(file), "r") as imported:
            semicolon = 0
            index = 0
            for line in imported:
                index += 1
                for char in line:
                    if char == ";":
                        semicolon += 1
                if semicolon == 0:
                    if len(line) > 1:
                        linearray = [char for char in line]
                        linearray.insert(0, "{};".format(index))
                        if "\n" in linearray:
                            linearray.insert(linearray.index("\n"), ";1;")
                        else:
                            linearray.append(";1;\n")
                        line = ''.join(linearray)
                    semicolon = 0
                    primal.write(line)
                elif semicolon == 3:
                    semicolon = 0
                    primal.write(line)
                else:
                    print("You've tied to import wrong format."
                          "\nPlease check if your file is supported")


# analyze highscores, plot
def analyze():
    previous_day = 0
    lst_dates = []  # zrobić sprwdzanie powtórzeń, jeśli są zmienić w jeden z uśrednionym scorem
    lst_scores = []

    with open("scores.txt", "r") as f:
        for line in f:
            whole = line.split(";")
            if len(whole) > 1:
                lst_dates.append(whole[0])
                lst_scores.append(float(whole[1]))
            else:
                print("Invalid Data Occured")

    i = 0
    while i < len(lst_dates):
        dates_splitted = [letter for letter in lst_dates[i]]

        stryear = ''.join(dates_splitted[:4])
        strmonth = ''.join(dates_splitted[5:7])
        strday = ''.join(dates_splitted[8:])

        year = int(stryear)
        month = int(strmonth)
        day = int(strday)

        try:
            datetime.datetime(year, month, day)
            if i > 0:
                if day != previous_day+1:
                    if day == previous_day:
                        i -= 1
                        lst_scores[i+1] = float("{0:.2f}".format((lst_scores[i+1]+lst_scores[i])/2))
                        lst_scores.pop(i)
                        lst_dates.pop(i)

                    elif day > previous_day+1:
                        difference = day - previous_day

                        for j in range(1, difference):
                            lst_scores.insert(i, float("{0:.2f}".format((lst_scores[i-1]+lst_scores[i])/2)))
                            tmp = previous_day+j
                            if len(str(tmp)) < 2:
                                lst_dates.append(''.join([stryear, "-", strmonth, "-", "0", str(tmp)]))
                            else:
                                lst_dates.append(''.join([stryear, "-", strmonth, "-", str(tmp)]))
            previous_day = day
            lst_dates = sorted(lst_dates)
            i += 1

        except ValueError:
            print("Your highscores storage got corrupted.\nPlease delete it with Clear")
            exit(0)

    with open("scores.txt", "w+") as f:
        for i in range(len(lst_dates)):
            f.write("".join([lst_dates[i], ";", str(lst_scores[i]), ";\n"]))

    for index in range(len(lst_dates)):
        lst_dates[index] = datestr2num(lst_dates[index])

    fig, ax = plt.subplots()
    fig.autofmt_xdate()
    plt.plot_date(lst_dates, lst_scores, 'g-')
    plt.yticks(numpy.arange(min(lst_scores), max(lst_scores), 250))
    slope, intercept, r_value, p_value, std_err = stats.linregress(lst_dates, lst_scores)
    y = [slope * x + intercept for x in lst_dates]
    ax.plot(lst_dates, y, "r--")
    plt.show()


# deletes databases
def clear():
    command = input("Clear the storage press: 'S'\nClear the highscores press: 'H'\nCancel press: 'C'")
    if command.upper() == "S":
        with open("storage.txt", "w+") as file:
            pass
    elif command.upper() == "H":
        with open("scores.txt", "w+") as file:
            pass


def weightedseed():
    weightedrange = []
    with open("storage.txt", "r") as f:
        lines = f.readlines()
        for line in lines:
            whole = line.split(";")
            for i in range(int(whole[2])):
                weightedrange.append(int(whole[0]))
    return weightedrange


# Ask for C/C++ support
def optimize():
    pass


# shows highscores
def show_highscores():
    highscores = []
    with open("scores.txt", "r") as f:
        for line in f:
            score = line.split(";")
            score.pop(2)
            score.reverse()
            highscores.append(score)
    highscores.sort(reverse=True)
    if len(highscores) >= 5:
        for i in range(5):
            print('||'.join(highscores[i]))
    else:
        print("Storage is to small, play more!")


# operational part of the program
while 1:
    dic = {"P": game, "S": show_highscores, "N": add_word, "D": del_word,
           "A": analyze, "V": print_volume, "I": imp_storage, "C": clear, "E": exit}

    command = input('Play: "P"\nHighscores: "S"\nNew word: "N"\nDelete word: "D"'
                    '\nAnalyze: "A"\nCheck Volume: "V"\nImport Storage: "I"\nClear Storage: "C"\nEnd: "E"\n')

    if command.upper() in dic:
        dic[command.upper()]()
