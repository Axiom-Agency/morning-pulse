import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Morning Pulse",
  description: "Daily market briefing for the Australian investor",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
