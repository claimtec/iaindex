'use client';

import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { format } from 'date-fns';
import type { VisibilityHistory } from '@/types';

interface VisibilityChartProps {
  data: VisibilityHistory[];
  showPlatforms?: boolean;
}

export function VisibilityChart({ data, showPlatforms = false }: VisibilityChartProps) {
  const chartData = data.map(item => ({
    date: format(new Date(item.date), 'MMM d'),
    score: item.score,
    ...(showPlatforms && {
      ChatGPT: item.platformScores.chatgpt,
      Perplexity: item.platformScores.perplexity,
      Claude: item.platformScores.claude,
      Gemini: item.platformScores.gemini,
    })
  }));

  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis
          dataKey="date"
          stroke="#6b7280"
          fontSize={12}
        />
        <YAxis
          stroke="#6b7280"
          fontSize={12}
          domain={[0, 100]}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: '#fff',
            border: '1px solid #e5e7eb',
            borderRadius: '8px',
            padding: '8px 12px'
          }}
        />
        <Legend />
        {!showPlatforms ? (
          <Line
            type="monotone"
            dataKey="score"
            stroke="#0ea5e9"
            strokeWidth={2}
            dot={{ fill: '#0ea5e9', r: 4 }}
            activeDot={{ r: 6 }}
            name="Visibility Score"
          />
        ) : (
          <>
            <Line
              type="monotone"
              dataKey="ChatGPT"
              stroke="#10b981"
              strokeWidth={2}
              dot={{ fill: '#10b981', r: 3 }}
            />
            <Line
              type="monotone"
              dataKey="Perplexity"
              stroke="#0ea5e9"
              strokeWidth={2}
              dot={{ fill: '#0ea5e9', r: 3 }}
            />
            <Line
              type="monotone"
              dataKey="Claude"
              stroke="#a855f7"
              strokeWidth={2}
              dot={{ fill: '#a855f7', r: 3 }}
            />
            <Line
              type="monotone"
              dataKey="Gemini"
              stroke="#f59e0b"
              strokeWidth={2}
              dot={{ fill: '#f59e0b', r: 3 }}
            />
          </>
        )}
      </LineChart>
    </ResponsiveContainer>
  );
}
