import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

const demo = Array.from({ length: 14 }).map((_, i) => ({
  t: `${i * 2}m`,
  use: 2 + Math.sin(i / 2) * 0.8 + i * 0.05,
  solar: Math.max(0, 1.2 + Math.cos(i / 2) * 1.5),
}));

export function UsageChart({ gridUsage, solarGeneration }) {
  const data = demo.map((row, idx) =>
    idx === demo.length - 1 ? { ...row, use: gridUsage ?? row.use, solar: solarGeneration ?? row.solar } : row,
  );
  return (
    <div className="h-[280px] w-full mt-4">
      <ResponsiveContainer>
        <AreaChart data={data} margin={{ top: 8, right: 12, left: -15, bottom: 0 }}>
          <defs>
            <linearGradient id="gUse" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#ff3366" stopOpacity={0.35} />
              <stop offset="100%" stopColor="#ff3366" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="gSol" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#00e676" stopOpacity={0.35} />
              <stop offset="100%" stopColor="#00e676" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--theme-border)" vertical={false} />
          <XAxis dataKey="t" stroke="var(--theme-muted)" tick={{ fill: "var(--theme-muted)", fontSize: 12 }} tickLine={false} axisLine={false} />
          <YAxis 
            stroke="var(--theme-muted)" 
            tick={{ fill: "var(--theme-muted)", fontSize: 12 }} 
            tickLine={false} 
            axisLine={false}
            tickFormatter={(val) => Number(val).toFixed(1)} 
          />
          <Tooltip
            formatter={(value, name) => [Number(value).toFixed(2), name]}
            contentStyle={{
              background: "var(--theme-card)",
              border: "1px solid var(--theme-border)",
              borderRadius: 12,
              color: "var(--theme-text)",
              boxShadow: "0 10px 25px -5px var(--theme-shadow)"
            }}
            itemStyle={{ color: "var(--theme-strong)" }}
          />
          <Area type="monotone" dataKey="use" name="Grid draw (kW)" stroke="#ff3366" fill="url(#gUse)" strokeWidth={3} />
          <Area type="monotone" dataKey="solar" name="Solar (kW)" stroke="#00e676" fill="url(#gSol)" strokeWidth={3} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
