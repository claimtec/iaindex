'use client'

import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip, Legend } from 'recharts'

interface IntentBreakdownProps {
  data: Array<{
    name: string
    value: number
    percentage: number
  }>
}

const COLORS = {
  training: 'hsl(217, 91%, 60%)', // blue
  retrieval: 'hsl(142, 76%, 36%)', // green
  scraping: 'hsl(25, 95%, 53%)', // orange
  unknown: 'hsl(0, 0%, 45%)', // gray
}

export function IntentBreakdown({ data }: IntentBreakdownProps) {
  return (
    <ResponsiveContainer width="100%" height={350}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          labelLine={false}
          label={({ name, percentage }) => `${name} ${percentage.toFixed(1)}%`}
          outerRadius={120}
          fill="#8884d8"
          dataKey="value"
        >
          {data.map((entry, index) => (
            <Cell
              key={`cell-${index}`}
              fill={COLORS[entry.name.toLowerCase() as keyof typeof COLORS] || COLORS.unknown}
            />
          ))}
        </Pie>
        <Tooltip
          content={({ active, payload }) => {
            if (active && payload && payload.length) {
              const data = payload[0].payload
              return (
                <div className="rounded-lg border bg-background p-3 shadow-sm">
                  <div className="grid gap-2">
                    <div className="flex flex-col">
                      <span className="text-[0.70rem] uppercase text-muted-foreground">
                        Intent Type
                      </span>
                      <span className="font-bold">{data.name}</span>
                    </div>
                    <div className="flex flex-col">
                      <span className="text-[0.70rem] uppercase text-muted-foreground">
                        Requests
                      </span>
                      <span className="font-bold">{data.value}</span>
                    </div>
                    <div className="flex flex-col">
                      <span className="text-[0.70rem] uppercase text-muted-foreground">
                        Percentage
                      </span>
                      <span className="font-bold">{data.percentage.toFixed(1)}%</span>
                    </div>
                  </div>
                </div>
              )
            }
            return null
          }}
        />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  )
}
