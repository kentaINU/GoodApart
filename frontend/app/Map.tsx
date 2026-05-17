"use client";

import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { useEffect, useState } from "react";
import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet";

interface Property {
    id: number | string;
    name: string;
    price: number;
    price_text: string;
    address: string;
    site_name: string;
    source_url: string;
    lat: number | null;
    lng: number | null;
}

const icon = L.icon({
    iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
    shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
    iconSize: [25, 41],
    iconAnchor: [12, 41],
});

export default function Map() {
    const [properties, setProperties] = useState<Property[]>([]);

    useEffect(() => {
        // APIのURL（未設定の場合はローカルホストをデフォルトにすると開発がスムーズです）
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

        fetch(`${apiUrl}/properties`)
            .then((res) => res.json())
            .then((data: Property[]) => setProperties(data))
            .catch((err) => console.error("Fetch error:", err));
    }, []);

    return (
        <MapContainer
            center={[33.5902, 130.4017]} // 福岡市役所付近
            zoom={13}
            style={{ height: "100vh", width: "100%" }}
        >
            <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />

            {properties.map((prop) => (
                // 💡 緯度経度が正常に存在する場合のみマーカーを描画
                prop.lat !== null && prop.lng !== null && (
                    <Marker key={prop.id} position={[prop.lat, prop.lng]} icon={icon}>
                        <Popup>
                            <div style={{ minWidth: "200px" }}>
                                <strong style={{ fontSize: "14px" }}>{prop.name}</strong>
                                <hr style={{ margin: "8px 0", border: "0", borderTop: "1px solid #eee" }} />

                                {/* 💡 きれいにパースした賃料テキストを表示 */}
                                <span style={{ color: "#e53e3e", fontWeight: "bold", fontSize: "14px" }}>
                                    {prop.price_text}
                                </span>
                                <br />

                                <span style={{ fontSize: "12px", color: "#666" }}>
                                    住所: {prop.address}
                                </span>
                                <br />

                                {/* 💡 元サイトへの直接リンクを設置 */}
                                <div style={{ marginTop: "10px", textAlign: "right" }}>
                                    <a
                                        href={prop.source_url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        style={{
                                            color: "#3182ce",
                                            textDecoration: "underline",
                                            fontSize: "12px",
                                            fontWeight: "bold"
                                        }}
                                    >
                                        元サイトで詳細を見る ↗
                                    </a>
                                </div>
                            </div>
                        </Popup>
                    </Marker>
                )
            ))}
        </MapContainer>
    );
}