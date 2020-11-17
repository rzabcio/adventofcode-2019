#!/bin/python
# -*- coding: utf-8 -*-

import fire
import functools
import logging
import os


# LOGGING UTILS ###############################################################
loggingInitialized = False
globalDebug = True


def initLogging(debug=False):
    global globalDebug
    globalDebug = debug
    global loggingInitialized
    if not loggingInitialized:
        if not os.path.exists('logs'):
            os.makedirs('logs')
        # logFormat = '%(filename)15s:%(lineno)4s %(levelname)6s:%(message)s'
        logFormat = ('[%(asctime)s] [%(levelname)7s] '
                     + '[%(filename)17s:%(lineno)-4s] %(message)s ')
        logging.basicConfig(
            filename='logs/puzzles.log',
            level=logging.DEBUG,
            format=logFormat)

        # QUETING REQUESTS ###################################################
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)

        # CONSOLE HANDLER
        console_handler = logging.StreamHandler()
        if debug:
            console_handler.setLevel(logging.DEBUG)
            console_handler.setFormatter(logging.Formatter(logFormat))
        else:
            console_handler.setLevel(logging.INFO)
        logging.getLogger().addHandler(console_handler)

        loggingInitialized = True
        logging.info('')


# input tools
def fileLineGenerator(input):
    with open(input) as file:
        for line in file:
            yield line.strip()


def modulesMasses(input='input-data/input-day1-modules-masses.txt'):
    return map(int, fileLineGenerator(input))


# puzzle functions and classes
def calcFuelForModuleMass(x):
    x = int(x)
    result = x // 3 - 2
    return result


def calcFuelForModuleAndFuel(x):
    result = x // 3 - 2
    if result > 0:
        result += calcFuelForModuleAndFuel(result)
        return result
    return 0


class IntcodeComputer(object):
    originalProgram = None
    program = None

    def __init__(self, programFile='input-day2-intcode-program.txt'):
        self.originalProgram = list(map(int, open(programFile).readline().split(',')))
        logging.info("IntcodeComputer")

    def findInput(self, result):
        for noun in range(0, 99):
            for verb in range(0, 99):
                if result == self.runProgram(noun, verb):
                    return noun * 100 + verb
        return None

    def runProgram(self, noun, verb):
        self.program = self.originalProgram.copy()
        self.program[1] = noun
        self.program[2] = verb
        for command in self.commandGen():
            self.runCommand(command)
        return self.program[0]

    def runCommand(self, command):
        if command[0] == 1:
            self.program[command[3]] = self.program[command[1]] + self.program[command[2]]
        elif command[0] == 2:
            self.program[command[3]] = self.program[command[1]] * self.program[command[2]]
        else:
            return False

    def commandGen(self):
        commandSize = 4
        for i in range(0, len(self.program), commandSize):
            yield self.program[i:i+commandSize]


# FIRE CLASS ##################################################################
class Puzzles(object):
    # --------------------------------------------- tests
    def test_puzzle1_1(self):
        assert self.puzzle1_1() == 3406342

    # --------------------------------------------- day 1
    def puzzle1_1(self,
                  env='gojira-prod', verbose=False):
        initLogging(debug=verbose)

        # approach 1 - naive
        # totalFuel = 0
        # for moduleMass in modulesMasses():
        #     requiredFuel = calcFuelForModuleMass(moduleMass)
        #     totalFuel += requiredFuel
        # logging.info("approach 1: %s" % (totalFuel))
        #
        # # approach 2
        # totalFuel = functools.reduce(lambda x, y: x + y, map(calcFuelForModuleMass, modulesMasses()))
        # logging.info("approach 2: %s" % totalFuel)

        # approach 3
        totalFuel = sum(map(calcFuelForModuleMass, modulesMasses()))
        logging.debug("approach 3: %s" % totalFuel)
        return totalFuel

    def puzzle1_2(self,
                  env='gojira-prod', verbose=False):
        initLogging(debug=verbose)

        # approach 1 - naive
        # totalFuel = 0
        # for moduleMass in modulesMasses():
        #     requiredFuel = calcFuelForModuleMass(moduleMass)
        #     while(requiredFuel > 0):
        #         totalFuel += requiredFuel
        #         requiredFuel = calcFuelForModuleMass(requiredFuel)
        # logging.info("approach 1: %s" % (totalFuel))
        #
        # # approach 2 - recursive
        # totalFuel = 0
        # for moduleMass in modulesMasses():
        #     requiredFuel = calcFuelForModuleAndFuel(moduleMass)
        #     totalFuel += requiredFuel
        # logging.info("approach 2: %s" % (totalFuel))

        # approach 2
        totalFuel = sum(map(calcFuelForModuleAndFuel, modulesMasses()))
        logging.debug("approach 3: %s" % totalFuel)
        return totalFuel

    # --------------------------------------------- day 2
    def puzzle2_1(self, noun, verb,
                  programFile='input-data/input-day2-intcode-program.txt',
                  env='gojira-prod', verbose=False):
        initLogging(debug=verbose)
        computer = IntcodeComputer(programFile=programFile)
        result = computer.runProgram(noun, verb)
        return result

    def puzzle2_2(self, result,
                  programFile='input-data/input-day2-intcode-program.txt',
                  env='gojira-prod', verbose=False):
        initLogging(debug=verbose)
        computer = IntcodeComputer(programFile=programFile)
        result = computer.findInput(result)
        return result

    # --------------------------------------------- day 2
    def puzzle3_1(self,
                  env='gojira-prod', verbose=False):
        initLogging(debug=verbose)

        result = 0
        return result

    # --------------------------------------------- tests only
    def test(self,
             env='gojira-prod', verbose=False):
        initLogging(debug=verbose)


###############################################################################
if __name__ == '__main__':
    fire.Fire(Puzzles)
