import { NavLink } from "react-router-dom";
import { Activity, CreditCard, LayoutDashboard, Settings, Zap } from "lucide-react";
import clsx from "clsx";

const items = [
  { to: "/", label: "Home", icon: LayoutDashboard },
  { to: "/analytics", label: "Analytics", icon: Activity },
  { to: "/devices", label: "Devices", icon: Zap },
  { to: "/billing", label: "Billing", icon: CreditCard },
  { to: "/settings", label: "Settings", icon: Settings },
];

export function MobileMenu({ onNavigate }) {
  return (
    <nav className="fixed bottom-0 left-0 right-0 z-40 border-t border-white/10 bg-vs-bg/90 px-2 py-2 backdrop-blur md:hidden">
      <div className="mx-auto flex max-w-lg items-center justify-between gap-1">
        {items.map((it) => (
          <NavLink
            key={it.to}
            to={it.to}
            end={it.to === "/"}
            onClick={() => onNavigate?.()}
            className={({ isActive }) =>
              clsx(
                "flex flex-1 flex-col items-center gap-1 rounded-xl px-2 py-2 text-[11px]",
                isActive ? "text-vs-primary" : "text-vs-muted",
              )
            }
          >
            <it.icon className="h-5 w-5" />
            {it.label}
          </NavLink>
        ))}
      </div>
    </nav>
  );
}
