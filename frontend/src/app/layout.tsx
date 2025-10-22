import "./globals.css";
import type { Metadata } from "next";
import { Toaster } from "sonner";

export const metadata: Metadata = {
  title: "PantryPal",
  description: "Inventory Management Dashboard",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="bg-background text-foreground">
      <body>
        {children}
        <Toaster richColors position="top-right" />
      </body>
    </html>
  );
}
