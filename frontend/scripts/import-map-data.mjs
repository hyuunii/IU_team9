import { readFile, writeFile, mkdir } from "node:fs/promises";
import { resolve } from "node:path";

const sourcePath = resolve(process.cwd(), "../../데이터/지도/기관 정보 3ba158a56065808caa6ded18d427e775.md");
const outputPath = resolve(process.cwd(), "public/nearby_places.json");
const cachePath = resolve(process.cwd(), "scripts/geocode-cache.json");
const categoryNames = {
  "교통":"교통", "금융":"은행·금융", "의료":"의료", "주거":"주거", "직장":"직장·노동",
  "행정, 복지":"행정·복지", "통신, 인터넷":"통신", "생활, 편의시설":"생활·편의", "긴급상황":"긴급상황"
};
const fallbackCenters = {
  "연수구":[37.409,126.678], "남동구":[37.447,126.731], "서해구":[37.506,126.676],
  "서구":[37.545,126.676], "부평구":[37.507,126.721], "미추홀구":[37.463,126.650],
  "중구":[37.473,126.621], "광명시":[37.416,126.884]
};

const text = await readFile(sourcePath, "utf8");
const lines = text.split(/\r?\n/);
const entries = [];
let category = "", current = null;
for (const line of lines) {
  const section = line.match(/^###\s+\d+\.\s+(.+)$/);
  if (section) { category = categoryNames[section[1].trim()] || section[1].trim(); continue; }
  const item = line.match(/^-\s+(.+)$/);
  if (item) {
    if (current) entries.push(current);
    current = { name:item[1].trim(), category, details:[] };
    continue;
  }
  const detail = line.match(/^\s{4}-\s+(.+)$/);
  if (detail && current) current.details.push(detail[1].trim());
}
if (current) entries.push(current);

function stripLabel(value) { return value.replace(/^(위치|전화번호|운영시간|진료과목|긴급신고):\s*/i, "").trim(); }
function districtOf(address) { return address.match(/(연수구|남동구|서해구|서구|부평구|미추홀구|중구|광명시)/)?.[1] || "인천"; }
function findAddress(details) {
  return stripLabel(details.find(value => /^(위치:\s*)?(인천|경기)/.test(value)) || "");
}
function findPhone(details) {
  const candidate = details.find(value => /(?:0\d{1,2}|0507|112|119)[-\s]\d/.test(value));
  return candidate?.match(/(?:0\d{1,2}|0507|112|119)(?:\s*-\s*\d{3,4}){1,2}/)?.[0].replace(/\s*-\s*/g,"-") || "";
}
function findHours(details) {
  return stripLabel(details.find(value => /운영시간|평일|매일|월[~-]|화[~-]|일[~-]|24시간|연중무휴/.test(value)) || "");
}
function sleep(ms) { return new Promise(resolve => setTimeout(resolve, ms)); }
let cache = {};
try { cache = JSON.parse(await readFile(cachePath, "utf8")); } catch {}

async function geocode(address) {
  if (!address) return null;
  if (cache[address]) return cache[address];
  const normalized = address.replace("서해구", "서구").replace("인천광역시", "인천");
  const roadOnly = normalized.match(/^((?:인천|경기)\s+\S+[시구]\s+.+?(?:대로|로|길)(?:\d+번길)?\s+\d+(?:-\d+)?)/)?.[1];
  for (const query of [...new Set([normalized, roadOnly].filter(Boolean))]) {
    const url = new URL("https://nominatim.openstreetmap.org/search");
    url.searchParams.set("q", query);
    url.searchParams.set("format", "json");
    url.searchParams.set("limit", "1");
    url.searchParams.set("countrycodes", "kr");
    try {
      const response = await fetch(url, { headers:{"User-Agent":"INJOY-local-data-import/1.0"} });
      const [result] = response.ok ? await response.json() : [];
      if (result) { cache[address] = [Number(result.lat), Number(result.lon)]; break; }
    } catch {}
    await sleep(1100);
  }
  return cache[address] || null;
}

const unique = new Map();
for (const entry of entries) {
  const address = findAddress(entry.details);
  const key = `${entry.name}|${address}`;
  if (!unique.has(key)) unique.set(key, {...entry, address});
}
const places = [];
for (const entry of unique.values()) {
  let coords = await geocode(entry.address);
  const district = districtOf(entry.address);
  if (!coords && entry.name.includes("수인분당선")) coords = [37.4077,126.6952];
  if (!coords) coords = fallbackCenters[district] || [37.4563,126.7052];
  const phone = findPhone(entry.details);
  const hours = findHours(entry.details) || "운영시간은 전화로 확인해주세요";
  const website = entry.details.find(value => /https?:\/\//.test(value))?.match(/https?:\/\/[^)\]]+/)?.[0] || "";
  const excluded = new Set([entry.details.find(value => stripLabel(value) === entry.address), entry.details.find(value => value.includes(phone)), entry.details.find(value => stripLabel(value) === hours), entry.details.find(value => value.includes(website))]);
  const description = entry.details.filter(value => !excluded.has(value)).map(stripLabel).join(" · ") || `${entry.category} 관련 도움을 받을 수 있는 기관입니다.`;
  places.push({
    id:`place-${places.length + 1}`, name:entry.name, category:entry.category,
    latitude:coords[0], longitude:coords[1], address:entry.address, district,
    phone, hours, description, website, source:"기관 정보 문서"
  });
}

await mkdir(resolve(process.cwd(), "public"), {recursive:true});
await writeFile(outputPath, JSON.stringify(places, null, 2));
await writeFile(cachePath, JSON.stringify(cache, null, 2));
console.log(`Imported ${places.length} places (${Object.keys(cache).length} geocoded addresses)`);
