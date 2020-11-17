#!/bin/python
# -*- coding: utf-8 -*-

import json
import fire
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

    # --------------------------------------------- day 2
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

    # --------------------------------------------- tests only
    def test(self,
             env='gojira-prod', verbose=False):
        initLogging(debug=verbose)


###############################################################################
if __name__ == '__main__':
    fire.Fire(Puzzles)
