from flask import Flask, send_from_directory, request, jsonify
import chess
import chess.engine
import os

# Look for index.html in the root folder
app = Flask(__name__, static_folder='.', static_url_path='')

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/move', methods=['POST'])
def make_move():
    data = request.json
    board = chess.Board(data['fen'])
    difficulty = data['difficulty']
    
    if not board.is_game_over():
        try:
            # 1. Using the absolute path for Stockfish in Codespaces/Linux
            # This is where 'sudo apt-get install stockfish' places it
            engine_path = "/usr/games/stockfish"
            
            # 2. Open engine
            engine = chess.engine.SimpleEngine.popen_uci(engine_path)
            
            skill_map = {"Easy": 0, "Medium": 10, "Impossible": 20}
            engine.configure({"Skill Level": skill_map.get(difficulty, 0)})
            
            # Give the engine a bit more time for "Impossible"
            limit_time = 0.5 if difficulty == "Impossible" else 0.05
            result = engine.play(board, chess.engine.Limit(time=limit_time))
            
            board.push(result.move)
            engine.quit()
            
        except Exception as e:
            # This will print the error in your terminal for debugging
            print(f"--- ENGINE ERROR: {e} ---")
            return jsonify({"error": str(e)}), 500

    return jsonify({
        'fen': board.fen(),
        'game_over': board.is_game_over(),
        'checkmate': board.is_checkmate()
    })

if __name__ == '__main__':
    # Ensure port 5000 is open in Codespaces
    app.run(host='0.0.0.0', port=5000, debug=True)
    