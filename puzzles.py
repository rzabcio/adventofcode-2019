#!/bin/python
# -*- coding: utf-8 -*-

import json
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

    def __init__(self, programFile='input-data/input-day2-intcode-program.txt'):
        self.originalProgram = list(map(int, open(programFile).readline().split(',')))
        logging.info("IntcodeComputer")

    def findInput(self, result):
        for noun in range(0, 99):
            for verb in range(0, 99):
                if result == self.runProgram(noun, verb):
                    return noun * 100 + verb
        return None

    def runProgram(self, noun=None, verb=None):
        self.program = self.originalProgram.copy()
        self.program[1] = noun
        self.program[2] = verb
        for command in self.commandGen():
            self.runCommand(command)
        return self.program[0]

    def runTestProgram(self, system_id=1):
        self.program = self.originalProgram.copy()
        self.input = system_id
        self.output = 0
        for command in self.commandGen():
            self.runCommand(command)
        return self.output

    def runCommand(self, command):
        # logging.info("command: %s" % command)
        if command.opcode == 1:
            logging.debug("ADD: %s + %s = %s -> [%s]" % (command.vals[0], command.vals[1], command.vals[0] + command.vals[1], command.pos))
            self.program[command.pos] = command.vals[0] + command.vals[1]
        elif command.opcode == 2:
            logging.debug("MUL: %s * %s = %s -> [%s]" % (command.vals[0], command.vals[1], command.vals[0] * command.vals[1], command.pos))
            self.program[command.pos] = command.vals[0] * command.vals[1]
        elif command.opcode == 3:
            logging.debug("INP: %s -> [%s]" % (self.input, command.pos))
            self.program[command.pos] = self.input
        elif command.opcode == 4:
            logging.debug("OUT: [%s] -> %s" % (command.pos, self.program[command.pos]))
            self.output = self.program[command.pos]
        else:
            return False

    def commandGen(self):
        command = None
        i = 0
        while not command or len(command) > 1:
            command = IntcodeCommand(self.program, i)
            yield command
            i += len(command)

    def commandSize(self, opcode):
        if opcode in [1, 2]:
            return 4
        if opcode in [3, 4]:
            return 2
        else:
            return 1


class IntcodeCommand(object):
    def __init__(self, command, start_index=0):
        self.len = None
        self.opcode = command[start_index] % 100
        self.params = [int(command[start_index]/100) % 10, int(command[start_index]/1000) % 10, int(command[start_index]/10000) % 10]
        self.args = command[start_index+1:start_index+len(self)]
        self.pos = None
        self.vals = []
        if len(self) > 1:
            self.pos = self.args[-1]
            for i in range(0, len(self)-1):
                self.vals.append(self.args[i] if self.params[i] else command[self.args[i]])  # 0 - position, 1 - immediate
        self.command = command[start_index:start_index+len(self)]

    def __len__(self):
        if not self.len:
            if self.opcode in [1, 2]:
                self.len = 4
            elif self.opcode in [3, 4]:
                self.len = 2
            else:
                self.len = 1
        return self.len

    def __str__(self):
        return "%s - opcode: %s, params: %s -> args: %s -> vals: %s => pos: %s" % (self.command, self.opcode, self.params, self.args, self.vals, self.pos)


class WireBox(object):
    info = None
    wireNo = None
    coord = None
    steps = None
    box = None

    def __init__(self, descFile='input-data/input-day3-wires.txt'):
        self.info = list(map(lambda line: line.strip().split(','), open(descFile).readlines()))
        self.wireNo = 0
        self.coord = [0, 0]
        self.steps = 0
        self.box = {}

    def construct(self):
        logging.info("constructing box...")
        for wire in self.info:
            self.wireNo += 1
            self.constructWire(wire)

    def constructWire(self, wire):
        logging.info("             wire %s..." % self.wireNo)
        self.coord = [0, 0]
        self.steps = 0
        for path in wire:
            self.constructPath(path)

    def constructPath(self, path):
        axis = 0 if path[0] in ['R', 'L'] else 1  # 0->x, 1->y
        sign = 1 if path[0] in ['U', 'R'] else -1
        delta = int(path[1:]) * sign
        for c in range(self.coord[axis]+sign, self.coord[axis]+delta, sign):
            self.coord[axis] = c
            # logging.info("  %s" % self.coord)
            self.addWire(self.coord, axis)
        self.coord[axis] += sign
        # logging.info("  %s" % self.coord)
        self.addWire(self.coord, axis, type='+')

    def addWire(self, coords, axis, type=None):
        coordsTpl = (coords[0], coords[1])
        wire = self.box.get(coordsTpl, None)
        self.steps += 1
        if wire and wire['no'] != self.wireNo:
            wire['type'] = 'X'
        else:
            wire = {}
            wire['coords'] = coords
            wire['type'] = type if type else '|' if axis else '-'
            wire['no'] = self.wireNo
            self.box[coordsTpl] = wire
        if not wire.get('steps_wire_%s' % self.wireNo, None):
            wire['steps_wire_%s' % self.wireNo] = self.steps
        wire['steps_total'] = sum([wire.get(x, 0) for x in list(map(lambda x: "steps_wire_%s" % x, range(1, self.wireNo+1)))])
        # logging.info("wire['steps_wire_%s]=%s, total: %s" % (self.wireNo, wire['steps_wire_%s' % self.wireNo], wire['steps_total']))

    def drawBox(self):
        xs = set(map(lambda tpl: tpl[0], self.box.keys()))
        ys = set(map(lambda tpl: tpl[1], self.box.keys()))
        logging.debug("xs: [%s, %s], ys: [%s,%s]" % (min(xs), max(xs), min(ys), max(ys)))
        boxDrawing = ""
        logging.info("===============")
        for y in range(max(ys), min(ys)-1, -1):
            for x in range(min(xs), max(xs)+1, 1):
                type = '.'
                wire = self.box.get((x, y), None)
                if x == 0 and y == 0:
                    type = 'o'
                elif wire:
                    type = wire['type']
                # logging.info("drawing (%s,%s) -> %s" % (x,y,type))
                boxDrawing += type
            logging.info(boxDrawing)
            boxDrawing = ""
        logging.info("===============")

    def distanceToClosestCrossing(self):
        logging.info("determining crossings...")
        crossings = dict(filter(lambda elem: elem[1]['type'] == 'X', self.box.items()))
        # logging.info("crossings [%s]:\n%s" % (len(crossings), crossings))
        return min(map(lambda coord: abs(coord[0])+abs(coord[1]), crossings))

    def minStepsToCrossing(self):
        logging.info("determining crossings...")
        crossings = dict(filter(lambda elem: elem[1]['type'] == 'X', self.box.items()))
        # logging.info("crossings [%s]:\n%s" % (len(crossings), crossings))
        return min(map(lambda crossing: crossing[1]['steps_total'], crossings.items()))


class PasswordBreaker(object):
    def __init__(self, start=0, end=999999):
        self.start = start
        self.end = end

    def passwords1(self):
        for passwd in range(self.start, self.end+1):
            passwdStr = str(passwd)
            if not self.hasDouble(passwdStr):
                continue
            if not self.hasNoLoweringNumbers(passwdStr):
                continue
            yield passwd

    def passwords2(self):
        for passwd in range(self.start, self.end+1):
            passwdStr = str(passwd)
            if not self.hasDouble(passwdStr):
                continue
            if not self.hasNoLoweringNumbers(passwdStr):
                continue
            if not self.hasOnlyDoublesRepeating(passwdStr):
                continue
            yield passwd

    def hasDouble(self, passwdStr):
        uniqueDigits = list(set(list(passwdStr)))
        return len(uniqueDigits) < len(passwdStr)

    def hasNoLoweringNumbers(self, passwdStr):
        passwdStrNumbersList = list(passwdStr)
        passwdStrNumbersList.sort()
        passwdStrSorted = "".join(passwdStrNumbersList)
        return passwdStr == passwdStrSorted

    def hasOnlyDoublesRepeating(self, passwdStr):
        passwdDigits = list(map(lambda s: int(s), list(passwdStr)))
        digitCounts = [0] * 10
        for digit in range(0, 10):
            for passwdDigit in passwdDigits:
                if digit == passwdDigit:
                    digitCounts[digit] += 1
        return any(map(lambda count: count == 2, digitCounts))


# FIRE CLASS ##################################################################
class Puzzles(object):
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

    # --------------------------------------------- day 3
    def puzzle3_1(self, descFile='input-data/input-day3-wires-test1.txt',
                  draw=False,
                  env='gojira-prod', verbose=False):
        initLogging(debug=verbose)
        wirebox = WireBox(descFile=descFile)
        wirebox.construct()
        if draw:
            wirebox.drawBox()
        result = wirebox.distanceToClosestCrossing()
        return result

    def puzzle3_2(self, descFile='input-data/input-day3-wires-test1.txt',
                  draw=False,
                  env='gojira-prod', verbose=False):
        initLogging(debug=verbose)
        wirebox = WireBox(descFile=descFile)
        wirebox.construct()
        if draw:
            wirebox.drawBox()
        result = wirebox.minStepsToCrossing()
        return result

    # --------------------------------------------- day 4
    def puzzle4_1(self, start=231832, end=767346,
                  env='gojira-prod', verbose=False):
        initLogging(debug=verbose)
        breaker = PasswordBreaker(start=start, end=end)
        result = len(list(breaker.passwords1()))
        return result

    def puzzle4_2(self, start=231832, end=767346,
                  env='gojira-prod', verbose=False):
        initLogging(debug=verbose)
        breaker = PasswordBreaker(start=start, end=end)
        result = len(list(breaker.passwords2()))
        return result

    # --------------------------------------------- day 5
    def puzzle5_1(self, system_id=1,
                  programFile='input-data/input-day5-intcode-program.txt',
                  env='gojira-prod', verbose=False):
        initLogging(debug=verbose)
        computer = IntcodeComputer(programFile=programFile)
        result = computer.runTestProgram(system_id=system_id)
        return result

    def puzzle5_2(self, system_id=1,
                  programFile='input-data/input-day5-intcode-program.txt',
                  env='gojira-prod', verbose=False):
        initLogging(debug=verbose)
        computer = IntcodeComputer(programFile=programFile)
        result = computer.runTestProgram(system_id=system_id)
        return result

    # --------------------------------------------- tests only
    def test(self,
             env='gojira-prod', verbose=False):
        initLogging(debug=verbose)


###############################################################################
if __name__ == '__main__':
    fire.Fire(Puzzles)
