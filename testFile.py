import time
import AI
import testLibrary
import  chessboard_alalysis

BLACK = '+'
WHITE = '-'
chessboard_case = [
    [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 1, 0],
    [0, 0, 1, 1, 0, 1, 1, 0],
    [0, 0, 0, 1, 1, 0, 1, 0],
    [0, 0, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0,-1, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0]
    ],
    [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, -1, -1, -1, 0],
    [0, 0, 0, 0, -1, 1, -1, 0],
    [0, 0, 0, 0, -1, -1, -1, 0],
    [1, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 0, 0, 0, 0, 0]
    ]
]
# chessboard_case2 这个变量储存了从log中读取的60个棋盘
chessboard_case2 = chessboard_alalysis.get_chessboard_list("log.txt")

# testObject = AI.AI(8, AI.BLACK, 5)

now_test = 50
testAI = AI.AI(8, AI.WHITE, 5)
# testObject.go(chessboard_case2[now_test])
testLibrary.print_chessboard(chessboard_case2[now_test])

# for chessboard in chessboard_case2:
#     print(testObject.evaluation_function(chessboard,-1),end=' ')
#     print(testObject.get_stable_degree(chessboard,-1))

# for i in range(0,60):
# time_start = time.time()
testAI.go(chessboard_case2[now_test])
# time_end = time.time()
testLibrary.print_chessboard(chessboard_case2[now_test])
    # print('time is ', time_end - time_start,' s')
print(testAI.candidate_list)

