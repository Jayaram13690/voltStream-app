import { useState } from "react";
import { toast } from "sonner";
import { Header } from "../../components/layout/Header.jsx";
import { Button } from "../../components/ui/Button.jsx";
import { Card } from "../../components/ui/Card.jsx";
import { Input } from "../../components/ui/Input.jsx";
import { useAuthStore } from "../../store/authStore.js";

export function SettingsPage() {
  const { theme, setTheme } = useAuthStore();
  const [email, setEmail] = useState("you@example.com");

  return (
    <div>
      <Header title="Settings" subtitle="Manage your profile and appearance preferences." />
      <div className="max-w-2xl flex flex-col gap-6">
        <Card>
          <div className="text-lg font-semibold text-vs-strong mb-6">Appearance</div>
          <div className="flex gap-4">
            <Button 
              variant={theme === "light" ? "primary" : "outline"} 
              onClick={() => setTheme("light")}
            >
              Light Mode
            </Button>
            <Button 
              variant={theme === "dark" ? "primary" : "outline"} 
              onClick={() => setTheme("dark")}
            >
              Dark Mode
            </Button>
          </div>
        </Card>

        <Card>
          <div className="text-lg font-semibold text-vs-strong mb-6">Profile</div>
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
            <div>
              <div className="mb-2 text-sm font-medium text-vs-muted">Contact email</div>
              <Input 
                value={email} 
                onChange={(e) => setEmail(e.target.value)} 
                className="w-full bg-vs-bg border-vs-border text-vs-strong focus:border-vs-primary focus:ring-1 focus:ring-vs-primary"
              />
            </div>
            <div className="flex items-end">
              <Button 
                onClick={() => toast.success("Saved locally (demo)")}
                className="w-full md:w-auto bg-vs-primary hover:bg-vs-primary/80 text-white transition-colors"
              >
                Save preferences
              </Button>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
