import pygame
from pygame.locals import *
import random

from piece import Piece
from utils import Utils

class Chess:
    def __init__(self, screen, pieces_src, square_coords, square_length):
        self.screen = screen
        self.chess_pieces = Piece(pieces_src, cols=6, rows=2)
        self.board_locations = square_coords
        self.square_length = square_length
        
        # Turn tracking dictionary
        self.turn = {"black": 0, "white": 0}
        self.moves = []
        self.utils = Utils()
        self.winner = ""
        self.captured = []

        # Mapping piece names to index on spritesheet
        self.pieces = {
            "white_pawn": 5, "white_knight": 3, "white_bishop": 2,
            "white_rook": 4, "white_king": 0, "white_queen": 1,
            "black_pawn": 11, "black_knight": 9, "black_bishop": 8,
            "black_rook": 10, "black_king": 6, "black_queen": 7
        }

        self.reset()
    
    def reset(self):
        self.moves = []
        
        self.turn["black"] = 0
        self.turn["white"] = 1
        # Structured board representation using explicit dictionaries
        self.piece_location = {}
        for i in range(97, 105):
            col_char = chr(i)
            self.piece_location[col_char] = {}
            for a in range(1, 9):
                x_coord = i - 97
                y_coord = 8 - a
                self.piece_location[col_char][a] = {
                    "name": "", 
                    "selected": False, 
                    "coord": [x_coord, y_coord]
                }

        self._setup_initial_board()

    def _setup_initial_board(self):
        back_row_pieces = ["rook", "knight", "bishop", "queen", "king", "bishop", "knight", "rook"]
        columns = [chr(i) for i in range(97, 105)]

        for idx, col in enumerate(columns):
            piece_type = back_row_pieces[idx]
            # Black pieces
            self.piece_location[col][8]["name"] = f"black_{piece_type}"
            self.piece_location[col][7]["name"] = "black_pawn"
            # White pieces
            self.piece_location[col][2]["name"] = "white_pawn"
            self.piece_location[col][1]["name"] = f"white_{piece_type}"

    def play_turn(self):
        white_color = (255, 255, 255)
        small_font = pygame.font.SysFont("comicsansms", 20)
        
        current_turn = "Black" if self.turn["black"] else "White"
        turn_text = small_font.render(f"Turn: {current_turn}", True, white_color)
        
        self.screen.blit(turn_text, ((self.screen.get_width() - turn_text.get_width()) // 2, 10))
        
        active_color = "black" if self.turn["black"] else "white"
        self.move_piece(active_color)

    def draw_pieces(self):
        green_surface = self._create_surface_with_color((0, 194, 39, 170))
        blue_surface = self._create_surface_with_color((28, 21, 212, 170))

        # Draw selection backgrounds and valid move highlights
        for val in self.piece_location.values():
            for data in val.values():
                if data["selected"] and data["name"]:
                    color = "black" if data["name"].startswith("black") else "white"
                    surface = green_surface if color == "black" else blue_surface
                    
                    piece_coord_x, piece_coord_y = data["coord"]
                    self.screen.blit(surface, self.board_locations[piece_coord_x][piece_coord_y])
                    
                    for move in self.moves:
                        mx, my = move
                        if 0 <= mx < 8 and 0 <= my < 8:
                            self.screen.blit(surface, self.board_locations[mx][my])
        
        # Draw all active pieces on the board
        for val in self.piece_location.values():
            for data in val.values():
                if data["name"]:
                    piece_coord_x, piece_coord_y = data["coord"]
                    self.chess_pieces.draw(
                        self.screen, 
                        data["name"], 
                        self.board_locations[piece_coord_x][piece_coord_y]
                    )

    def _create_surface_with_color(self, color):
        surface = pygame.Surface((self.square_length, self.square_length), pygame.SRCALPHA)
        surface.fill(color)
        return surface

    def possible_moves(self, piece_name, piece_coord):
        positions = []
        if not piece_name:
            return positions

        x_coord, y_coord = piece_coord
        piece_type = piece_name.split("_")[1]
        piece_color = piece_name.split("_")[0]

        if piece_type == "bishop":
            positions = self.diagonal_moves(positions, piece_name, piece_coord)
        elif piece_type == "pawn":
            positions = self._get_pawn_moves(piece_name, piece_coord, piece_color)
        elif piece_type == "rook":
            positions = self.linear_moves(positions, piece_name, piece_coord)
        elif piece_type == "knight":
            positions = self._get_knight_moves(x_coord, y_coord)
        elif piece_type == "king":
            positions = self._get_king_moves(x_coord, y_coord)
        elif piece_type == "queen":
            positions = self.diagonal_moves(positions, piece_name, piece_coord)
            positions = self.linear_moves(positions, piece_name, piece_coord)

        # Filter out moves that overlap friendly pieces
        return [
            pos for pos in positions 
            if not self._is_friendly_piece(pos, piece_color)
        ]

    def _is_friendly_piece(self, pos, current_color):
        x, y = pos
        col_char = chr(97 + x)
        row_no = 8 - y
        des_piece = self.piece_location[col_char][row_no]["name"]
        return des_piece.startswith(current_color)

    def _get_knight_moves(self, x, y):
        positions = []
        knight_offsets = [
            (-2, -1), (-2, 1), (-1, -2), (1, -2),
            (2, -1), (2, 1), (-1, 2), (1, 2)
        ]
        for dx, dy in knight_offsets:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 8 and 0 <= ny < 8:
                positions.append([nx, ny])
        return positions

    def _get_king_moves(self, x, y):
        positions = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < 8 and 0 <= ny < 8:
                    positions.append([nx, ny])
        return positions

    def _get_pawn_moves(self, piece_name, piece_coord, color):
        positions = []
        x_coord, y_coord = piece_coord
        direction = 1 if color == "black" else -1
        start_row_y = 1 if color == "black" else 6
        
        # Forward move
        ny = y_coord + direction
        if 0 <= ny < 8:
            col_char = chr(97 + x_coord)
            row_no = 8 - ny
            front_piece = self.piece_location[col_char][row_no]["name"]
            
            if not front_piece:
                positions.append([x_coord, ny])
                # Double step from start
                nny = y_coord + (2 * direction)
                if y_coord == start_row_y and not self.piece_location[col_char][8 - nny]["name"]:
                    positions.append([x_coord, nny])

        # Diagonal captures
        enemy_color = "white" if color == "black" else "black"
        for dx in [-1, 1]:
            nx, ny = x_coord + dx, y_coord + direction
            if 0 <= nx < 8 and 0 <= ny < 8:
                col_char = chr(97 + nx)
                row_no = 8 - ny
                target = self.piece_location[col_char][row_no]["name"]
                if target.startswith(enemy_color):
                    positions.append([nx, ny])
                    
        return positions

    def move_piece(self, turn):
        square = self.get_selected_square()
        if not square:
            return

        piece_name, column_char, row_no = square
        piece_color = piece_name.split("_")[0] if piece_name else ""
        x, y = self.piece_location[column_char][row_no]["coord"]

        if piece_name and piece_color == turn:
            self.moves = self.possible_moves(piece_name, [x, y])

        target_data = self.piece_location[column_char][row_no]
        for move in self.moves:
            if move == [x, y]:
                if target_data["name"].startswith(turn) or not target_data["name"]:
                    self.validate_move([x, y])
                else:
                    self.capture_piece(turn, [column_char, row_no], [x, y])

        if piece_color == turn:
            for k in self.piece_location.keys():
                for key in self.piece_location[k].keys():
                    self.piece_location[k][key]["selected"] = False
            target_data["selected"] = True

    def get_selected_square(self):
        if not self.utils.left_click_event():
            return None

        mouse_event = self.utils.get_mouse_event()
        for i, row_list in enumerate(self.board_locations):
            for j, coords in enumerate(row_list):
                rect = pygame.Rect(coords[0], coords[1], self.square_length, self.square_length)
                if rect.collidepoint(mouse_event[0], mouse_event[1]):
                    column_char = chr(97 + i)
                    row_no = 8 - j
                    piece_name = self.piece_location[column_char][row_no]["name"]
                    return [piece_name, column_char, row_no]
        return None

    def capture_piece(self, turn, chess_board_coord, piece_coord):
        x, y = piece_coord
        column_char, row_no = chess_board_coord
        target_piece = self.piece_location[column_char][row_no]
        
        if target_piece["name"] == "white_king":
            self.winner = "Black"
            print("Black wins")
        elif target_piece["name"] == "black_king":
            self.winner = "White"
            print("White wins")

        self.captured.append(target_piece)
        self.validate_move(piece_coord)

    def validate_move(self, destination):
        des_col_char = chr(97 + destination[0])
        des_row_no = 8 - destination[1]

        for k in self.piece_location.keys():
            for key in self.piece_location[k].keys():
                board_piece = self.piece_location[k][key]

                if board_piece["selected"]:
                    board_piece["selected"] = False
                    piece_name = board_piece["name"]
                    
                    self.piece_location[des_col_char][des_row_no]["name"] = piece_name
                    board_piece["name"] = ""

                    # Switch turn
                    if self.turn["black"]:
                        self.turn["black"] = 0
                        self.turn["white"] = 1
                    else:
                        self.turn["black"] = 1
                        self.turn["white"] = 0

                    print(f"{piece_name} moved from {k}{key} to {des_col_char}{des_row_no}")

    def diagonal_moves(self, positions, piece_name, piece_coord):
        directions = [(-1, -1), (1, 1), (-1, 1), (1, -1)]
        piece_color = piece_name.split("_")[0]

        for dx, dy in directions:
            x, y = piece_coord
            while True:
                x += dx
                y += dy
                if not (0 <= x < 8 and 0 <= y < 8):
                    break
                
                positions.append([x, y])
                col_char = chr(97 + x)
                row_no = 8 - y
                target_piece = self.piece_location[col_char][row_no]["name"]

                if target_piece:
                    if not target_piece.startswith(piece_color):
                        break
                    break
        return positions

    def linear_moves(self, positions, piece_name, piece_coord):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        piece_color = piece_name.split("_")[0]

        for dx, dy in directions:
            x, y = piece_coord
            while True:
                x += dx
                y += dy
                if not (0 <= x < 8 and 0 <= y < 8):
                    break
                
                positions.append([x, y])
                col_char = chr(97 + x)
                row_no = 8 - y
                target_piece = self.piece_location[col_char][row_no]["name"]

                if target_piece:
                    if not target_piece.startswith(piece_color):
                        break
                    break
        return positions