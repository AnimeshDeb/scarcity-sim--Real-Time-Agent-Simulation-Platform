"use client";

import { useState, useEffect } from 'react';

// --- TYPES ---
type CellType = 'empty' | 'food' | 'agent';

interface Cell {
  type: CellType;
}

interface TrainingData {
  best_path: string[];
  food_locations: number[][];
  q_table: number[][][];
}

export default function Home() {
  // --- CONFIG ---
  const WORLD_DIMENSION = 6;
  const NUM_FOOD = 10;
  const NUM_EPISODES = 500;

  // --- STATE ---
  const [grid, setGrid] = useState<Cell[][]>([]);
  const [status, setStatus] = useState<string>("Ready to Train");
  const [loading, setLoading] = useState<boolean>(false);

  // Initialize
  useEffect(() => {
    resetGrid();
  }, []);

  const resetGrid = () => {
    const newGrid: Cell[][] = Array(WORLD_DIMENSION).fill(null).map(() =>
      Array(WORLD_DIMENSION).fill({ type: 'empty' })
    );
    setGrid(newGrid);
  };

  // --- API ---
  const trainAgent = async () => {
    setLoading(true);
    setStatus("Training AI in Python...");
    resetGrid();

    try {
      const res = await fetch('http://127.0.0.1:8000/ailogic/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          num_food: NUM_FOOD,
          world_dimension: WORLD_DIMENSION, // Matches Python singular
          num_episodes: NUM_EPISODES
        }),
      });

      if (!res.ok) throw new Error(`Server error: ${res.status}`);

      const data: TrainingData = await res.json();
      
      setStatus("Training Complete! Replaying Best Path...");
      animatePath(data.food_locations, data.best_path);

    } catch (error) {
      console.error(error);
      setStatus("Error: Is Python Backend Running?");
      setLoading(false);
    }
  };

  // --- ANIMATION ---
  const animatePath = (foodLocs: number[][], pathMoves: string[]) => {
    let agentRow = 0;
    let agentCol = 0;
    let currentFood = [...foodLocs];

    pathMoves.forEach((move, index) => {
      setTimeout(() => {
        if (move === "up") agentRow = Math.max(0, agentRow - 1);
        if (move === "down") agentRow = Math.min(WORLD_DIMENSION - 1, agentRow + 1);
        if (move === "left") agentCol = Math.max(0, agentCol - 1);
        if (move === "right") agentCol = Math.min(WORLD_DIMENSION - 1, agentCol + 1);

        // Eat food visually
        currentFood = currentFood.filter(f => !(f[0] === agentRow && f[1] === agentCol));

        drawFrame(agentRow, agentCol, currentFood);

        if (index === pathMoves.length - 1) {
          setLoading(false);
          setStatus("Goal Reached! 🏁");
        }
      }, index * 200);
    });
  };

  const drawFrame = (rAgent: number, cAgent: number, foodLocations: number[][]) => {
    const newGrid: Cell[][] = [];
    for (let r = 0; r < WORLD_DIMENSION; r++) {
      const row: Cell[] = [];
      for (let c = 0; c < WORLD_DIMENSION; c++) {
        let type: CellType = 'empty';
        if (foodLocations.some(f => f[0] === r && f[1] === c)) type = 'food';
        if (r === rAgent && c === cAgent) type = 'agent';
        row.push({ type });
      }
      newGrid.push(row);
    }
    setGrid(newGrid);
  };

  // --- RENDER ---
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-black text-white">
      <div style={{ textAlign: 'center' }}>
        <h1 className="text-4xl font-bold mb-4">🧠 AI Q-Learning Visualizer</h1>
        <p className="mb-6 text-xl text-gray-300">{status}</p>

        {/* --- GRID CONTAINER (FIXED WITH INLINE STYLES) --- */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: `repeat(${WORLD_DIMENSION}, 50px)`,
            gap: '4px',
            backgroundColor: '#333',
            padding: '10px',
            borderRadius: '8px',
            margin: '0 auto' // Center it
          }}
        >
          {grid.map((row, rIndex) =>
            row.map((cell, cIndex) => (
              <div
                key={`${rIndex}-${cIndex}`}
                style={{
                  width: '50px',
                  height: '50px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '24px',
                  borderRadius: '4px',
                  backgroundColor: 
                    cell.type === 'agent' ? '#2196f3' : 
                    cell.type === 'food' ? '#4caf50' : 
                    '#2a2a2a', // Dark gray for empty
                  transition: 'background-color 0.2s ease'
                }}
              >
                {cell.type === 'agent' && '🤖'}
                {cell.type === 'food' && '🍎'}
              </div>
            ))
          )}
        </div>

        <div className="mt-8">
          <button
            onClick={trainAgent}
            disabled={loading}
            className="px-6 py-3 bg-blue-500 hover:bg-blue-600 rounded text-lg font-bold disabled:opacity-50"
          >
            {loading ? "Thinking..." : "Start Training"}
          </button>
        </div>
      </div>
    </main>
  );
}