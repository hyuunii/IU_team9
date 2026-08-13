import { readFile, writeFile, mkdir } from "node:fs/promises";
import { basename, resolve } from "node:path";

const sourceRoot = resolve(process.cwd(), "../../데이터/챗봇");
const phoneRoot = resolve(sourceRoot, "전화번호");
const districts = ["검단구", "남동구", "서해구", "연수구", "영종도구", "제물포구"];

function parseCsv(text) {
  const rows = [];
  let row = [], cell = "", quoted = false;
  for (let i = 0; i < text.length; i++) {
    const char = text[i];
    if (char === '"') {
      if (quoted && text[i + 1] === '"') { cell += '"'; i++; }
      else quoted = !quoted;
    } else if (char === "," && !quoted) { row.push(cell.trim()); cell = ""; }
    else if ((char === "\n" || char === "\r") && !quoted) {
      if (char === "\r" && text[i + 1] === "\n") i++;
      row.push(cell.trim()); cell = "";
      if (row.some(Boolean)) rows.push(row);
      row = [];
    } else cell += char;
  }
  if (cell || row.length) { row.push(cell.trim()); rows.push(row); }
  return rows;
}

async function decoded(path, encoding = "utf-8") {
  const bytes = await readFile(path);
  return new TextDecoder(encoding).decode(bytes).replace(/^\uFEFF/, "");
}

function cleanPhone(value = "") { return value.replace(/\s*-\s*/g, "-").trim(); }
function value(row, header, names) {
  const index = names.map(name => header.indexOf(name)).find(i => i >= 0);
  return index === undefined ? "" : (row[index] || "").trim();
}

const contacts = [];
for (const district of districts) {
  const path = resolve(phoneRoot, `${district} 부서별 전화번호.csv`);
  const encoding = ["연수구", "영종도구"].includes(district) ? "euc-kr" : "utf-8";
  const [header, ...rows] = parseCsv(await decoded(path, encoding));
  for (const row of rows) {
    const department = value(row, header, ["담당부서", "부서명", "부서"]);
    const team = value(row, header, ["세부항목", "담당업무", "업무/팀", "팀명", "직위"]);
    const category = value(row, header, ["분야", "구분", "상위조직"]);
    const service = value(row, header, ["민원목록"]);
    const phone = cleanPhone(value(row, header, ["연락처", "전화번호", "대표번호", "대표전화"]));
    if (!department || !phone) continue;
    contacts.push({
      id: `${district}-${contacts.length + 1}`,
      district,
      institution: `${district}청`,
      department,
      team,
      category,
      service,
      phone,
      address: "",
      type: "public-office",
      searchText: [district, department, team, category, service].filter(Boolean).join(" ")
    });
  }
}

const medicalPath = resolve(sourceRoot, "인천광역시_의료기관 현황_20251231.csv");
const [medicalHeader, ...medicalRows] = parseCsv(await decoded(medicalPath, "euc-kr"));
for (const row of medicalRows) {
  const institution = value(row, medicalHeader, ["의료기관명"]);
  const phone = cleanPhone(value(row, medicalHeader, ["연락처"]));
  const address = value(row, medicalHeader, ["소재지"]);
  if (!institution || !phone) continue;
  const sourceDistrict = value(row, medicalHeader, ["군구명"]);
  const addressDistrict = address.match(/(연수구|남동구|서구|중구|동구|미추홀구|부평구|계양구|강화군|옹진군)/)?.[1] || sourceDistrict;
  const specialties = value(row, medicalHeader, ["진료과목"]);
  const hospitalType = value(row, medicalHeader, ["병원종별"]);
  contacts.push({
    id: `medical-${contacts.length + 1}`,
    district: addressDistrict,
    institution,
    department: hospitalType,
    team: specialties,
    category: "의료",
    service: specialties,
    phone,
    address,
    type: "medical",
    searchText: [addressDistrict, institution, hospitalType, specialties, "병원 진료 의료 건강"].filter(Boolean).join(" ")
  });
}

await mkdir(resolve(process.cwd(), "public"), { recursive: true });
await writeFile(resolve(process.cwd(), "public/institution_contacts.json"), JSON.stringify(contacts, null, 2));
console.log(`Imported ${contacts.length} contacts from ${basename(sourceRoot)}`);
