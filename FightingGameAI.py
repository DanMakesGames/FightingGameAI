import numpy as np
import random

attacks = 4
actions = 7
positions = 5
statesPerPos = (attacks * 2) + 1
S = statesPerPos * positions

headbuttRange = 1
punchRange = 2
kickRange = 3
grabRange = 1

headbuttIndex = 0
punchIndex = 1
kickIndex = 2
grabIndex = 3

# enemy response behavior for attacks 0: block, 1: counter, 2:hit
enemyResHB = [0.0,0.0,0.0]
enemyResHB[0] = 0.3
enemyResHB[1] = 0.4
enemyResHB[2] = 1 - (enemyResHB[0] + enemyResHB[1])

enemyResP = [0.0,0.0,0.0]
enemyResP[0] = 0.3
enemyResP[1] = 0.1
enemyResP[2] = 1 - (enemyResP[0] + enemyResP[1])

enemyResK = [0.0,0.0,0.0]
enemyResK[0] = 0.4
enemyResK[1] = 0.3
enemyResK[2] = 1 - (enemyResK[0] + enemyResK[1])

enemyResG = [0.0,0.0,0.0]
enemyResG[0] = 0.0
enemyResG[1] = 0.4
enemyResG[2] = 1 - (enemyResG[0] + enemyResG[1])

#based on range
enemyCounterWF = [0.9,0.5,0.3]
enemyCounterWB = [0.4,0.2,0.1]

enemyGrabProb = 0.3
# create transition matrices based on attack ranges, attack damage, and enemy patterns

# action 0, headbutt. R = from, C = to
def CreateTransMatrixAttack(enemyResponse, attackRange, attackIndex):
	
	transMat = np.zeros((S,S))
	
	for p in range(0,positions):
		if (p+1) <= attackRange:
			# chance to hit
			transMat[p * statesPerPos][(p * statesPerPos) + 1 + attackIndex] = enemyResponse[2]
			
			# chance to take damage from being countered by the enemy
			transMat[p * statesPerPos][(p * statesPerPos) + attacks + 1 + punchIndex] = enemyResponse[1]
			
			# chance to be blocked
			transMat[p * statesPerPos][p * statesPerPos] = enemyResponse[0]
			print("dingo" + str(p))
                # if we are out of range for this attack but still within kick range
		elif p < kickRange:
                        # chance to take damage from being countered by the enemy
			transMat[p * statesPerPos][(p * statesPerPos) + attacks + 1 + punchIndex] = enemyResponse[1]
			# chance to be blocked
			transMat[p * statesPerPos][p * statesPerPos] = enemyResponse[0] + enemyResponse[2]
		# we are out of range to hit, and ouf of range to be countered, then nothing happens
		else:
				transMat[p * statesPerPos][p * statesPerPos] = 1
				
		
	return transMat

transHeadbutt = CreateTransMatrixAttack(enemyResHB, headbuttRange, headbuttIndex)
print(transHeadbutt)
transPunch = CreateTransMatrixAttack(enemyResP, punchRange, punchIndex)
transKick = CreateTransMatrixAttack(enemyResK, kickRange, kickIndex)
transGrab = CreateTransMatrixAttack(enemyResG, grabRange, grabIndex)

transWalkF = np.zeros((S,S))

for p in range(0,positions):
	#player already adjacent to enemy. Walking forward does nothing
	if p == 0:
		#does nothing
		transWalkF[p * statesPerPos][p * statesPerPos] = 1 - enemyCounterWF[p]
		#still can get countered
		transWalkF[p * statesPerPos][(p * statesPerPos) + attacks + 1 + punchIndex] = enemyCounterWF[p]
	# player in range of enemy
	elif p < (kickRange):
		# successful walk
		transWalkF[p * statesPerPos][(p-1) * statesPerPos] = 1 - enemyCounterWF[p]
		# get hit durring
		# TODO, expand to account for different enemy attacks based on range
		transWalkF[p * statesPerPos][(p * statesPerPos) + attacks + 1 + punchIndex] = enemyCounterWF[p]
	# not in range, can walk forward easily
	elif p >= kickRange:
		transWalkF[p * statesPerPos][(p-1) * statesPerPos] = 1

transWalkB = np.zeros((S,S))

for p in range(0,positions):

	# already at max distance, cant walk back any more
	if p == (positions-1):
		if (p+1) <= kickRange:
			#does nothing
			transWalkB[p * statesPerPos][p * statesPerPos] = 1 - enemyCounterWB[p]
			#still can get countered
			transWalkB[p * statesPerPos][(p * statesPerPos) + attacks + 1 + punchIndex] = enemyCounterWB[p]
		else:
			#does nothing
			transWalkB[p * statesPerPos][p * statesPerPos] = 1
			
	# player in range of enemy
	elif p < (kickRange):
		# successful walk
		transWalkB[p * statesPerPos][(p+1) * statesPerPos] = 1 - enemyCounterWB[p]
		# get hit durring
		# TODO, expand to account for different enemy attacks based on range
		transWalkB[p * statesPerPos][(p * statesPerPos) + attacks + 1 + punchIndex] = enemyCounterWB[p]
		
	# not in range, can walk back easily
	elif p >= kickRange:
		# always can walk forward unmolested
		transWalkB[p * statesPerPos][(p+1) * statesPerPos] = 1

# transition matrix for action Blocking
def CreateBlockTransMatrix(inEnemyGrabProb):
        transMat = np.zeros((S,S))
        transMat[0][0 + 1 + grabIndex] = inEnemyGrabProb
        transMat[0][0] = 1 - inEnemyGrabProb
        for p in range(1,positions):
                transMat[p * statesPerPos][p * statesPerPos] = 1
        return transMat
	
transBlock = CreateBlockTransMatrix(enemyGrabProb)

# add in all the processing for the attack and block states
def CreateHitDamageStates(transMat):
	for p in range(0,positions):
	
		# set all attacks to go back
		for a in range(0,attacks):
			# attack hit states always go back to neutral
			transMat[(p*statesPerPos)+1+a][p*statesPerPos] = 1.0
		# set all damage states to go back to neutral
		for d in range(0,attacks):
			transMat[(p*statesPerPos)+1+attacks+d][p*statesPerPos] = 1.0
# test if rows add to 1

CreateHitDamageStates(transHeadbutt)
CreateHitDamageStates(transPunch)
CreateHitDamageStates(transKick)
CreateHitDamageStates(transGrab)
CreateHitDamageStates(transWalkF)
CreateHitDamageStates(transWalkB)
CreateHitDamageStates(transBlock)

def TestTransMat(transMat):
        for r in transMat:
                total = 0
                for i in r:
                        total += i
                if total != 1:
                        print("total: " + str(total))

print("headbutt")
TestTransMat(transHeadbutt)

print("Punch")
TestTransMat(transPunch)

print("kick")
TestTransMat(transKick)

print("grab")
TestTransMat(transGrab)

print("WalkF")
TestTransMat(transWalkF)

print("walkB")
TestTransMat(transWalkB)

print("block")
TestTransMat(transBlock)


