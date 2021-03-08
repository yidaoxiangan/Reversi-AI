'''
这个函数将棋局格式化打印输出到控制台
输入为一个棋局二维list
'''
def print_chessboard(chessboard):
    for row in chessboard:
        for node in row:
            if node == -1:
                print('%3s' % '+', end='')
            elif node == 1:
                print('%3s' % '-', end='')
            elif node == 0:
                print('%3s' % 'O',  end='')
            # print('%3d' % node, end='')
        print()
    print()
