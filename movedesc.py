def get_move_description(board, start_r, start_c, end_r, end_c):
        piece = board[start_r][start_c]
        
        direction = "Move"
        
        if piece[1] == "P":
            if end_r < start_r:
                if piece[0] == "w":
                    direction = "F"
                else:
                    direction = "B"
            elif end_r > start_r:
                if piece[0] == "w":
                    direction = "B" 
                else:
                    direction = "F"
            elif end_c > start_c:
                if piece[0] == "w":
                    direction = "R"
                else:
                    direction = "L"
            elif end_c < start_c:
                if piece[0] == "w":
                    direction = "L"
                else:
                    direction = "R"
        

        elif piece[2] == "1": 
            if end_r - start_r == 2 or start_r - end_r == 2:
                if piece[0] == "w":
                    direction = "F" if end_r < start_r else "B"
                else:
                    direction = "B" if end_r < start_r else "F"
            elif end_c - start_c == 2 or start_c - end_c == 2:
                if piece[1] == "b":
                    direction = "R" if end_c > start_c else "L"
                else:
                    direction = "L" if end_c > start_c else "R"

        elif piece[2] == "2": 
                    if end_r < start_r:
                        if end_c > start_c:
                            if piece[0] == "w":
                                direction = "FR"
                            else:
                                direction = "BL"
                        else:
                            if piece[0] == "w":
                                direction = "FL"
                            else:
                                direction = "BR"
                    else:
                        if end_c > start_c:
                            if piece[0] == "w":
                                direction = "BR"
                            else:
                                direction = "FL"
                        else:
                            if piece[0] == "w":
                                direction = "BL"
                            else:
                                direction = "FR"
            
        return direction