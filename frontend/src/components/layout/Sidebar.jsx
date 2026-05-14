import { NavLink } from "react-router-dom";
import { Activity, CreditCard, LayoutDashboard, Settings, SlidersHorizontal, Zap } from "lucide-react";
import clsx from "clsx";

const items = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/analytics", label: "Analytics", icon: Activity },
  { to: "/devices", label: "Devices", icon: Zap },
  { to: "/billing", label: "Billing", icon: CreditCard },
  { to: "/settings", label: "Settings", icon: Settings },
];

export function Sidebar({ onNavigate }) {
  return (
    <aside className="group hidden w-20 hover:w-64 shrink-0 flex-col border-r border-vs-border bg-vs-bg py-6 transition-all duration-300 overflow-hidden md:flex relative z-50">
      <div className="mb-8 flex items-center px-4 w-full">
        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-vs-card text-vs-strong shadow-[0_0_15px_var(--theme-shadow)] transition-all">
          <SlidersHorizontal className="h-6 w-6" />
        </div>
        <div className="ml-3 whitespace-nowrap opacity-0 transition-opacity duration-300 group-hover:opacity-100">
          <div className="text-sm font-semibold text-vs-strong">VoltStream</div>
          <div className="text-xs text-vs-muted">Energy cockpit</div>
        </div>
      </div>
      <nav className="flex flex-col gap-4 w-full px-4">
        {items.map((it) => (
          <NavLink
            key={it.to}
            to={it.to}
            end={it.to === "/"}
            title={it.label}
            onClick={() => onNavigate?.()}
            className={({ isActive }) =>
              clsx(
                "group/link flex h-12 w-full items-center rounded-xl transition-all duration-300 overflow-hidden",
                isActive 
                  ? "bg-vs-primary text-white shadow-[0_0_15px_rgba(255,51,102,0.5)]" 
                  : "text-vs-muted hover:bg-vs-card hover:text-vs-strong"
              )
            }
          >
            <div className="flex h-12 w-12 shrink-0 items-center justify-center">
              <it.icon className={clsx("h-5 w-5 transition-transform duration-300 group-hover/link:scale-110")} />
            </div>
            <span className="whitespace-nowrap font-medium opacity-0 transition-opacity duration-300 group-hover:opacity-100">
              {it.label}
            </span>
          </NavLink>
        ))}
      </nav>
      <div className="mt-auto pt-4 flex flex-col items-center">
        {/* Intentionally blank */}
      </div>
    </aside>
  );
}
