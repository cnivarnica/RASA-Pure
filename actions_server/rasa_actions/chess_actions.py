from typing import Any, Text, Dict, List
from rasa_sdk import Action, FormValidationAction, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import SlotSet, FollowupAction
import chess
from .custom_actions_packages.chess_ai import get_best_move

class ChessGame:
    @staticmethod
    def get_board(tracker: Tracker) -> chess.Board:
        board_fen = tracker.get_slot("chess_board")
        return chess.Board(board_fen) if board_fen else None

    @staticmethod
    def set_promotion(move: chess.Move, board: chess.Board) -> None:
        if (move.promotion is None and 
            board.piece_at(move.from_square) and 
            board.piece_at(move.from_square).piece_type == chess.PAWN):
            if ((board.turn == chess.WHITE and chess.square_rank(move.to_square) == 7) or 
                (board.turn == chess.BLACK and chess.square_rank(move.to_square) == 0)):
                move.promotion = chess.QUEEN

class ActionNewChessGame(Action):
    def name(self) -> Text:
        return "action_new_chess_game"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain_dict: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        board = chess.Board()
        return [
            SlotSet("chess_board", board.fen()),
            SlotSet("chess_move", None),
            SlotSet("game_over", False),
            FollowupAction("action_ask_for_move")
        ]

class ActionAskForMove(Action):
    def name(self) -> Text:
        return "action_ask_for_move"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain_dict: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        board = ChessGame.get_board(tracker)
        if board:
            dispatcher.utter_message(response="utter_ask_for_move")
        else:
            dispatcher.utter_message(response="utter_no_game_in_progress")
        return [SlotSet("chess_move", None)]

class ActionChessMove(Action):
    def name(self) -> Text:
        return "action_chess_move"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain_dict: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_move = tracker.get_slot("chess_move")
        board = ChessGame.get_board(tracker)

        if not user_move:
            dispatcher.utter_message(response="utter_no_move_provided")
            return [FollowupAction("action_ask_for_move")]

        if not board:
            dispatcher.utter_message(response="utter_no_game_in_progress")
            return [FollowupAction("action_new_chess_game")]

        try:
            move = chess.Move.from_uci(user_move)
            ChessGame.set_promotion(move, board)

            if move in board.legal_moves:
                board.push(move)
                dispatcher.utter_message(response="utter_move_accepted", move=user_move)
                return [
                    SlotSet("chess_board", board.fen()),
                    SlotSet("chess_move", None),
                    FollowupAction("action_ai_move")
                ]
            else:
                dispatcher.utter_message(response="utter_illegal_move", move=user_move)
                return [FollowupAction("action_ask_for_move")]
        except ValueError:
            dispatcher.utter_message(response="utter_move_wrong_format", move=user_move)
            return [FollowupAction("action_ask_for_move")]

class ValidateChessMoveForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_chess_move_form"

    def validate_chess_move(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict,) -> Dict[Text, Any]:
        if not slot_value:
            dispatcher.utter_message(response="utter_no_move_provided")
            return {"chess_move": None}
        
        board = ChessGame.get_board(tracker)
        if not board:
            dispatcher.utter_message(response="utter_no_game_in_progress")
            return {"chess_move": None}

        try:
            move = chess.Move.from_uci(slot_value)
            ChessGame.set_promotion(move, board)

            if move in board.legal_moves:
                return {"chess_move": move.uci()}
            else:
                dispatcher.utter_message(response="utter_illegal_move", move=move)
                return {"chess_move": None}
        except ValueError:
            dispatcher.utter_message(response="utter_move_wrong_format", move=move)
            return {"chess_move": None}

class ActionAIMove(Action):
    def name(self) -> Text:
        return "action_ai_move"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain_dict: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        board = ChessGame.get_board(tracker)
        if not board:
            dispatcher.utter_message(response="utter_no_game_in_progress")
            return [FollowupAction("action_new_chess_game")]

        try:
            ai_move = get_best_move(board, time_limit=5, max_depth=3)
            ChessGame.set_promotion(ai_move, board)

            if ai_move in board.legal_moves:
                board.push(ai_move)
                dispatcher.utter_message(response="utter_ai_move", move=ai_move, board=board.unicode())
                return [
                    SlotSet("chess_board", board.fen()),
                    FollowupAction("action_check_game_over")
                ]
            else:
                dispatcher.utter_message(response="utter_ai_illegal_move", move=ai_move)
                return [FollowupAction("action_new_chess_game")]
        except Exception:
            dispatcher.utter_message(response="utter_ai_error")
            return [FollowupAction("action_new_chess_game")]

class ActionCheckGameOver(Action):
    def name(self) -> Text:
        return "action_check_game_over"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain_dict: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        board = ChessGame.get_board(tracker)
        if not board:
            dispatcher.utter_message(response="utter_no_game_in_progress")
            return [FollowupAction("action_new_chess_game")]

        try:
            if board.is_game_over():
                result = board.result()
                if result == "1-0":
                    message = "Game over. White wins!"
                elif result == "0-1":
                    message = "Game over. Black wins!"
                else:
                    message = "Game over. It's a draw!"

                if board.is_checkmate():
                    message += " Checkmate!"
                elif board.is_stalemate():
                    message += " Stalemate!"
                elif board.is_insufficient_material():
                    message += " Insufficient material to continue."
                elif board.is_seventyfive_moves():
                    message += " 75-move rule applied."
                elif board.is_fivefold_repetition():
                    message += " Fivefold repetition."

                dispatcher.utter_message(text=message)
                return [
                    SlotSet("game_over", True),
                    FollowupAction("action_end_game")
                ]
            else:
                return [FollowupAction("action_ask_for_move")]
        except Exception as e:
            dispatcher.utter_message(response="utter_status_error", error=str(e))
            return [FollowupAction("action_new_chess_game")]

class ActionEndGame(Action):
    def name(self) -> Text:
        return "action_end_game"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain_dict: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(response="utter_game_over")
        return []