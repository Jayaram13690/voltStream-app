import { Outlet } from "react-router-dom";
import { MobileMenu } from "../components/layout/MobileMenu.jsx";
import { Sidebar } from "../components/layout/Sidebar.jsx";
import { ChatWidget } from "../components/chat/ChatWidget.jsx";

export function MainLayout() {
  return (
    <div className="flex min-h-full bg-vs-bg">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col pb-20 md:pb-0">
        <main className="flex-1 p-4 lg:p-8 pt-6 lg:pt-8">
          <Outlet />
        </main>
      </div>
      <MobileMenu />
      <ChatWidget />
    </div>
  );
}
