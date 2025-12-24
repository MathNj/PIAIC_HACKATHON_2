import type { Metadata } from "next";
import { Geist, Geist_Mono, Noto_Nastaliq_Urdu } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/components/AuthProvider";
import SharedLayout from "@/components/SharedLayout";
import { LanguageProvider } from "@/lib/i18n/LanguageContext";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

// Urdu font for RTL support
const notoNastaliqUrdu = Noto_Nastaliq_Urdu({
  variable: "--font-noto-urdu",
  subsets: ["arabic"],
  weight: ["400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "TODO App - Phase II",
  description: "Multi-user TODO application with JWT authentication",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} ${notoNastaliqUrdu.variable} antialiased`}
      >
        <LanguageProvider defaultLanguage="en">
          <AuthProvider>
            <SharedLayout>
              {children}
            </SharedLayout>
          </AuthProvider>
        </LanguageProvider>
      </body>
    </html>
  );
}
