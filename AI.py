import random
import copy

BLACK = -1
WHITE = 1
COLOR_NONE = 0
CURRENT_STEP = 0

ALPHA_INIVAL = float('-Inf')
BETA_INIVAL = float('Inf')
random.seed(0)
INI_DEPTH = 4
BRUTE_FORCE_INIT_DEPTH = 10

# 这是最初的估值矩阵
INI_EVALUATION_MATRIX = [
    [500, -250, 30, 30, 30, 30, -250, 500],
    [-250, -500, 20, 0, 0, 20, -500, -250],
    [30, 20, 30, 5, 5, 30, 20, 30],
    [30, 2, 5, 2, 2, 5, 2, 30],
    [30, 2, 5, 2, 2, 5, 2, 30],
    [30, 20, 30, 5, 5, 30, 20, 30],
    [-250, -500, 20, 2, 2, 20, -500, -250],
    [500, -250, 30, 30, 30, 30, -250, 500],
]


class AI(object):
    def __init__(self, chessboard_size, color, time_out):
        self.chessboard_size = chessboard_size
        self.color = color
        self.time_out = time_out
        self.candidate_list = []

    def go(self, chessboard):
        # if self.get_step_number(chessboard) <= 64:
        global CURRENT_STEP
        CURRENT_STEP = self.get_step_number(chessboard)
        global BRUTE_FORCE_INIT_DEPTH
        # 确保这个数字大于10
        BRUTE_FORCE_INIT_DEPTH = 68 - CURRENT_STEP
        self.candidate_list.clear()
        self.candidate_list = self.get_candidate_list(chessboard, self.color)
        self.avoid_bad_list(self.get_bad_list(chessboard))
        self.get_corner()
        if CURRENT_STEP >= 56:
            best_value, best_coordinate = self.brute_force_minimax_search(chessboard, BRUTE_FORCE_INIT_DEPTH,
                                                                          self.color, ALPHA_INIVAL,
                                                                          BETA_INIVAL)
            print(best_value)
        else:
            global INI_DEPTH
            if 45 >= CURRENT_STEP > 16:
                INI_DEPTH = 3
            best_value, best_coordinate = self.alpha_beta_minimax_search(chessboard, INI_DEPTH, self.color,
                                                                         ALPHA_INIVAL,
                                                                         BETA_INIVAL)
            print(best_value)
        self.up_coordinate(best_coordinate)
        self.special_rule(chessboard)

    '''
    搜索结束后，对candidate_list 增加的强行的最高规则
    '''

    def special_rule(self, chessboard):
        # 避免占星位
        self.avoid_X()
        # 尽量占领角周围的三个稳定子
        self.capture_stable_corner(chessboard)

    '''
    占领与角相关的稳定子
    '''

    def capture_stable_corner(self, chessboard):
        if chessboard[0][0] == self.color:
            self.up_coordinate((1, 1))
            self.up_coordinate((0, 1))
            self.up_coordinate((1, 0))
        if chessboard[0][7] == self.color:
            self.up_coordinate((1, 6))
            self.up_coordinate((0, 6))
            self.up_coordinate((1, 7))
        if chessboard[7][0] == self.color:
            self.up_coordinate((6, 1))
            self.up_coordinate((6, 0))
            self.up_coordinate((7, 1))
        if chessboard[7][7] == self.color:
            self.up_coordinate((6, 6))
            self.up_coordinate((6, 7))
            self.up_coordinate((7, 6))

    '''
    这个函数输入一个坐标
        判定candidate_list 中是否含有这个坐标
            若含有，则将其 置于顶层
    '''

    def up_coordinate(self, coordinate):
        if coordinate in self.candidate_list:
            self.candidate_list.remove(coordinate)
            self.candidate_list.append(coordinate)

    '''
    输入棋盘和当前玩家
    返回基于棋盘局面评估的稳定度(stable degree)
    测试用例为:
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0,-1,-1,-1, 0],
    [0, 0, 0, 0,-1, 1,-1, 0],
    [0, 0, 0, 0,-1,-1,-1, 0],
    [1, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 0, 0, 0, 0, 0]
    '''

    def get_stable_degree(self, chessboard, player):

        stable_degree = 0

        # 对这四个方向以及每个方向的相反方向进行寻找
        directions = [[0, 1], [1, 0], [1, 1], [1, -1]]
        for i in range(0, self.chessboard_size):
            for j in range(0, self.chessboard_size):
                if not chessboard[i][j] == player:
                    continue
                # 共四个方向
                for now_direction in directions:

                    new_coordinate1 = [i + now_direction[0], j + now_direction[1]]
                    # 寻找该方向,找到不为player的点坐标为止(包括出界，对手棋子，空棋子)
                    while self.is_valid_point(new_coordinate1):
                        if chessboard[new_coordinate1[0]][new_coordinate1[1]] == player:
                            new_coordinate1[0] += now_direction[0]
                            new_coordinate1[1] += now_direction[1]
                        else:
                            break

                    op_direction = [-now_direction[0], -now_direction[1]]
                    new_coordinate2 = [i + op_direction[0], j + op_direction[1]]
                    # 寻找该方向的反方向,找到不为player的点坐标为止(包括出界，对手棋子，空棋子)
                    while self.is_valid_point(new_coordinate2):
                        if chessboard[new_coordinate2[0]][new_coordinate2[1]] == player:
                            new_coordinate2[0] += op_direction[0]
                            new_coordinate2[1] += op_direction[1]
                        else:
                            break
                    # 若这两个坐标点有至少一个越界，则稳定度加1
                    if (not self.is_valid_point(new_coordinate1)) or (not self.is_valid_point(new_coordinate2)):
                        stable_degree += 1
                    else:
                        # 若这两个坐标点都是对手棋子，则稳定度加1
                        if (chessboard[new_coordinate1[0]][new_coordinate1[1]] == -player) and (
                                chessboard[new_coordinate2[0]][new_coordinate2[1]] == -player):
                            stable_degree += 1

        return stable_degree

    '''
    这个函数输入棋盘和当前玩家
    返回当前局面下该玩家的行动力
    '''

    def get_move(self, chessboard, player):
        # 返回值就是当前玩家candidate_list的长度
        return len(self.get_candidate_list(chessboard, player))

    '''
    这个函数返回当前棋局已经下了多少颗子
    '''

    def get_step_number(self, chessboard):
        nums = 0
        for row in chessboard:
            for coordinate in row:
                if coordinate != 0:
                    nums += 1
        return nums

    '''
    这是评估函数。输入为一个棋盘局面和当前玩家
    返回值为当前局面的评估结果值
    这个函数只对叶子节点使用，即只评估叶子节点的局面好坏
    早期： 稳定子
    中期： 行动力
    '''

    def evaluation_function(self, chessboard):

        player_evaluation_matrix = self.renew_evaluation_matrix(chessboard, self.color)
        op_evaluation_matrix = self.renew_evaluation_matrix(chessboard, -self.color)
        matrix_value = self.cal_value_from_matrix(chessboard, self.color,
                                                  player_evaluation_matrix) - self.cal_value_from_matrix(
            chessboard, -self.color, op_evaluation_matrix)
        stable_degree_value = self.get_stable_degree(chessboard, self.color) - self.get_stable_degree(chessboard,
                                                                                                      -self.color)
        move_degree = self.get_move(chessboard, self.color) - self.get_move(chessboard, -self.color)

        global CURRENT_STEP
        if CURRENT_STEP <= 20:
            value = matrix_value + 20 * stable_degree_value + move_degree
        elif 24 < CURRENT_STEP <= 44:
            value = matrix_value + 20 * stable_degree_value + 40 * move_degree
        else:
            value = matrix_value + 30 * stable_degree_value + move_degree
        return value

    '''
    计算由权值矩阵得出的局面评估值
    简单的计算所有子的权值和
    '''

    def cal_value_from_matrix(self, chessboard, player, evaluation_matrix):
        value = 0
        for i in range(0, self.chessboard_size):
            for j in range(0, self.chessboard_size):
                if chessboard[i][j] == player:
                    value += evaluation_matrix[i][j]
        return value

    '''
    这个函数根据当前的局面以及角稳定子来刷新评估矩阵
    '''

    def renew_evaluation_matrix(self, chessboard, player):
        new_evaluation_matrix = copy.deepcopy(INI_EVALUATION_MATRIX)
        # 若占了角 则角周围三点的权重增加
        if chessboard[0][0] == player:
            new_evaluation_matrix[0][1] = 300
            new_evaluation_matrix[1][0] = 300
            new_evaluation_matrix[1][1] = 100
        if chessboard[0][7] == player:
            new_evaluation_matrix[0][6] = 300
            new_evaluation_matrix[1][7] = 300
            new_evaluation_matrix[1][6] = 100
        if chessboard[7][0] == player:
            new_evaluation_matrix[6][0] = 300
            new_evaluation_matrix[7][1] = 300
            new_evaluation_matrix[6][1] = 100
        if chessboard[7][7] == player:
            new_evaluation_matrix[7][6] = 300
            new_evaluation_matrix[6][7] = 300
            new_evaluation_matrix[6][6] = 100

        return new_evaluation_matrix

    '''
            print(start,end)
    暴力情况的minimax搜索函数
    适用于最后十步
    '''

    def brute_force_minimax_search(self, chessboard, search_depth, player, alpha, beta):
        # 当搜索深度为0时，说明到达最终节点，开始进行局面评估
        # best_coordinate 是要返回的最佳节点
        best_coordinate = []
        if len(self.get_candidate_list(chessboard, player)) == 0 and len(
                self.get_candidate_list(chessboard, -player)) == 0:
            if_win = 0
            for i in range(0, self.chessboard_size):
                for j in range(0, self.chessboard_size):
                    if_win += 1 if chessboard[i][j] == self.color else -1
            return if_win, best_coordinate
        # 当搜索深度未达到0时，开始向下搜索

        # max节点的情况 轮到己方行动
        if player == self.color:
            # 得到己方能行动的所有坐标 为candidate_list
            candidate_list = self.get_candidate_list(chessboard, player)
            # 遍历所有的candidate_list
            for next_coordinate in candidate_list:
                new_chessboard, new_player = self.next_chessboard(chessboard, player, next_coordinate)
                # 寻找这个坐标下的评估返回值
                tmp_val, tmp_coordinate = self.brute_force_minimax_search(new_chessboard, search_depth - 1, new_player,
                                                                          alpha, beta)
                if tmp_val > alpha:
                    alpha = tmp_val
                    if search_depth == BRUTE_FORCE_INIT_DEPTH:
                        best_coordinate = next_coordinate
                if alpha > beta:
                    best_coordinate = next_coordinate
                    return alpha, best_coordinate
            return alpha, best_coordinate
        # min节点的情况 轮到对方行动
        elif player == -self.color:
            # 得到己方能行动的所有坐标 为candidate_list
            candidate_list = self.get_candidate_list(chessboard, player)
            # 遍历所有的candidate_list
            for next_coordinate in candidate_list:
                new_chessboard, new_player = self.next_chessboard(chessboard, player, next_coordinate)
                tmp_val, tmp_coordinate = self.brute_force_minimax_search(new_chessboard, search_depth - 1, new_player,
                                                                          alpha, beta)
                if tmp_val < beta:
                    beta = tmp_val
                if alpha > beta:
                    return beta, []
            return beta, []

    # def brute_force_minimax_search(self, chessboard, search_depth,player):
    #     best_coordinate = []
    #     # 最后一层时返回输赢值 赢了返回1 输了返回-1
    #     # 相当于bruteforce搜索情况下的评估函数
    #     if len(self.get_candidate_list(chessboard, player)) == 0 and len(
    #             self.get_candidate_list(chessboard, -player)) == 0:
    #         if_win = 0
    #         for i in range(0, self.chessboard_size):
    #             for j in range(0, self.chessboard_size):
    #                 if_win += 1 if chessboard[i][j] == self.color else -1
    #         return if_win, best_coordinate
    #
    #     if player == self.color:
    #         max_val = ALPHA_INIVAL
    #         candidate_list = self.get_candidate_list(chessboard,player)
    #         for next_coordinate in candidate_list:
    #             new_chessboard,new_player = self.next_chessboard(chessboard,player,next_coordinate)
    #             tmp_val,tmp_coordinate = self.brute_force_minimax_search(new_chessboard,search_depth - 1,new_player)
    #             if tmp_val > max_val:
    #                 max_val = tmp_val
    #                 if search_depth == BRUTE_FORCE_INIT_DEPTH:
    #                     best_coordinate = next_coordinate
    #     else:
    #         min_val = BETA_INIVAL
    #         candidate_list = self.get_candidate_list(chessboard,player)
    #         for next_coordinate in candidate_list:
    #             new_chessboard,new_player = self.next_chessboard(chessboard,player,next_coordinate)
    #             tmp_val,tmp_coordinate = self.brute_force_minimax_search(new_chessboard,search_depth - 1,new_player)
    #             if tmp_val < min_val:
    #                 min_val = tmp_val
    #                 if search_depth == BRUTE_FORCE_INIT_DEPTH:
    #                     best_coordinate = next_coordinate

    '''
    这是54步以及之前的minimax算法的搜索函数
    (54步之后采用brute force搜索)
    search_depth 参数代表搜索深度
    chessboard 代表一个棋盘，为 8 * 8 的 二维list
    player 是当前行动玩家
    
    返回值分别为 搜索到的最大/最小值 以及找到的最佳节点
    最佳节点只在最高层max搜索被返回(我们只关心这一节点)
    '''

    def alpha_beta_minimax_search(self, chessboard, search_depth, player, alpha, beta):
        # 当搜索深度为0时，说明到达叶子节点，开始进行局面评估
        # best_coordinate 是要返回的最佳节点
        best_coordinate = []
        if search_depth == 0:
            return self.evaluation_function(chessboard), best_coordinate
        # 当搜索深度未达到0时，开始向下搜索

        # max节点的情况 轮到己方行动
        if player == self.color:
            # 得到己方能行动的所有坐标 为candidate_list
            candidate_list = self.get_candidate_list(chessboard, player)
            # 遍历所有的candidate_list
            for next_coordinate in candidate_list:
                new_chessboard, new_player = self.next_chessboard(chessboard, player, next_coordinate)
                # 寻找这个坐标下的评估返回值
                tmp_val, tmp_coordinate = self.alpha_beta_minimax_search(new_chessboard, search_depth - 1, new_player,
                                                                         alpha, beta)
                if tmp_val > alpha:
                    alpha = tmp_val
                    # 这里记录最佳的点位选择,只有在最上层的时候才需要进行点位置选择
                    if search_depth == INI_DEPTH:
                        best_coordinate = next_coordinate
                if alpha > beta:
                    best_coordinate = next_coordinate
                    return alpha, best_coordinate
            return alpha, best_coordinate
        # min节点的情况 轮到对方行动
        elif player == -self.color:
            # 得到己方能行动的所有坐标 为candidate_list
            candidate_list = self.get_candidate_list(chessboard, player)
            # 遍历所有的candidate_list
            for next_coordinate in candidate_list:
                new_chessboard, new_player = self.next_chessboard(chessboard, player, next_coordinate)
                tmp_val, tmp_coordinate = self.alpha_beta_minimax_search(new_chessboard, search_depth - 1, new_player,
                                                                         alpha, beta)
                if tmp_val < beta:
                    beta = tmp_val
                if alpha > beta:
                    return beta, []
            return beta, []

    '''
    该函数
         输入一个棋盘chessboard
         输入此时行动的玩家
         输入此时行动的坐标
         返回行动后的棋盘
         返回下一回合应该行动的玩家

    该函数模拟一次下棋行为，并返回 下棋过后的棋盘局面 和 下棋后应该行动的玩家(考虑无棋可下的情况下,下棋者不会更替)
    '''

    def next_chessboard(self, chessboard, player, next_coordinate):
        # 判断8个方向
        directions = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]
        # 对手的颜色是当前玩家颜色的相反色
        op_color = -player
        # 拷贝一份新的棋盘到new_chessboard变量中
        new_chessboard = copy.deepcopy(chessboard)
        # 使用list储存所有要被翻转的棋子
        change_coordinate_list = [next_coordinate]
        # 遍历 8 个方向 找出所有被反转的坐标
        for now_direction in directions:
            x = next_coordinate[0] + now_direction[0]
            y = next_coordinate[1] + now_direction[1]
            # tmp_change_list 是当前方向上要被翻转的点的坐标
            tmp_change_list = []
            # if_change 变量表示这个方向上临时找到的对手颜色的点是否要被翻转
            if_change = False
            # while 循环用于寻找这个方向上所有的可被翻转的点
            while self.is_valid_point([x, y]):
                # 如果当前的点是对手的颜色，则把该点坐标加入备选list，并且将坐标向当前方向移动
                if chessboard[x][y] == op_color:
                    tmp_change_list.append([x, y])
                    x += now_direction[0]
                    y += now_direction[1]
                elif chessboard[x][y] == player:
                    # 如果当前的点是player的颜色，则退出循环，找到头了
                    # 并且将已经备选的list加入最终的change_list
                    if_change = True
                    break
                # 如果遇到空点，则直接退出循环
                elif chessboard[x][y] == COLOR_NONE:
                    break

            # 只有在遇到当前player点之后，if_change才为true
            if if_change:
                change_coordinate_list.extend(tmp_change_list)

        for coordinate in change_coordinate_list:
            new_chessboard[coordinate[0]][coordinate[1]] = player

        # 判断在新的棋局中，对手是否有子可下
        new_player = player
        if self.get_candidate_list(new_chessboard, op_color):
            new_player = op_color

        # 返回新的棋盘 和 新的玩家
        return new_chessboard, new_player

    '''
    该函数输入一个点坐标(x,y)并判断该坐标是否越过棋盘边界
    '''

    def is_valid_point(self, point):
        return 0 <= point[0] < self.chessboard_size and 0 <= point[1] < self.chessboard_size

    '''
    该函数输入一个棋盘chessboard
         输入当前玩家player
         返回当前玩家在当前棋盘下的可行动列表
    '''

    def get_candidate_list(self, chessboard, player):
        candidate_list = []

        op_player = -player

        directions = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]
        for i in range(0, self.chessboard_size):
            for j in range(0, self.chessboard_size):

                if chessboard[i][j] != player:
                    continue

                for now_direction in directions:
                    x = i + now_direction[0]
                    y = j + now_direction[1]

                    if not self.is_valid_point([x, y]):
                        continue
                    if not chessboard[x][y] == op_player:
                        continue

                    while True:
                        x += now_direction[0]
                        y += now_direction[1]
                        if not self.is_valid_point([x, y]):
                            break
                        if not chessboard[x][y] == op_player:
                            break

                    if not self.is_valid_point([x, y]):
                        continue
                    if chessboard[x][y] == COLOR_NONE and (x, y) not in candidate_list:
                        candidate_list.append((x, y))

        return candidate_list

    '''
    这个函数避免候选列表最后一位是星位
    '''

    def avoid_X(self):
        end = len(self.candidate_list) - 1
        list = [(1, 1), (1, 6), (6, 1), (6, 6)]
        for i in range(0, len(self.candidate_list)):
            if self.candidate_list[end] in list:
                self.candidate_list[end], self.candidate_list[i] = self.candidate_list[i], self.candidate_list[
                    end]
            if self.candidate_list[end] in list:
                continue
            else:
                break

    def avoid_bad_list(self, bad_list):

        end = len(self.candidate_list) - 1
        for i in range(0, len(self.candidate_list)):

            if self.candidate_list[end] in bad_list:
                self.candidate_list[end], self.candidate_list[i] = self.candidate_list[i], self.candidate_list[
                    end]

            if self.candidate_list[end] in bad_list:
                continue
            else:
                break

    def get_corner(self):

        if (0, 0) in self.candidate_list:
            self.candidate_list.remove((0, 0))
            self.candidate_list.append((0, 0))
        if (7, 7) in self.candidate_list:
            self.candidate_list.remove((7, 7))
            self.candidate_list.append((7, 7))
        if (7, 0) in self.candidate_list:
            self.candidate_list.remove((7, 0))
            self.candidate_list.append((7, 0))
        if (0, 7) in self.candidate_list:
            self.candidate_list.remove((0, 7))
            self.candidate_list.append((0, 7))

    def get_bad_list(self, chessboard):

        bad_list = [(0, 1), (1, 0), (1, 1), (0, 6), (1, 7), (1, 6), (6, 0), (6, 1), (7, 1), (6, 6), (7, 6), (6, 7)]
        if chessboard[0][0] == self.color:
            bad_list.remove((1, 1))
            bad_list.remove((0, 1))
            bad_list.remove((1, 0))

        if chessboard[0][7] == self.color:
            bad_list.remove((0, 6))
            bad_list.remove((1, 6))
            bad_list.remove((1, 7))

        if chessboard[7][0] == self.color:
            bad_list.remove((6, 1))
            bad_list.remove((6, 0))
            bad_list.remove((7, 1))

        if chessboard[7][7] == self.color:
            bad_list.remove((6, 6))
            bad_list.remove((7, 6))
            bad_list.remove((6, 7))

        return bad_list
