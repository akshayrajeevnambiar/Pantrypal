import Nav from "@/components/nav";

export default function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen">
      <Nav />
      <main className="mx-auto max-w-7xl p-4">{children}</main>
    </div>
  );
}
