import time
from collections import deque
import heapq
import itertools

class SokoBot:
    def solveSokobanPuzzle(self, width, height, mapData, itemsData):
        
        directions = {'u': (-1, 0), 'd': (1, 0), 'l': (0, -1), 'r': (0, 1)}
        directionList = list(directions.items())
        INF = 10**8
        
        # CONVERT LAYOUT DATA INTO ROWS OF CHARS
        def getRow(layout): 
            if isinstance(layout, str): 
                return layout.splitlines()
            return [row if isinstance(row, str) else ''.join(row) for row in layout]
        
        mapRows = getRow(mapData)
        itemRows = getRow(itemsData)
        
        rowCount = max(len(mapRows), len(itemRows), int(height))
        colCount = max(
            int(width),
            max((len(row) for row in mapRows), default=0),
            max((len(row) for row in itemRows), default=0)
        )
        
        # MAP PARSING
        walls = set()
        goals = set()
        crates = set()
        players = set()
        floor = set()
         
        # MAP INSTANTIATION
        for layout in (mapRows, itemRows): 
            for r, row in enumerate(layout): 
                usedCol = [c for c, char in enumerate(row[:colCount]) if char != ' ']
                if not usedCol:
                    continue
                
                floor.update((r, c) for c in range(usedCol[0], usedCol[-1] + 1))
                
                for c, char in enumerate(row[:colCount]):
                    pos = (r, c)
                    if char == '#':
                        walls.add(pos) 
                    elif char == '.':
                        goals.add(pos) 
                    elif char == '$':
                        crates.add(pos) 
                    elif char == '@':
                        players.add(pos) 
                    elif char == '*':   # CRATE ON GOAL SYMBOL (stated by map txt file)
                        crates.add(pos) 
                        goals.add(pos) 
                    elif char == '+':   # PLAYER ON GOAL SYMBOL (stated by map txt file)
                        players.add(pos) 
                        goals.add(pos) 
        
        # TILE CLEANUP
        # PLACES GOAL AND CRATES ON A CERTAIN FLOOR
        # GOALS AND CRATES ARE FROZEN IN PREPARATION FOR THE REVERSE PUSH HEURISTIC
        player = next(iter(players))
        goals.difference_update(walls)
        crates.difference_update(walls)
        floor.update(goals)
        floor.update(crates)
        floor.add(player)
        floor.difference_update(walls)
        goals = frozenset(goals)
        crates = frozenset(crates)
         
        # FINDS EVERY UNOCCUPIED FLOOR A BOT CAN TRAVERSE THROUGH BFS
        def floorExploreBFS(playerPos, blockedByCrate): 
            parent = {playerPos: (None, '')}
            queue = deque([playerPos])
            
            while queue: 
                r, c = queue.popleft()
                for move, (dr, dc) in directionList: 
                    nextPos = (r + dr, c + dc)
                    if(nextPos in floor and
                            nextPos not in blockedByCrate and
                            nextPos not in parent): 
                        parent[nextPos] = ((r, c), move)
                        queue.append(nextPos)

            return parent
        
        # GETS WALKING PATH BASED OFF OF ATTAINED POSITIONS
        def getPath(src, dest, parent):
            path = []
            pos = dest
            while pos != src:
                prev, move = parent[pos]
                path.append(move)
                pos = prev
                
            return ''.join(reversed(path))
        
        # COMPUTES DISTANCES BETWEEN CRATE TO GOAL WITH BFS FOR POSITION EXPLORATIONS
        goalList = sorted(goals)
        goalDist = []
        pushRegions = set()
        
        for goal in goalList: 
            dist = {goal: 0}
            queue = deque([goal])
            
            while queue: 
                r, c = queue.popleft()
                for dr, dc in directions.values():
                    prevCrate = (r - dr, c - dc)
                    mustStand = (r - 2 * dr, c - 2 * dc)
                    
                    if(prevCrate in floor and
                            mustStand in floor and
                            prevCrate not in dist):
                        dist[prevCrate] = dist[(r, c)] + 1
                        queue.append(prevCrate)
                        
            goalDist.append(dist)
            pushRegions.update(dist)
            
        # CHECKS 2X2 DEADLOCKS THAT PREVENTS A CRATE FROM REACHING A GOAL
        def hasDeadlock(cratePos):
            for r, c in cratePos:
                for top in (r - 1, r): 
                    for left in (c - 1, c):
                        block = (
                                (top, left), 
                                (top + 1, left), 
                                (top, left + 1), 
                                (top + 1, left + 1)
                            )
                        blocked = all(pos not in floor or pos in cratePos
                            for pos in block
                        )
                        crateNotOnGoal = any(
                            pos in cratePos and pos not in goals
                            for pos in block
                        )
                        if blocked and crateNotOnGoal:
                            return True
                        
            return False
        
        # FINDS SHORTEST REVERSE PUSH DISTANCE FOR MATCHING CRATES TO GOAL
        def heuristic(cratePos): 
            sortedCrates = sorted(
                cratePos, 
                key=lambda crate: sum(crate in dists for dists in goalDist)
            )
            
            costs = {frozenset(): 0}
            
            for crate in sortedCrates:
                nextCosts = {}
                for assignedGoals, cost in costs.items():
                    for goalIndex, dists in enumerate(goalDist):
                        if goalIndex in assignedGoals:
                            continue 
                        
                        dist = dists.get(crate, INF)
                        if dist >= INF:
                            continue
                        
                        nextAssignedGoals = assignedGoals.union((goalIndex,))
                        nextCosts[nextAssignedGoals] = min(nextCosts.get(nextAssignedGoals, INF), cost + dist)
                        
                costs = nextCosts
                if not costs:
                    return INF
                    
            allGoals = frozenset(range(len(goalList)))
            return costs.get(allGoals, INF)
        
        # A* SEARCH SETUP USING CRATE PUSHES AS A COST
        reachable = floorExploreBFS(player, crates)
        startKey = (crates, min(reachable))
        startHeuristic = heuristic(tuple(sorted(crates)))
        
        ctr = itertools.count()
        frontier = [(startHeuristic, startHeuristic, next(ctr), 0, startKey)]
        optimalPush = {startKey: 0}
        playerPos = {startKey: player}
        parents = {startKey: None}
        goalKey = None
        
        # A* SEARCH
        while frontier: 
            f, h, _, pushes, state = heapq.heappop(frontier)
            
            if pushes != optimalPush.get(state):
                continue
            
            cratePos, _ = state
            currPlayer = playerPos[state]
            
            if cratePos == goals: 
                goalKey = state
                break
            
            reachable = floorExploreBFS(currPlayer, cratePos)
            
            # EVALUATES THE MOST OPTIMAL PUSH
            for crateR, crateC in cratePos: 
                for move, (dr, dc) in directionList: 
                    standPos = (crateR - dr, crateC - dc)
                    nextCrate = (crateR + dr, crateC + dc)
                    
                    if standPos not in reachable: 
                        continue
                    if nextCrate not in floor or nextCrate in cratePos:
                        continue
                    if nextCrate not in goals and nextCrate not in pushRegions:
                        continue
                    
                    updatedCrates = set(cratePos)
                    updatedCrates.remove((crateR, crateC))
                    updatedCrates.add(nextCrate)
                    newCrates = frozenset(updatedCrates)
                    if hasDeadlock(newCrates):
                        continue
                    
                    # UTILIZE PLAYER'S REACHABLE AREAS AS PARTS OF STATE
                    newPlayer = (crateR, crateC)
                    nextReachables = floorExploreBFS(newPlayer, newCrates)
                    nextState = (newCrates, min(nextReachables))
                    newPushes = pushes + 1
                    
                    if newPushes >= optimalPush.get(nextState, INF):
                        continue
                    
                    newHeuristic = heuristic(tuple(sorted(newCrates)))
                    if newHeuristic >= INF:
                        continue
                    
                    # STORES THE WALKS AND PUSHES WHEN APPROACHING AND PUSHING A CRATE
                    pathProgress = getPath(currPlayer, standPos, reachable) + move
                    optimalPush[nextState] = newPushes
                    playerPos[nextState] = newPlayer
                    parents[nextState] = (state, pathProgress)
                    
                    heapq.heappush(
                        frontier,
                        (newPushes + newHeuristic, newHeuristic, next(ctr),
                        newPushes, nextState)
                    )
                
        # RECONSTRUCT THE FINISHING MOVES
        pathSegments = []
        state = goalKey
        while state != startKey:
            prev, segment = parents[state]
            pathSegments.append(segment)
            state = prev
        
        return ''.join(reversed(pathSegments)) 
            
        
        """ def heuristic(playerPos, cratePos):
            total = 0
            for (crateR, crateC) in cratePos:
                nearestGoal = 0
                for (goalR, goalC) in goals:
                    dist = abs(crateR - goalR) + abs(crateC - goalC)
                    if dist < nearestGoal:
                        nearestGoal = dist
                total += nearestGoal

            playerR, playerC = playerPos
            nearestCrate = 0
            for (crateR, crateC) in cratePos:
                dist = abs(playerR - crateR) + abs(playerC - crateC)
                if dist < nearestCrate:
                    nearestCrate = dist
            total += nearestCrate
            return total
    
        # variables
        walls = set()
        goals = set()
        crates = set()
        player = None
        strSolution = ""
        directions = {'u': (-1, 0), 'd': (1, 0), 'l': (0, -1), 'r': (0, 1)}
        best = 0

        # mapData Parsing
        for r, row in enumerate(mapData):
            for c, char in enumerate(row):
                if char == '#':
                    walls.add((r, c))
                    #strSolution += (r, c)
                elif char == '.':
                    goals.add((r, c))
                    #strSolution += (r, c)

        for r, row in enumerate(itemsData):
            for c, char in enumerate(row):
                if char == '$':
                    crates.add((r, c))
                    #strSolution += (r, c)
                elif char == '@':
                    player = (r, c)
                    #strSolution += (r, c)
        playerR, playerC = player #move player position data

        # A* search implementation
        startState = (player, frozenset(crates))
        startTime = time.time()
        frontier = [(heuristic(player, startState[1]), 0, startState, "")]
        explored = set()

        while len(frontier) > 0:

            for i in range(len(frontier)):
                if frontier[i][0] < frontier[best][0]:
                    best = i

            f, g, state, path = frontier.pop(best)
            playerPos, cratePos = state

            if state in explored:
                continue
            explored.add(state)
            if cratePos == goals:
                strSolution = path
                break
            playerR, playerC = playerPos
            for move, (directionsR, directionsC) in directions.items():
                newR, newC = playerR + directionsR, playerC + directionsC
                if (newR, newC) in walls:
                    continue
                if (newR, newC) in cratePos:
                    behindR, behindC = newR + directionsR, newC + directionsC
                    if (behindR, behindC) in walls or (behindR, behindC) in cratePos:
                        continue
                    newCrates = set(cratePos)
                    newCrates.remove((newR, newC))
                    newCrates.add((behindR, behindC))
                    newCrates = frozenset(newCrates)
                else:
                    newCrates = cratePos
                newState = ((newR, newC), newCrates)
                if newState not in explored:
                    newG = g + 1
                    newF = newG + heuristic((newR, newC), newCrates)
                    frontier.append((newF, newG, newState, path + move))

      
      
      

      # Old Solution
        #for i in range(3): #Can change this, just indicates the number of moves
            #for move, (directionsR, directionsC) in directions.items():
                #newR, newC = playerR + directionsR, playerC + directionsC
                #if (newR, newC) not in walls and (newR, newC) not in crates:
                    #strSolution += move #adds move from the direction set to strSolution
                    #playerR, playerC = newR, newC     
                    #break

        return strSolution """