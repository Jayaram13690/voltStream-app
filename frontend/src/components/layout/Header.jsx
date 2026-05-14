export function Header({ title, subtitle }) {
  return (
    <div className="mb-8 mt-2">
      <h1 className="text-3xl font-semibold tracking-tight text-vs-strong">{title}</h1>
      {subtitle ? <p className="mt-2 text-sm text-vs-muted">{subtitle}</p> : null}
    </div>
  );
}
