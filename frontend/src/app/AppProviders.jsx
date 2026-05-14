import { Toaster } from "sonner";

export function AppProviders({ children }) {
  return (
    <>
      {children}
      <Toaster richColors theme="dark" position="top-right" />
    </>
  );
}
