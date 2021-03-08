import re
import testLibrary


def get_chessboard_list(address):
    with open(address, "r") as r:
        tmp_list = []
        for line in r:
            string = line
            # print(string)
            tmp_list = re.findall(r'-?\d', string)

        count = 0
        ans_list = []
        for i in range(0, 60):
            ans_list.append([])
            for j in range(0, 8):
                ans_list[i].append([])
                for k in range(0, 8):
                    ans_list[i][j].append(int(tmp_list[count]))
                    count += 1
                    if count == len(tmp_list):
                        return ans_list


# chessboard_list = get_chessboard_list()
# count = 0
# for chessboard in chessboard_list:
#     print(count)
#     count+=1
#     testLibrary.print_chessboard(chessboard)
