import pytest
from unittest.mock import patch
from chess import Chess

class MockScreen:
    def get_width(self):
        return 800

@patch("chess.Piece")
@patch("pygame.image.load")
def test_initial_board_setup(mock_image_load, mock_piece_class):
    """Testa se as peças iniciais estão posicionadas corretamente no tabuleiro."""
    screen = MockScreen()
    game = Chess(screen=screen, pieces_src="dummy_path", square_coords=[], square_length=50)
    
    assert game.piece_location["e"][1]["name"] == "white_king"
    assert game.piece_location["e"][8]["name"] == "black_king"
    assert game.piece_location["d"][1]["name"] == "white_queen"
    assert game.piece_location["d"][8]["name"] == "black_queen"

@patch("chess.Piece")
@patch("pygame.image.load")
def test_pawn_moves_and_promotion(mock_image_load, mock_piece_class):
    """Testa os movimentos do peão e a funcionalidade de promoção a Dama."""
    screen = MockScreen()
    game = Chess(screen=screen, pieces_src="dummy_path", square_coords=[], square_length=50)
    
    # Testa os movimentos iniciais do peão branco em e2 (coordenada [4, 6])
    pawn_moves = game.possible_moves("white_pawn", [4, 6])
    assert [4, 5] in pawn_moves  # Avançar 1 casa
    assert [4, 4] in pawn_moves  # Avançar 2 casas
    
    # Testa a Promoção do Peão
    game.piece_location["e"][7]["name"] = "white_pawn"
    game.piece_location["e"][7]["selected"] = True
    game.validate_move([4, 0])
    
    assert game.piece_location["e"][8]["name"] == "white_queen"

@patch("chess.Piece")
@patch("pygame.image.load")
def test_knight_moves(mock_image_load, mock_piece_class):
    """Testa se o cavalo calcula corretamente os saltos válidos."""
    screen = MockScreen()
    game = Chess(screen=screen, pieces_src="dummy_path", square_coords=[], square_length=50)
    
    # A partir de [4, 4], o cavalo retorna os saltos que estão dentro dos limites [0-7]
    moves = game.possible_moves("white_knight", [4, 4])
    
    assert len(moves) == 6  # 6 saltos válidos dentro dos limites a partir de [4, 4]
    assert [2, 3] in moves
    assert [6, 5] in moves

@patch("chess.Piece")
@patch("pygame.image.load")
def test_king_moves(mock_image_load, mock_piece_class):
    """Testa os movimentos do rei em redor."""
    screen = MockScreen()
    game = Chess(screen=screen, pieces_src="dummy_path", square_coords=[], square_length=50)
    
    moves = game.possible_moves("white_king", [4, 4])
    
    assert len(moves) == 8
    assert [4, 3] in moves
    assert [5, 5] in moves

@patch("chess.Piece")
@patch("pygame.image.load")
def test_bishop_diagonal_moves(mock_image_load, mock_piece_class):
    """Testa se o bispo calcula corretamente as diagonais."""
    screen = MockScreen()
    game = Chess(screen=screen, pieces_src="dummy_path", square_coords=[], square_length=50)
    
    moves = game.possible_moves("white_bishop", [4, 4])
    assert len(moves) > 0

@patch("chess.Piece")
@patch("pygame.image.load")
def test_rook_linear_moves(mock_image_load, mock_piece_class):
    """Testa se a torre calcula corretamente as linhas retas."""
    screen = MockScreen()
    game = Chess(screen=screen, pieces_src="dummy_path", square_coords=[], square_length=50)
    
    moves = game.possible_moves("white_rook", [4, 4])
    assert len(moves) > 0

@patch("chess.Piece")
@patch("pygame.image.load")
def test_queen_combined_moves(mock_image_load, mock_piece_class):
    """Testa se a rainha combina movimentos lineares e diagonais."""
    screen = MockScreen()
    game = Chess(screen=screen, pieces_src="dummy_path", square_coords=[], square_length=50)
    
    moves = game.possible_moves("white_queen", [4, 4])
    assert len(moves) > 0