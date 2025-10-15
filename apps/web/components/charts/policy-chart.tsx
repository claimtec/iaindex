'use client'

import { Area, AreaChart, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis, Legend } from 'recharts'

interface PolicyChartProps {
  data: Array<{
    date: string
    allowed: number
    denied: number
  }>
  variant?: 'line' | 'area'
}

export function PolicyChart({ data, variant = 'line' }: PolicyChartProps) {
  const ChartComponent = variant === 'area' ? AreaChart : LineChart
  const DataComponent = variant === 'area' ? Area : Line

  return (
    <ResponsiveContainer width="100%" height={350}>
      <ChartComponent data={data}>
        <XAxis
          dataKey="date"
          stroke="#888888"
          fontSize={12}
          tickLine={false}
          axisLine={false}
        />
        <YAxis
          stroke="#888888"
          fontSize={12}
          tickLine={false}
          axisLine={false}
        />
        <Tooltip
          content={({ active, payload }) => {
            if (active && payload && payload.length) {
              return (
                <div className="rounded-lg border bg-background p-3 shadow-sm">
                  <div className="grid gap-2">
                    <div className="flex flex-col">
                      <span className="text-[0.70rem] uppercase text-muted-foreground">
                        Date
                      </span>
                      <span className="font-bold text-muted-foreground">
                        {payload[0].payload.date}
                      </span>
                    </div>
                    <div className="flex items-center justify-between gap-4">
                      <div className="flex flex-col">
                        <span className="text-[0.70rem] uppercase text-muted-foreground">
                          Allowed
                        </span>
                        <span className="font-bold text-green-600">
                          {payload[0].payload.allowed}
                        </span>
                      </div>
                      <div className="flex flex-col">
                        <span className="text-[0.70rem] uppercase text-muted-foreground">
                          Denied
                        </span>
                        <span className="font-bold text-red-600">
                          {payload[0].payload.denied}
                        </span>
                      </div>
                    </div>
                    <div className="flex flex-col pt-2 border-t">
                      <span className="text-[0.70rem] uppercase text-muted-foreground">
                        Compliance Rate
                      </span>
                      <span className="font-bold">
                        {(
                          (payload[0].payload.allowed /
                            (payload[0].payload.allowed + payload[0].payload.denied)) *
                          100
                        ).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                </div>
              )
            }
            return null
          }}
        />
        <Legend />
        {variant === 'area' ? (
          <>
            <Area
              type="monotone"
              dataKey="allowed"
              stackId="1"
              stroke="hsl(142, 76%, 36%)"
              fill="hsl(142, 76%, 36%)"
              fillOpacity={0.6}
            />
            <Area
              type="monotone"
              dataKey="denied"
              stackId="1"
              stroke="hsl(0, 84%, 60%)"
              fill="hsl(0, 84%, 60%)"
              fillOpacity={0.6}
            />
          </>
        ) : (
          <>
            <Line
              type="monotone"
              dataKey="allowed"
              stroke="hsl(142, 76%, 36%)"
              strokeWidth={2}
              activeDot={{ r: 6 }}
            />
            <Line
              type="monotone"
              dataKey="denied"
              stroke="hsl(0, 84%, 60%)"
              strokeWidth={2}
              activeDot={{ r: 6 }}
            />
          </>
        )}
      </ChartComponent>
    </ResponsiveContainer>
  )
}
