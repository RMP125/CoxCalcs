import matplotlib
import math
import random

piety = True
attLev = 120.
strLev = 120.

tekton = {
    "def": 205,
    "hp": 300,
    "mage": 205,
    "bonuses": [155, 165, 105, 0, 0]
}
vasa = {
    "def": 175,
    "hp": 300,
    "mage": 230,
    "bonuses": [170, 190, 50, 400, 60]
}
lefthand = {
    "def": 175,
    "hp": 600,
    "mage": 175,
    "bonuses": [50, 50, 50, 50, 50]
}
head = {
    "def": 150,
    "hp": 800,
    "mage": 200,
    "bonuses": [200, 200, 200, 400, 50]
}
npcs = {"tekton": tekton,
        "vasa": vasa,
        "lefthand": lefthand,
        "head": head
        }

attStyleDict = {
    "Stab": 0,
    "Slash": 1,
    "Crush": 2,
    "Mage": 3,
    "Range": 4
}


class NPC(object):
    npc_type = object

    def __init__(self, npc_type):
        self.defLev = npcs[npc_type]["def"]
        self.hp = npcs[npc_type]["hp"]
        self.mage = npcs[npc_type]["mage"]
        self.statBlock = npcs[npc_type]["bonuses"]
        self.type = npc_type

    def changeDef(self, reduction):
        self.defLev -= reduction

    def loseHP(self, reduction):
        self.hp -= reduction


def getDefRoll(effDef, defBonus):
    return (effDef+9) * (defBonus + 64)


def getAttRoll(attBonus, pieT, bonuspct, attStyleBonus):
    attWPray = attLev
    if pieT:
        attWPray *= 1.2
    attWPray = math.floor(attWPray)
    effAtt = math.floor(attWPray + attStyleBonus + 8)
    attRoll = effAtt * (attBonus + 64)
    return math.floor(attRoll * bonuspct)


def getScyHitStats(monster, isInq):
    maxHit = [48, 24, 12]
    attBonus = 147
    if isInq:
        maxHit = [46, 23, 11]
        attBonus = 139
    attStyle = ["Slash", 0]
    return getHit(False, False, isInq, maxHit, attStyle, False, attBonus, monster)


def getHammerHitStats(monster, isInq):
    maxHit = [76]
    attBonus = 160
    if isInq:
        maxHit = [75]
        attBonus = 192
    attStyle = ["Crush", 3]
    return getHit(False, True, isInq, maxHit, attStyle, False, attBonus, monster)


def getBGSHitStats(monster, isInq):
    maxHit = [74]
    attBonus = 169
    if isInq:
        maxHit = [72]
        attBonus = 161
    attStyle = ["Slash", 0]
    return getHit(True, False, isInq, maxHit, attStyle, True, attBonus, monster)


# def getFangHitStats(monster, isInq):
#     maxHit = [48, 24, 12]
#     attBonus = 147
#     if isInq:
#         maxHit = [46, 23, 11]
#         attBonus = 155
#     attStyle = ["Stab", 0]
#     doubleRoll = True,
#     return getHit(False, False, isInq, maxHit, attStyle, doubleRoll, attBonus, monster)


def getMaceHitStats(monster, isInq):
    maxHit = [53]
    attBonus = 160
    if isInq:
        maxHit = [52]
        attBonus = 192
    attStyle = ["Crush", 0]
    doubleRoll = False,
    return getHit(False, False, isInq, maxHit, attStyle, doubleRoll, attBonus, monster)


def hitChance(attRoll, defRoll):
    if attRoll > defRoll:
        return 1 - ((defRoll + 2) / (2 * (attRoll + 1)))
    return attRoll / (2 * (defRoll + 1))


def isHit(attRoll, defRoll):
    hitTemp = hitChance(attRoll, defRoll)
    return random.random() < hitTemp


def getHit(bgsDrain, hammerDrain, isInq, maxHit, attStyle, doubleRoll, attBonus, npc):
    bonus = 1
    hit = 0
    if isInq and attStyle[0] == "Crush":
        bonus = 1.025
    attRoll = getAttRoll(attBonus, True, bonus, attStyle[1])
    attStyleLoc = attStyleDict[attStyle[0]]
    defRoll = getDefRoll(npc.statBlock[attStyleLoc], npc.defLev)
    for k in maxHit:
        isAHit = isHit(attRoll, defRoll)
        if doubleRoll and not isAHit:
            isAHit = isHit(attRoll, defRoll)
        if isAHit:
            hit += random.randint(0, k)
        if bgsDrain:
            npc.changeDef(hit)
        elif hammerDrain and hit > 0:
            npc.changeDef(math.floor(npc.defLev * .3))
    npc.loseHP(hit)
    if npc.hp <= 0:
        return [npc, 1]
    elif npc.type == "tekton":
        if bgsDrain:
            npc.changeDef(10)
        elif hammerDrain and hit > 0:
            npc.changeDef(math.floor(npc.defLev * .05))
    return [npc, 0]


def hitBoss(specWep, numSpecs, isInq, npc):
    ttk = 0
    dead = 0
    for j in range(numSpecs):
        ttk += 3.6
        if specWep == "BGS":
            [npc, dead] = getBGSHitStats(npc, isInq)
        elif specWep == "DWH":
            [npc, dead] = getHammerHitStats(npc, isInq)
    while dead == 0:
        [npc, dead] = getScyHitStats(npc, False)
        ttk += 3.0
    ttk -= 2.4
    return ttk


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    bgsAVGTime = 0
    hammerAVGTime = 0
    hammerTorvaAVGTime = 0
    sampleSize = 100000
    # specs = 2
    for specs in (1, 2):
        for i in range(sampleSize):
            bgsAVGTime += hitBoss("BGS", specs, False, NPC("lefthand"))
            hammerAVGTime += hitBoss("DWH", specs, True, NPC("lefthand"))
            hammerTorvaAVGTime += hitBoss("DWH", specs, False, NPC("lefthand"))

        bgsAVGTime /= sampleSize
        hammerAVGTime /= sampleSize
        hammerTorvaAVGTime /= sampleSize
        print("For a sample size of ", sampleSize, ", with ", specs, " Specs \n" +
              "per phase, as well as always scything in Torva afterwards... \n" +
              "BGS had an average kill time of: ", round(bgsAVGTime, 4), ", \n" +
              "Inq hammer had an average kill time of: ", round(hammerAVGTime, 4), ", and\n" +
              "Torva hammer had an average kill time of: ", round(hammerTorvaAVGTime, 4), ". ")
