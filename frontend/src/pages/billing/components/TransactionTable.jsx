export function TransactionTable({ rows }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[520px] text-left text-sm">
        <thead className="text-xs uppercase tracking-wide text-vs-muted">
          <tr>
            <th className="py-2">Label</th>
            <th className="py-2">Amount</th>
            <th className="py-2">Date</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.id} className="border-t border-white/10">
              <td className="py-3">{r.label}</td>
              <td className="py-3 font-semibold">${Math.abs(r.amount).toFixed(2)}</td>
              <td className="py-3 text-vs-muted">{new Date(r.paid_at).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
