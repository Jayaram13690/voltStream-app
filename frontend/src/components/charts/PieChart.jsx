import { Cell, Pie, PieChart as RPieChart, ResponsiveContainer, Tooltip } from "recharts";

export function PieChart({ data, nameKey, valueKey, colors, height = 260 }) {
  return (
    <div style={{ width: "100%", height }} className="min-h-[220px]">
      <ResponsiveContainer>
        <RPieChart>
          <Pie data={data} dataKey={valueKey} nameKey={nameKey} innerRadius={55} outerRadius={85} paddingAngle={3}>
            {data.map((_, i) => (
              <Cell key={i} fill={colors[i % colors.length]} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              background: "#111827",
              border: "1px solid rgba(255,255,255,0.08)",
              borderRadius: 12,
            }}
          />
        </RPieChart>
      </ResponsiveContainer>
    </div>
  );
}
