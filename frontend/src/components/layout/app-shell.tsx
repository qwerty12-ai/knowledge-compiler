import type { ReactNode } from "react";
import { Suspense } from "react";
import { Sidebar } from "./sidebar";
import { Topbar } from "./topbar";

interface AppShellProps {
  children: ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="flex min-h-screen">
        <Suspense fallback={null}>
          <Sidebar />
        </Suspense>

        <div className="flex min-w-0 flex-1 flex-col">
          <Suspense fallback={null}>
            <Topbar />
          </Suspense>

          <main className="min-w-0 flex-1 overflow-x-hidden">
            {children}
          </main>
        </div>
      </div>
    </div>
  );
}