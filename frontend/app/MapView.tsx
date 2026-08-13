"use client";
import { useEffect, useRef } from "react";
import type { Map as LeafletMap } from "leaflet";

export type Place={id:string;name:string;category:string;latitude:number;longitude:number;address:string;district:string;phone:string;hours:string;description:string;website:string;source:string};

export default function MapView({places,onSelect}:{places:Place[];onSelect?:(place:Place)=>void}){
 const el=useRef<HTMLDivElement>(null),map=useRef<LeafletMap|null>(null),selectHandler=useRef(onSelect);
 selectHandler.current=onSelect;
 useEffect(()=>{let alive=true;(async()=>{
  const L=await import("leaflet");if(!alive||!el.current)return;
  if(map.current){map.current.remove();map.current=null}
  const m=L.map(el.current,{zoomControl:true,attributionControl:true}).setView([37.4563,126.7052],11);map.current=m;
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",{attribution:"© OpenStreetMap"}).addTo(m);
  const pinIcon=L.icon({
   iconUrl:"/characters/map-pin.png",
   iconSize:[48,50],
   iconAnchor:[24,48],
   popupAnchor:[0,-43],
   className:"character-map-marker",
  });
  const bounds:L.LatLngExpression[]=[];
  places.forEach(place=>{
   bounds.push([place.latitude,place.longitude]);
   const detail=[place.category,place.address,place.phone].filter(Boolean).join("<br>");
   L.marker([place.latitude,place.longitude],{icon:pinIcon}).addTo(m).bindPopup(`<b>${place.name}</b><br>${detail}`).on("click",()=>selectHandler.current?.(place));
  });
  if(bounds.length>1)m.fitBounds(bounds as L.LatLngBoundsExpression,{padding:[32,32]});else if(bounds.length===1)m.setView(bounds[0],13);
  setTimeout(()=>m.invalidateSize(),50);
 })();return()=>{alive=false;if(map.current){map.current.remove();map.current=null}}},[places]);
 return <div ref={el} className="real-map" aria-label="인천 도움처 지도"/>;
}
