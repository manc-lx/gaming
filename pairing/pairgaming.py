import time

class Pairing:
    def __init__(self, cardCount, graphCntPerCard):
        self.cardCount = cardCount
        self.graphCntPerCard = graphCntPerCard
        self.isEvenNumber = graphCntPerCard % 2 == 0 # vs odd numbers
        # max cardCount: (n-1)^2+n
        self.maxCardCnt = (graphCntPerCard-1) * (graphCntPerCard-1)+graphCntPerCard
        self.totalGraphCnt = 0
        self.allCardGraphs = []
        self.graphIdxToCardIdices = {}
        self.maxGraphIdx = -1
        self.tempCardCache = []  # backtracking method cache
        self.allCardGraphSet = []

    def addToCards(self,card):
        card.sort()
        self.allCardGraphs.append(card)
        self.allCardGraphSet.append(set(card))
        if self.maxGraphIdx < card[-1]:
            self.maxGraphIdx = card[-1]
        for x in card: self.addToGraphIdxToCardIdices(x,len(self.allCardGraphs)-1)

    def addToGraphIdxToCardIdices(self,graphIdx, cardIdx):
        cardIndices = self.graphIdxToCardIdices.get(graphIdx)
        if cardIndices:
            cardIndices.append(cardIdx)
        else:
            self.graphIdxToCardIdices[graphIdx] = [cardIdx]

    def solve(self):
        self.testaddcnt = 0
        self.validatecnt = 0
        if self.graphCntPerCard <=2:
            print("graphCntPerCard must be >2.")
            return 0, []
        if self.cardCount < 2:
            print("cardCount must be >=2.")
            return 0, []
        # if self.isEvenNumber:
        #     print("not implemented for even numbers yet.")
        #     return 0, []

        # self.__solveBackTracking()
        # self.__solveFaster()
        self.__solveArray()

        # validate all cards
        for cardIdx in range(len(self.allCardGraphs)):
            for secondCardIdx in range(cardIdx+1,len(self.allCardGraphs)):
                duplication = self.allCardGraphSet[cardIdx] & self.allCardGraphSet[secondCardIdx]
                if len(duplication) != 1:
                    print("validate all cards failed at {} and {}.".format(cardIdx,secondCardIdx))
                    print(self.allCardGraphs[cardIdx])
                    print(self.allCardGraphs[secondCardIdx])
                    print("failed ceritea: {}".format(list(duplication)))
                    return 0, []

        self.dumpCards()

    def dumpCards(self):
        # sort by the last item in card
        self.allCardGraphsSorted=sorted(self.allCardGraphs,key=lambda card:card[-1])

        if self.cardCount > len(self.allCardGraphs):
            if self.cardCount <= self.maxCardCnt:
                print("something went wrong, not able to generate {} cards. "\
                    "need to examine the implementation".format(self.cardCount))
            else:
                print("request card count {} exceed max allowed card count {}. will generate {} "\
                    "cards instead.".format(self.cardCount,self.maxCardCnt,len(self.allCardGraphs)))
            self.cardCount = len(self.allCardGraphs)
        if self.cardCount > 0:
            self.totalGraphCnt = self.allCardGraphsSorted[self.cardCount-1][-1]
        print("Total graph count needed is {} for {} cards.".format(self.totalGraphCnt, self.cardCount))
        print("The cards are:")
        for x in range(self.cardCount):
            print(self.allCardGraphsSorted[x])
        print("All cards for debug purpose:")
        for x in self.allCardGraphs: print(x)  # for debug

    def addFast(self,x,y):
        '''
        idea:
        * find lists with x or y from all,
        * collect elements from the found lists,
        * exclude the collected elements from range(1,maxGraphIndex),
        * choose items from the excluded list.
        '''
        card = [x,y]
        excludes = set()
        XcardIndices = self.graphIdxToCardIdices.get(x)
        if XcardIndices:
            for i in XcardIndices:
                excludes |= self.allCardGraphSet[i]
        YcardIndices = self.graphIdxToCardIdices.get(y)
        if YcardIndices:
            for i in YcardIndices:
                excludes |= self.allCardGraphSet[i]
        graphsNoXY = set() #set(range(1,self.maxGraphIdx+1))
        cardIndicesXOrY = set(XcardIndices) | set(YcardIndices)
        cardIndicesNoXY = set(range(len(self.allCardGraphs))) - cardIndicesXOrY
        for i in cardIndicesNoXY:
            graphsNoXY |= self.allCardGraphSet[i]
        candidates = graphsNoXY - excludes
        cardIndicesNoXY = list(cardIndicesNoXY)
        cardIndicesNoXY.sort()

        success = False
        if len(candidates) == 0 and len(card) < self.graphCntPerCard:
            card.extend(range(self.maxGraphIdx+1,self.maxGraphIdx+1+self.graphCntPerCard-len(card)))
            success = True
        else:
            success, card = self.testAdd(card, candidates, cardIndicesNoXY)

        if success and len(card) == self.graphCntPerCard:
            self.addToCards(card)
            return True
        else:
            #print("something went wrong with {} entry".format(card))
            return False

    def testAdd(self,card,candidateGraphs,testingCardIndices):
        '''
        递归
        card:list，当前卡牌图案
        candidateGraphs:set，所有可选图案
        testingCardIndices:list，所有剩余卡牌索引
        '''
        # self.testaddcnt += 1
        # if self.testaddcnt % 10000 == 0: print("test add count {}".format(self.testaddcnt))
        if (len(testingCardIndices) == 0 or len(candidateGraphs) == 0) and \
            len(card) < self.graphCntPerCard:
            return False, card
        firstTestingCardGraphs = self.allCardGraphSet[testingCardIndices[0]]
        tempCandidates = list(firstTestingCardGraphs & candidateGraphs)
        tempCandidates.sort()
        for graph in tempCandidates:
            newCard = card.copy()
            newCard.append(graph)
            valid,xcardIdx = self.validate(newCard, testingCardIndices[1:])
            if valid:
                if len(newCard) == self.graphCntPerCard:
                    if (len(self.tempCardCache) == 0 or newCard != self.tempCardCache[-1]):
                        return True,newCard
                    else:
                        newCard.pop()
                        continue
                #update candidateGraphs, minus all graphs in cards contain graph
                newCandidateGraphs = candidateGraphs - firstTestingCardGraphs
                cardIndices = self.graphIdxToCardIdices.get(graph)
                for i in cardIndices:
                    newCandidateGraphs -= self.allCardGraphSet[i]
                #update testingCardIndices, minus cards contain graph
                newTestCardIndices = testingCardIndices.copy()
                for c in cardIndices: newTestCardIndices.remove(c)
                success,retCard = self.testAdd(newCard,newCandidateGraphs,newTestCardIndices)
                if success and (len(self.tempCardCache) == 0 or retCard != self.tempCardCache[-1]):
                    return success,retCard
                else:
                    newCard.pop()
            else:
                newCard.pop()

        if len(card) == self.graphCntPerCard and (len(self.tempCardCache) == 0 or card != self.tempCardCache[-1]):
            return True,card
        else:
            return False,card

    def validate(self,card,testingCardIndices):
        cardSet = set(card)
        for i in testingCardIndices:
            # self.validatecnt += 1
            # if self.validatecnt % 10000 == 0: print("validate count {}".format(self.validatecnt))
            if len(cardSet & self.allCardGraphSet[i]) >= 2:
                return False,i
        return True,0

    def __solveBackTracking(self):
        self.firstCardGraph = list(range(1, self.graphCntPerCard+1)) # use 1 based
        self.secondCardGraph = [1]
        self.secondCardGraph.extend(range(self.graphCntPerCard+1,2*self.graphCntPerCard))
        self.addToCards(self.firstCardGraph)
        self.addToCards(self.secondCardGraph)

        # 回溯法，定义临时缓存，超级慢
        xIdx = 1
        yIdx = 1
        # go begin with the 2nd items from the first two lists
        while xIdx >= 1 and yIdx >= 1:
            success = self.addFast(self.firstCardGraph[xIdx],self.secondCardGraph[yIdx])
            if success:
                if yIdx < len(self.secondCardGraph) - 1:
                    yIdx += 1
                else:
                    yIdx = 1
                    xIdx += 1
                    if xIdx >= len(self.firstCardGraph):
                        break
            else:
                # move last card x,y-1 from all to a temp cache
                tempCardIdx = len(self.allCardGraphs) - 1
                lastCard = self.allCardGraphs.pop()
                self.allCardGraphSet.pop()
                # remove temp cache that > lastCard
                for i in range(len(self.tempCardCache)-1,-1,-1): # backorder
                    t = self.tempCardCache[i]
                    if t > lastCard:
                        self.tempCardCache.remove(t)
                if not self.tempCardCache.count(lastCard):
                    self.tempCardCache.append(lastCard)
                # update self.graphIdxToCardIdices
                for g in lastCard:
                    if self.graphIdxToCardIdices[g].count(tempCardIdx):
                        self.graphIdxToCardIdices[g].remove(tempCardIdx)
                #re-test add last card, in the next while iteration
                yIdx -= 1
                if yIdx == 0:
                    yIdx = self.graphCntPerCard-1
                    xIdx -= 1
                    if xIdx < 1:
                        print("Not able to generate full cards.")
                        return 0,[]

        # additional card-graph starts-with 1
        # TBD: replace with backtracking method?
        self.tempCardCache = []
        for k in range(2*self.graphCntPerCard,3*self.graphCntPerCard-2):
            self.addFast(1,k)

    def __solveArray(self):
        """
            from https://www.zhihu.com/question/403423086
            n: graph count per card
            m: card count
            不符合需求，假如m < 8n-7，需要的总图案数不是最优解
            1,2,   3,...,   n
            1,n+1, n+2,..., 2n-1
            1,2n,  2n+1,...,3n-2
            1,3n-1,3n-2,...,4n-3
            1,4n-2,4n-1,...,5n-4
            1,5n-3,5n-2,...,6n-5
            1,6n-4,6n-3,...,7n-6
            1,7n-5,7n-4,...,8n-7
        """
        # verify them...
        cards = []
        cardStr = """
            1  2  3  4  5  6  7  8
            1  9 10 11 12 13 14 15
            1 16 17 18 19 20 21 22
            1 23 24 25 26 27 28 29
            1 30 31 32 33 34 35 36
            1 37 38 39 40 41 42 43
            1 44 45 46 47 48 49 50
            1 51 52 53 54 55 56 57
            2  9 16 23 30 37 44 51
            2 10 17 24 31 38 45 52
            2 11 18 25 32 39 46 53
            2 12 19 26 33 40 47 54
            2 13 20 27 34 41 48 55
            2 14 21 28 35 42 49 56
            2 15 22 29 36 43 50 57
            3  9 17 25 33 41 49 57
            3 10 18 26 34 42 50 51
            3 11 19 27 35 43 44 52
            3 12 20 28 36 37 45 53
            3 13 21 29 30 38 46 54
            3 14 22 23 31 39 47 55
            3 15 16 24 32 40 48 56
            4  9 18 27 36 38 47 56
            4 10 19 28 30 39 48 57
            4 11 20 29 31 40 49 51
            4 12 21 23 32 41 50 52
            4 13 22 24 33 42 44 53
            4 14 16 25 34 43 45 54
            4 15 17 26 35 37 46 55
            5  9 19 29 32 42 45 55
            5 10 20 23 33 43 46 56
            5 11 21 24 34 37 47 57
            5 12 22 25 35 38 48 51
            5 13 16 26 36 39 49 52
            5 14 17 27 30 40 50 53
            5 15 18 28 31 41 44 54
            6  9 20 24 35 39 50 54
            6 10 21 25 36 40 44 55
            6 11 22 26 30 41 45 56
            6 12 16 27 31 42 46 57
            6 13 17 28 32 43 47 51
            6 14 18 29 33 37 48 52
            6 15 19 23 34 38 49 53
            7  9 21 26 31 43 48 53
            7 10 22 27 32 37 49 54
            7 11 16 28 33 38 50 55
            7 12 17 29 34 39 44 56
            7 13 18 23 35 40 45 57
            7 14 19 24 36 41 46 51
            7 15 20 25 30 42 47 52
            8  9 22 28 34 40 46 52
            8 10 16 29 35 41 47 53
            8 11 17 23 36 42 48 54
            8 12 18 24 30 43 49 55
            8 13 19 25 31 37 50 56
            8 14 20 26 32 38 44 57
            8 15 21 27 33 39 45 51
        """
        ret = cardStr.split()
        for i in range(0,57):
            cards.append(ret[8*i:8*i+8])
        # validate all cards
        i = 1
        for cardIdx in range(len(cards)):
            for secondCardIdx in range(cardIdx+1,len(cards)):
                duplication = set(cards[cardIdx]) & set(cards[secondCardIdx])
                if len(duplication) != 1:
                    print("validate all cards failed at {} and {}.".format(cardIdx,secondCardIdx))
                    print(cards[cardIdx])
                    print(cards[secondCardIdx])
                    print("failed ceritea: {}".format(list(duplication)))
                # else:
                #     print(i)
                #     i+=1

    def __solveXXX(self):
        '''
        ideas?
        '''
        pass

if __name__ == "__main__":
    p=Pairing(43,7)
    p.solve()
