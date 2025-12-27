"use client";

import { useState, useRef, useCallback } from 'react';
import useWebSocket from 'react-use-websocket';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts';

// --- TYPES ---
interface Agent {
  id: number;
  x: number;
  y: number;
  hunger: number;
  is_alive: boolean;
}

// The new shape of data coming from Python
interface ServerPayload {
    money: number;
    agents: Agent[];
}

interface DataPoint {
    tick: number;
    alive: number;
    totalMoney: number;
}

interface GameState {
    tick: number;
    history: DataPoint[];
    stats: {
        alive: number;
        totalMoney: number;
    };
}

// --- CONFIGURATION ---
const GRID_SIZE = 10; 
const CELL_SIZE = 40; 
const CANVAS_SIZE = GRID_SIZE * CELL_SIZE;
const START_DATE = new Date("2025-01-01");
const SOCKET_URL = 'ws://127.0.0.1:8000/ws';

export default function Home() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const [game, setGame] = useState<GameState>({
    tick: 0,
    history: [],
    stats: { alive: 0, totalMoney: 0 }
  });

  const handleMessage = useCallback((event: WebSocketEventMap['message']) => {
    const rawData = JSON.parse(event.data) as ServerPayload;
    
    // Extract the new data structure
    const agents = rawData.agents;
    const globalMoney = rawData.money;

    // --- A. FAST RENDER ---
    const canvas = canvasRef.current;
    if (canvas) {
        const ctx = canvas.getContext('2d');
        if (ctx) {
            ctx.clearRect(0, 0, CANVAS_SIZE, CANVAS_SIZE);
            
            // Grid
            ctx.strokeStyle = '#333';
            ctx.lineWidth = 0.5;
            for (let i = 0; i <= GRID_SIZE; i++) {
                ctx.beginPath(); ctx.moveTo(i * CELL_SIZE, 0); ctx.lineTo(i * CELL_SIZE, CANVAS_SIZE); ctx.stroke();
                ctx.beginPath(); ctx.moveTo(0, i * CELL_SIZE); ctx.lineTo(CANVAS_SIZE, i * CELL_SIZE); ctx.stroke();
            }

            // Shop
            const shopX = Math.floor(GRID_SIZE / 2);
            const shopY = Math.floor(GRID_SIZE / 2);
            ctx.fillStyle = '#22c55e';
            ctx.fillRect(shopX * CELL_SIZE, shopY * CELL_SIZE, CELL_SIZE, CELL_SIZE);
            ctx.fillStyle = 'white';
            ctx.font = '12px Arial';
            ctx.fillText("BANK", shopX * CELL_SIZE + 5, shopY * CELL_SIZE + 25);

            // Agents
            agents.forEach((agent) => {
                if (!agent.is_alive) return; 
                const x = agent.x * CELL_SIZE;
                const y = agent.y * CELL_SIZE;

                ctx.fillStyle = '#ef4444';
                ctx.fillRect(x + 5, y + 5, CELL_SIZE - 10, CELL_SIZE - 10);

                ctx.fillStyle = 'black';
                ctx.fillRect(x + 5, y - 5, CELL_SIZE - 10, 4);
                const healthPercent = agent.hunger / 100;
                ctx.fillStyle = healthPercent > 0.5 ? '#00ff00' : '#ff0000';
                ctx.fillRect(x + 5, y - 5, (CELL_SIZE - 10) * healthPercent, 4);
            });
        }
    }

    // --- B. UPDATE STATS ---
    const aliveCount = agents.filter(a => a.is_alive).length;
    
    setGame(prev => {
        // Optimization: Dedupe
        if (prev.history.length > 0 && prev.stats.alive === aliveCount && prev.stats.totalMoney === globalMoney) {
             return prev;
        }

        const newTick = prev.tick + 1;
        const newHistoryPoint = { tick: newTick, alive: aliveCount, totalMoney: globalMoney };
        
        const newHistory = [...prev.history, newHistoryPoint];
        if (newHistory.length > 50) newHistory.shift();

        return {
            tick: newTick,
            history: newHistory,
            stats: { alive: aliveCount, totalMoney: globalMoney }
        };
    });
  }, []); 

  useWebSocket(SOCKET_URL, {
    onMessage: handleMessage,
    shouldReconnect: () => true,
    reconnectInterval: 1000,
    reconnectAttempts: 10,
  });

  const formatMoney = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const getCurrentDate = () => {
    const date = new Date(START_DATE);
    date.setDate(date.getDate() + game.tick); 
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  return (
    <div className="flex flex-col min-h-screen bg-gray-900 text-white font-mono">
      
      {/* HUD BAR */}
      <div className="w-full bg-gray-800 border-b-4 border-gray-700 p-4 shadow-lg flex justify-around items-center sticky top-0 z-10">
        <div className="text-center">
            <p className="text-gray-400 text-xs uppercase tracking-widest">Date</p>
            <p className="text-2xl font-bold text-white">{getCurrentDate()}</p>
        </div>
        
        <div className="text-center bg-gray-900 px-8 py-2 rounded-lg border border-gray-600">
            <p className="text-green-400 text-xs uppercase tracking-widest mb-1">Public Treasury</p>
            <p className="text-4xl font-extrabold text-green-400 tabular-nums">
                {formatMoney(game.stats.totalMoney)}
            </p>
        </div>

        <div className="text-center">
            <p className="text-gray-400 text-xs uppercase tracking-widest">Survivors</p>
            <p className="text-2xl font-bold text-blue-400">{game.stats.alive} / 10</p>
        </div>
      </div>

      <div className="flex flex-row justify-center p-10 gap-10">
        
        {/* Game View */}
        <div className="flex flex-col items-center">
            <div className="border-4 border-gray-700 rounded-lg shadow-2xl bg-black">
                <canvas ref={canvasRef} width={CANVAS_SIZE} height={CANVAS_SIZE} />
            </div>
            <p className="mt-2 text-gray-500 text-xs">Simulating 1 Day per 0.1s</p>
        </div>

        {/* Charts */}
        <div className="flex flex-col w-[500px]">
             <div className="h-64 bg-gray-800 p-4 rounded-lg border border-gray-700 shadow-xl">
                <h3 className="text-sm text-gray-400 mb-2">Resource Depletion</h3>
                <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={game.history}>
                        <XAxis hide dataKey="tick" />
                        <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }} />
                        <Legend />
                        <YAxis yAxisId="left" stroke="#60a5fa" domain={[0, 10]} />
                        <Line yAxisId="left" type="monotone" dataKey="alive" stroke="#60a5fa" strokeWidth={2} dot={false} name="Survivors" />
                        <YAxis yAxisId="right" orientation="right" stroke="#4ade80" />
                        <Line yAxisId="right" type="monotone" dataKey="totalMoney" stroke="#4ade80" strokeWidth={2} dot={false} name="Treasury ($)" />
                    </LineChart>
                </ResponsiveContainer>
            </div>

            <div className="mt-6 bg-red-900/20 border border-red-500/30 p-4 rounded text-sm text-red-200">
                <p className="font-bold mb-2">Scenario: Tragedy of the Commons</p>
                <ul className="list-disc pl-4 space-y-1">
                    <li>Shared Pot: $1000.</li>
                    <li>Cost to Eat: $50.</li>
                    <li>Once the pot hits $0, everyone starves.</li>
                    <li>Goal: Survive long enough to split the remainder?</li>
                </ul>
            </div>
        </div>

      </div>
    </div>
  );
}