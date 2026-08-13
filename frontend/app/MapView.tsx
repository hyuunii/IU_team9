"use client";
import { useEffect, useRef } from "react";
import type { Map as LeafletMap } from "leaflet";
export type Place={id:string;name:string;category:string;latitude:number;longitude:number;distance_km:number;hours:string;description:string;languages:string[];audience:string;sample?:boolean};
export default function MapView({places}:{places:Place[]}){
 const el=useRef<HTMLDivElement>(null), map=useRef<LeafletMap|null>(null);
 useEffect(()=>{let alive=true;(async()=>{const L=await import("leaflet");if(!alive||!el.current)return;if(map.current){map.current.remove();map.current=null;}const m=L.map(el.current,{zoomControl:true,attributionControl:true}).setView([37.4563,126.7052],11);map.current=m;L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",{attribution:"© OpenStreetMap"}).addTo(m);const bounds:L.LatLngExpression[]=[];places.forEach(p=>{bounds.push([p.latitude,p.longitude]);const icon=L.divIcon({className:"place-marker",html:"<span>⌖</span>",iconSize:[38,38],iconAnchor:[19,19]});L.marker([p.latitude,p.longitude],{icon}).addTo(m).bindPopup(`<b>${p.name}</b><br>${p.category}`)});if(bounds.length>1)m.fitBounds(bounds as L.LatLngBoundsExpression,{padding:[32,32]});else if(bounds.length===1)m.setView(bounds[0],13);setTimeout(()=>m.invalidateSize(),50)})();return()=>{alive=false;if(map.current){map.current.remove();map.current=null}}},[places]);
 return <div ref={el} className="real-map" aria-label="인천 도움처 지도"/>;
}
