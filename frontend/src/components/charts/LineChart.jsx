import { CartesianGrid, Line, LineChart as RLineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export function LineChart({ data, xKey, series, height = 280 }) {
  return (
    <div style={{ width: "100%", height }} className="min-h-[220px]">
      <ResponsiveContainer>
        <RLineChart data={data} margin={{ top: 8, right: 12, left: -15, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--theme-border)" vertical={false} />
          <XAxis dataKey={xKey} stroke="var(--theme-muted)" tick={{ fill: "var(--theme-muted)", fontSize: 12 }} tickLine={false} axisLine={false} />
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
          {series.map((s) => (
            <Line key={s.dataKey} type="monotone" dataKey={s.dataKey} name={s.name} stroke={s.color} strokeWidth={2} dot={false} />
          ))}
        </RLineChart>
      </ResponsiveContainer>
    </div>
  );
}
