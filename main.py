import easygui
from copy import deepcopy
import pygame
pygame.init()
#Colors
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
blue = (0, 0, 255)
green = (0, 255, 0)
golden_rod = (218, 165, 32)
myfont = pygame.font.SysFont("monospace", 15)
#Constants
display_width = 1200
display_height = 800
display_surface = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption("GO")
clock = pygame.time.Clock()
display_surface.fill(white)
board_width = 9
board_height = 9
game_board = [["" for height in range(board_width)] for width in range(board_height)]
x_first = 50
y_first = 50
square_size = 30
white_captured = 0
black_captured = 0
previous_move = []
turn = 1
mouseX = 0
mouseY = 0
one_move_ago = []
two_move_ago = []
pass_in_row = 0
white_points = 0
black_points = 0
visited = []

def game_start():
    size = easygui.indexbox("Choose the size of the board", choices=("9x9","13x13","19x19"))
    global  board_height, board_width
    if size == 0:
        board_width = 9
        board_height = 9
    elif size == 1:
        board_height = 13
        board_width = 13
    elif size == 2:
        board_height = 19
        board_width = 19
    return board_width, board_height
def reverse_token(token):
    if token == "W":
        return "B"
    elif token == "B":
        return "W"

def next_to_enemy(x_cord, y_cord, token):
    enemies = []
    if (x_cord-1)>=0 and game_board[x_cord -1][y_cord] == reverse_token(token):
        enemies.append((x_cord - 1, y_cord))
    if (x_cord+1)<board_width and game_board[x_cord + 1][y_cord] == reverse_token(token):
        enemies.append((x_cord + 1,y_cord))
    if (y_cord-1)>=0 and game_board[x_cord][y_cord - 1] == reverse_token(token):
        enemies.append((x_cord, y_cord-1))
    if (y_cord+1)<board_height and game_board[x_cord][y_cord + 1] == reverse_token(token):
        enemies.append((x_cord, y_cord+1))
    return enemies

def count_liberty(x_cord, y_cord, previous, prev_count,token):
    previous.add((x_cord,y_cord))
    count = prev_count
    if (x_cord-1)>=0 and (x_cord-1, y_cord) not in previous:
        if game_board[x_cord -1][y_cord] == "":
            count+=1
        elif game_board[x_cord-1][y_cord] == token:
            count +=count_liberty(x_cord-1,y_cord,previous,count,token)[0]
    if (x_cord+1)<board_width and (x_cord+1, y_cord) not in previous:
        if game_board[x_cord +1][y_cord] == "":
            count+=1
        elif game_board[x_cord+1][y_cord] == token:
            count +=count_liberty(x_cord+1,y_cord,previous,count,token)[0]
    if (y_cord-1)>=0 and (x_cord,y_cord-1) not in previous:
        if game_board[x_cord][y_cord - 1] == "":
            count += 1
        elif game_board[x_cord][y_cord-1] == token:
            count += count_liberty(x_cord,y_cord-1,previous,count,token)[0]
    if (y_cord+1)<board_height and (x_cord,y_cord + 1) not in previous:
        if game_board[x_cord][y_cord + 1] == "":
            count += 1
        elif game_board[x_cord][y_cord + 1] == token:
            count += count_liberty(x_cord, y_cord+1 ,previous, count, token)[0]
    return count, previous

def is_atari(x_cord, y_cord, token):
    removed = []
    for element in next_to_enemy(x_cord,y_cord,token):
        liberties, points = count_liberty(element[0],element[1],set(),0,reverse_token(token))
        if liberties == 0:
            for point in points:
                game_board[point[0]][point[1]]=""
                removed.append((point[0], point[1]))
    return removed
    
def place_token (x_cord, y_cord, token):
    left, top = get_pixels(x_cord, y_cord)
    if token == "W":
        color = white
        pygame.draw.circle(display_surface, color, (left + int(square_size/2), top + int(square_size/2)), int(square_size/2))
    elif token == "B":
        color = black
        pygame.draw.circle(display_surface, color, (left + int(square_size/2), top + int(square_size/2)), int(square_size/2))

def draw_board(color1,color2):
    for boardX in range(board_height):
        for boardY in range(board_width):
            if boardX % 2 == 0:
                if boardY % 2 == 0:
                    pygame.draw.rect(display_surface, color1, (x_first+square_size * boardX, y_first + square_size * boardY, square_size, square_size))
                else:
                    pygame.draw.rect(display_surface, color2, (x_first+square_size * boardX, y_first + square_size * boardY, square_size, square_size))
            else:
                if boardY%2 == 0:
                    pygame.draw.rect(display_surface, color2, (x_first+square_size*boardX, y_first+square_size*boardY, square_size, square_size))
                else:
                    pygame.draw.rect(display_surface, color1, (x_first+square_size*boardX, y_first+square_size*boardY, square_size, square_size))
    draw_lines()
    for boardX in range(board_height):
        for boardY in range(board_width):
            if game_board[boardX][boardY] != "":
                place_token(boardX, boardY, game_board[boardX][boardY])

def draw_lines():
    for x in range(board_height):
        left, top = get_pixels(0,x)
        pygame.draw.line(display_surface,black,(left+square_size*0.5,top+square_size*0.5),(left+board_width*square_size-square_size*0.5,top+square_size*0.5))
    for y in range(board_width):
        left, top = get_pixels(y,0)
        pygame.draw.line(display_surface,black,(left+square_size*0.5,top+square_size*0.5),(left+square_size*0.5,top+board_height*square_size-square_size*0.5))

def get_pixels(box_x,box_y):
    top = y_first+box_y*square_size
    left = x_first+box_x*square_size
    return left, top

def get_square(x_cord, y_cord):
    for box_x in range(board_width):
        for box_y in range(board_height):
            left, top = get_pixels(box_x, box_y)
            box_rect = pygame.Rect(left, top, square_size, square_size)
            if box_rect.collidepoint(x_cord,y_cord):
                return box_x, box_y
    return -1, -1

def last_move(x_cord, y_cord, token):
    left, top = get_pixels(x_cord,y_cord)
    if token == "W":
        color = black
    else:
        color = white
    pygame.draw.circle(display_surface, blue, (left + int(square_size/2), top + int(square_size/2)), int(square_size/2*0.8))
    pygame.draw.circle(display_surface, color, (left + int(square_size/2), top + int(square_size/2)), int(square_size/2*0.7))

def add_lables():
    x_max, y_max = get_pixels(board_height-1,board_width-1)
    for i in range(board_height):
            label = myfont.render(str(chr(i+65)), 1, black)
            display_surface.blit(label, (x_first+i*square_size+square_size*0.3, y_first-square_size))
            display_surface.blit(label,(x_first+i*square_size+square_size*0.3, y_max+square_size))
    for i in range(board_width):
            number = myfont.render(str(i+1),1,black)
            display_surface.blit(number,(x_first-square_size, y_max-i*square_size))
            display_surface.blit(number,(x_max+square_size, y_max-i*square_size))

def undo(white_captured, black_captured,turn, token):
    x, y, removed = previous_move.pop()
    game_board[x][y] = ""
    if len(removed)>0:
       for element in removed:
            game_board[element[0]][element[1]] = token
    if token=="W":
        white_captured -= len(removed)
    else:
        black_captured -= len(removed)
    turn -= 1
    return white_captured, black_captured, turn

def game_end():
    easygui.msgbox("Please mark the dead stones now. When you are done, click d")
    mark_dead_strings()
    go_over()
    count_points()
    white_total = white_points-white_captured
    black_total = black_points-black_captured
    if white_total>black_total:
        easygui.msgbox("White wins with "+str(white_total)+" to "+str(black_total)+" points.")
    elif white_total<black_total:
        easygui.msgbox("Black wins with "+str(black_total)+" to "+str(white_total)+" points.")
    elif white_total==black_total:
        easygui.msgbox("Draw")


def mark_dead_strings():
    done = False
    draw_board(golden_rod, golden_rod)
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
                global crashed
                crashed = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouseX, mouseY = event.pos
                x, y = get_square(mouseX, mouseY)
                print(x,y)
                if x >= 0 and y >= 0 and game_board[x][y] != "":
                    game_board[x][y] = mark(x,y)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    done = True
        pygame.display.update()
        clock.tick(60)
    for x in range(board_height):
        for y in range(board_width):
            if "D" in game_board[x][y]:
                game_board[x][y] =""
    draw_board(golden_rod, golden_rod)
    return

def mark(x,y):
    if game_board[x][y] == "W" or game_board[x][y]=="B":
        game_board[x][y] += "D"
        draw_square(x,y)
    elif game_board[x][y] == "WD":
        game_board[x][y] = "W"
        draw_square(x,y)
    elif game_board[x][y] == "BD":
        game_board[x][y] = "B"
        draw_square(x,y)
    return game_board[x][y]

def draw_square(x_cord,y_cord):
    token = game_board[x_cord][y_cord]
    left, top = get_pixels(x_cord,y_cord)
    if token == "BD":
        first_color = blue
        second_color = black
    elif token=="B":
        first_color = black
        second_color = black
    elif token == "WD":
        first_color = blue
        second_color = white
    elif token=="W":
        first_color = white
        second_color = white
    pygame.draw.rect(display_surface, first_color, (left+square_size*0.2,top+square_size*0.2, square_size*0.6, square_size*0.6))
    pygame.draw.rect(display_surface,second_color,(left+square_size*0.25,top+square_size*0.25, square_size*0.5, square_size*0.5))

def go_over():
    for x in range(board_height):
        for y in range(board_width):
            if game_board[x][y]=="B" or game_board[x][y]=="W":
                flood_fill(x+1,y,game_board[x][y],visited)
                flood_fill(x-1,y,game_board[x][y],visited)
                flood_fill(x,y+1,game_board[x][y],visited)
                flood_fill(x,y-1,game_board[x][y],visited)

def flood_fill(x,y, token,visited):
    if x>=0 and x<board_width and y>=0 and y<board_height:
        if game_board[x][y] == "B" or game_board[x][y] == "W" or (x,y,token) in visited:
            return
        if game_board[x][y]=="":
            game_board[x][y]=0
        if token == "W":
            game_board[x][y] += 1
            visited.append((x,y,token))
        elif token == "B":
            game_board[x][y] -= 1
            visited.append((x,y,token))
        flood_fill(x+1,y,token,visited)
        flood_fill(x-1,y,token,visited)
        flood_fill(x,y+1,token,visited)
        flood_fill(x,y-1,token,visited)

def count_points():
     for x in range(board_height):
        for y in range(board_width):
            if game_board[x][y]==1:
                global white_points
                white_points += 1
            elif game_board[x][y]==-1:
                global black_points
                black_points +=1


crashed = False
board_width, board_height = game_start()
game_board = [["" for height in range(board_width)] for width in range(board_height)]
while not crashed:
    if turn % 2 == 1:
        token = "B"
    else:
        token = "W"
    draw_board(golden_rod, golden_rod)
    add_lables()
    if len(previous_move)>0:
        last_move(previous_move[-1][0],previous_move[-1][1],token)
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            crashed = True

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouseX, mouseY = event.pos
            x, y = get_square(mouseX, mouseY)
            if x >= 0 and y >= 0 and game_board[x][y] == "":
                game_board[x][y] = token
                removed =is_atari(x,y,token)
                if count_liberty(x,y,set(),0,token)[0] != 0:
                    previous_move.append((x,y,removed))
                    turn += 1
                    if token == "B":
                        white_captured += len(removed)
                    elif token == "W":
                        black_captured += len(removed)
                    pass_in_row = 0
                    if game_board == two_move_ago:
                        white_captured, black_captured, turn = undo(white_captured,black_captured,turn,reverse_token(token))
                    else:
                        two_move_ago = deepcopy(one_move_ago)
                        one_move_ago = deepcopy(game_board)
                else:
                    game_board[x][y] = ""

        elif event.type == pygame.KEYDOWN:
            #Undo button
            if event.key == pygame.K_u and len(previous_move)>0:
                white_captured, black_captured, turn = undo(white_captured,black_captured,turn,token)

            #Pass button
            elif event.key == pygame.K_p:
                pass_in_row +=1
                if pass_in_row==3:
                    game_end()
                else:
                    if token == "W":
                        black_captured +=1
                    else:
                        white_captured +=1
                    turn +=1

    pygame.display.update()
    clock.tick(60)
pygame.quit()
quit()