"use client";

import dynamic from "next/dynamic";

const Map = dynamic(() => import("./Map"), {
  ssr: false,
  loading: () => <p>地図を読み込み中...</p>
});

export default function Home() {
  return (
    <main>
      <h1 style={{ padding: "10px", textAlign: "center" }}>
        福岡マンスリーマンションマップ
      </h1>
      <Map />
    </main>
  );
}