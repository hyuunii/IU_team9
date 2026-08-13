import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "인조이 | 인천 생활 시작하기",
  description: "외국인 주민과 유학생을 위한 인천 생활 맞춤 온보딩",
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}
