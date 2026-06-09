import { useEffect, useState } from "react";
import { toast } from "sonner";
import { Header } from "../../components/layout/Header.jsx";
import { Spinner } from "../../components/ui/Spinner.jsx";
import { api } from "../../services/api.js";
import { useDeviceStore } from "../../store/deviceStore.js";
import { DeviceGrid } from "./components/DeviceGrid.jsx";

export function DevicesPage() {
  const devices = useDeviceStore((s) => s.devices);
  const setDevices = useDeviceStore((s) => s.setDevices);
  const patchLocal = useDeviceStore((s) => s.patchLocal);
  const [busyId, setBusyId] = useState(null);
  const [pageLoading, setPageLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setPageLoading(true);
      try {
        const res = await api.get("/api/v1/devices");
        if (!cancelled) setDevices(res.data);
      } catch {
        toast.error("Could not load devices.");
      } finally {
        if (!cancelled) setPageLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [setDevices]);

  // Listen for device status updates from agent operations
  useEffect(() => {
    const handleDeviceUpdate = () => {
      // Refresh devices when agent updates device status
      (async () => {
        try {
          const res = await api.get("/api/v1/devices");
          setDevices(res.data);
          // No toast - using inline notification in chat
        } catch {
          console.error("Failed to refresh device status");
          // Silent error handling
        }
      })();
    };

    window.addEventListener('deviceStatusUpdated', handleDeviceUpdate);
    return () => {
      window.removeEventListener('deviceStatusUpdated', handleDeviceUpdate);
    };
  }, [setDevices]);

  async function onToggle(device, nextOn) {
    setBusyId(device.id);
    try {
      const status = nextOn ? "on" : "off";
      const res = await api.patch(`/api/v1/devices/${device.id}`, { status });
      patchLocal(device.id, res.data);
      toast.success(`${device.name} is now ${status}.`);
    } catch {
      toast.error("Update failed.");
    } finally {
      setBusyId(null);
    }
  }

  if (pageLoading) {
    return (
      <div className="flex min-h-[40vh] items-center gap-2 text-vs-muted">
        <Spinner className="h-6 w-6" />
        Loading devices…
      </div>
    );
  }

  if (!devices.length) {
    return (
      <div>
        <Header title="Devices" subtitle="No devices returned from the API." />
        <div className="mt-4 text-sm text-vs-muted">Start the backend and reload.</div>
      </div>
    );
  }

  return (
    <div>
      <Header title="Devices" subtitle="Toggle loads and watch power change instantly." />
      <DeviceGrid devices={devices} busyId={busyId} onToggle={onToggle} />
    </div>
  );
}
