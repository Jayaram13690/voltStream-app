import { LineChart } from "../../../components/charts/LineChart.jsx";

export function ConsumptionChart({ points }) {
  const data = points.map((p) => ({ label: p.label, consumption: p.consumption, solar: p.solar }));
  return (
    <LineChart
      data={data}
      xKey="label"
      series={[
        { dataKey: "consumption", name: "Consumption", color: "#ff3366" },
        { dataKey: "solar", name: "Solar", color: "#00e676" },
      ]}
      height={300}
    />
  );
}
