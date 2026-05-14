import { LineChart } from "../../../components/charts/LineChart.jsx";

export function BillingChart() {
  const data = [
    { m: "Jan", bill: 118 },
    { m: "Feb", bill: 112 },
    { m: "Mar", bill: 121 },
    { m: "Apr", bill: 119 },
    { m: "May", bill: 128 },
  ];
  return <LineChart data={data} xKey="m" series={[{ dataKey: "bill", name: "Bill ($)", color: "#3b82f6" }]} height={280} />;
}
