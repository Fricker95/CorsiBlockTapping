#! /bin/python3.7
# Nicolas Fricker

import psychopy
from psychopy import visual, core, event, gui, data, logging, colors
from psychopy.hardware import keyboard

import numpy as np
import csv
import time
import sys
import os

class CorsiBlockTappingTest():
	"""Corsi block-tapping test class"""

	LIVES = 2
	WINDIM = 1024
	INSTRUCTIONS = f"A sequence of blocks will be shown in a specific order. On \"GO\" recreate the sequence respecting the order. If you get the boxes or the sequence wrong, you lose a life, you get one opportunity to complete the level (2 lives). Finally, the score (number of correct trials) will be displayed at the end.\nPress Left click on the Mouse to START."

	def __init__(self):
		self.expInfo = dict()
		self.setup()

		self.win = visual.Window([self.WINDIM, self.WINDIM], fullscr = False, pos = (0., 0.))
		self.mouse = event.Mouse(win = self.win)

		self.numLives = self.LIVES

		self.showInstructions()
		self.initializeGrid()

	def __version__(self):
		return psychopy.__version__

	def __name__(self):
		return 'Corsi block-tapping test'

	def setup(self):
		self.getParticipant()

		self.filename = os.path.dirname(os.path.abspath(__file__)) + os.sep + u"expData/%s_%s" % (self.__name__(), self.expInfo["timestamp"])

		self.thisExp = data.ExperimentHandler(
			name = self.__name__(), 
			version = "", 
			extraInfo = None, 
			runtimeInfo = None, 
			savePickle = True, 
			saveWideText = True, 
			dataFileName = self.filename
		)

		self.thisExp.addData("age", self.expInfo["age"])
		self.thisExp.addData("dyslexic", self.expInfo["dyslexic"]) 

		logFile = logging.LogFile(self.filename + ".log", level = logging.EXP)
		logging.console.setLevel(logging.WARNING)

	def getParticipant(self):
		self.expInfo = {
			"age": 0,
			"dyslexic": False
		}
		dlg = gui.DlgFromDict(
			dictionary = self.expInfo,
			sortKeys = False,
			title = self.__name__()
		)
		if dlg.OK == False: core.quit()
		
		self.expInfo["timestamp"] = data.getDateStr()
		self.expInfo["expName"] = self.__name__()
		self.expInfo["psychopyVersion"] = self.__version__()

	def showInstructions(self):
		instructions = visual.TextStim(
			self.win, 
			text = self.INSTRUCTIONS,
			color = "black"
		)
		instructions.size = 2
		instructions.draw(self.win)
		self.win.flip()
		while True:
			if self.mouse.getPressed()[0]: break

	def initializeGrid(self):
		# tmp = [1., 0., -1.]
		tmp = [1., 0.5, 0., -0.5, -1.]

		self.matrixSize = len(tmp)**2

		shape = np.array([0.5, 0.5])

		positions = [shape * modifier for modifier in np.array([[i, j] for i in tmp for j in tmp[::-1]])]

		self.grid = [
			visual.rect.Rect(self.win, 
				size = shape * 0.49, 
				pos = pos
			) for pos in positions
		]
		self.seqNum = [
			visual.TextStim(self.win, 
				text = "",
				pos = pos
			) for pos in positions
		]

		for shape in self.grid:
			shape.fillColor = "black"
			shape.borderColor = "blue"
			shape.autoDraw = True

		for shapeNum in self.seqNum:
			shapeNum.autoDraw = True

		self.title = visual.TextStim(self.win, 
			text = f"Starting...",
			pos = (0, 0.8),
			color = "black"
		)
		self.title.autoDraw = True

		self.lives = visual.TextStim(self.win, 
			text = f"Lives: {self.numLives}",
			pos = (0.8, 0.8),
			color = "black"
		)
		self.lives.size = 0.1
		self.lives.autoDraw = True
		
		self.win.flip()

		time.sleep(2.0)


	def simulate(self, n = 0):
		self.title.text = f"Memorize (level = {n})"
		self.title.draw(self.win)
		self.win.flip()

		self.randseq = []
		while len(self.randseq) < n:
			r = np.random.randint(0, self.matrixSize)
			if r not in self.randseq: self.randseq.append(r)

		for index in self.randseq:
			print(index)
			self.grid[index].fillColor = "white"
			self.win.flip()
			time.sleep(1.0)


	def getResult(self, n = 0):
		self.title.text = f"Go (level = {n})"
		self.title.draw(self.win)
		self.win.flip()

		self.selected = []
		while len(self.selected) < n:
			for i, shape in enumerate(self.grid):
				if self.mouse.getPressed()[0] & shape.contains(self.mouse.getPos() + 1):
					if shape.__dict__["_fillColor"] == colors.Color("black"):
						shape.fillColor = "white"
						self.selected.append(i)
					else:
						shape.fillColor = "black"
						self.selected.remove(i)
					print(i)
					self.win.flip()
					time.sleep(0.2)
					break

	def showAnswer(self):
		isCorrect = self.randseq == self.selected

		incorrectOrder = set(self.randseq).issubset(set(self.selected))
		
		if isCorrect:
			print("Correct")
			self.num += 1
			self.numLives = self.LIVES
		else:
			print("Incorrect")
			self.numLives -= 1
			if incorrectOrder:
				print("Incorrect Order")


		self.title.text = ["Correct" if isCorrect else "Incorrect" if not incorrectOrder else "Incorrect Order"][0]
		self.title.draw(self.win)

		self.lives.text = f"Lives: {self.numLives}"
		self.lives.draw(self.win)

		for i, shape in enumerate(self.grid):
			if i in self.randseq and i in self.selected and (self.selected.index(i) == self.randseq.index(i)):
				shape.fillColor = "green"
			elif i in self.randseq and i in self.selected and self.selected.index(i) != self.randseq.index(i):
				shape.fillColor = "orange"
			elif i not in self.randseq and i in self.selected:
				shape.fillColor = "red"
			else:
				shape.fillColor = "black"

		for i, r in enumerate(self.randseq):
			self.seqNum[r].text = f"{i + 1}"

		self.win.flip()
		time.sleep(2.0)

	def reset(self):
		for num in self.seqNum:
			num.text = ""
		for shape in self.grid:
			shape.fillColor = "black"
		self.win.flip()

	def run(self):
		self.num = 2
		while self.num <= self.matrixSize and self.numLives:
			self.win.flip()
			self.reset()
			self.simulate(self.num)
			self.reset()
			self.getResult(self.num)
			self.showAnswer()
			self.reset()

		score = self.num - 1

		self.thisExp.addData("score", score)

		self.title.text = f"Out of Lives! GoodBye...\nScore = {score}"
		self.title.draw(self.win)
		self.win.flip()
		core.wait(5.0)

def main():
	test = CorsiBlockTappingTest()
	test.run()

	core.quit()

if __name__ == '__main__':
	main()
