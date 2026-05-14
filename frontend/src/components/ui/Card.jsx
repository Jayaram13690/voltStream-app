import clsx from "clsx";

export function Card({ className, children, ...props }) {
  return (
    <div className={clsx("bento-card p-6", className)} {...props}>
      {children}
    </div>
  );
}
