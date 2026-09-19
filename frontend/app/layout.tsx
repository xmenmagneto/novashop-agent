import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "NovaShop Support",
  description: "NovaShop Customer Support AI Agent",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
