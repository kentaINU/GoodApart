"use client";

import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { useEffect, useState } from "react";
import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet";

const icon = L.icon({
    iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
    shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
    iconSize: [25, 41],
    iconAnchor: [12, 41],
});

export default function Map() {
    const [properties, setProperties] = useState<any[]>([]);

    // FastAPIからデータを取ってくる
    useEffect(() => {
        fetch(`${process.env.NEXT_PUBLIC_API_URL}/properties`)
            .then((res) => res.json())
            .then((data) => setProperties(data));
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
                prop.lat && prop.lng && (
                    <Marker key={prop.id} position={[prop.lat, prop.lng]} icon={icon}>
                        <Popup>
                            <strong>{prop.name}</strong><br />
                            {prop.price}円/日<br />
                            {prop.address}
                        </Popup>
                    </Marker>
                )
            ))}
        </MapContainer>
    );
}