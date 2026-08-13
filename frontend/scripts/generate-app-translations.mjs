import {readFile,writeFile} from "node:fs/promises";
import {resolve} from "node:path";

const targets={en:"English",zh:"Chinese (Simplified)",vi:"Vietnamese",ja:"Japanese",th:"Thai",mn:"Mongolian",ru:"Russian",uz:"Uzbek",tl:"Filipino",km:"Khmer",ne:"Nepali"};
const files=["app/MainApp.tsx","app/data.ts"];
const texts=new Set([
  "홈","생활가이드","AI에게 질문","내 주변","마이 라이프","전체","생활 팁","공식 정보",
  "인천 생활을 함께할게요","체류기간","오늘 필요한 정보만 쉽고 빠르게 확인하세요.","당신을 위한 추천",
  "긴 문서가 아니라, 실행 가능한 단계로 정리했어요.","한국 생활에서 막히는 걸 편하게 물어보세요.",
  "무엇이 궁금하세요?","행정·의료·은행·통신처럼 처음엔 놓치기 쉬운 정보도 함께 안내해요.","AI 답변",
  "기준 추천 기관","지도에서 보기","무엇이든 물어보세요...","실제로 도움을 받을 수 있는 곳들.",
  "운영시간은 전화로 확인해주세요","길찾기","완료","개 저장","프로필 수정","나의 체크리스트",
  "한국 생활 시작하기","자세히 보기","저장한 정보","아직 저장한 정보가 없어요.","아직 모를 수 있는 것들",
  "질문·체크리스트 기록을 바탕으로 골랐어요.","왜 중요한가요","한국 생활에서 미리 알아두면 시간과 시행착오를 줄일 수 있는 정보예요.",
  "저장됨","저장하기","체크리스트에서 확인","연수구","남동구","검단구","서해구","영종도구","제물포구","교통","의료","은행·금융","주거","통신","일상생활","직장·노동","행정·비자","긴급상황","행정·복지","생활·편의",
  "답변을 준비하지 못했어요.","연결이 원활하지 않아요. 생활가이드에서 관련 정보를 먼저 확인해주세요."
]);
for(const file of files){const source=await readFile(resolve(process.cwd(),file),"utf8");for(const match of source.matchAll(/["`]([^"`\n]*[가-힣][^"`\n]*)["`]/g)){const value=match[1].replace(/\\n/g," ").trim();if(value.length<140&&!value.includes("${")&&!value.includes("http"))texts.add(value)}}
const places=JSON.parse(await readFile(resolve(process.cwd(),"public/nearby_places.json"),"utf8"));
for(const place of places)for(const key of ["category","district","hours","description"])if(place[key])texts.add(place[key]);
const sourceTexts=[...texts];
let existing={};
try{existing=JSON.parse(await readFile(resolve(process.cwd(),"app/app-translations.json"),"utf8"))}catch{}
const output={...existing,ko:{...(existing.ko||{}),...Object.fromEntries(sourceTexts.map(text=>[text,text]))}};
for(const [code,name] of Object.entries(targets)){
  output[code]={...(existing[code]||{})};
  const missing=sourceTexts.filter(text=>!output[code][text]||output[code][text]===text);
  for(let start=0;start<missing.length;start+=20){
    const batch=missing.slice(start,start+20);
    await Promise.all(batch.map(async text=>{
      const url=new URL("https://translate.googleapis.com/translate_a/single");
      url.searchParams.set("client","gtx");url.searchParams.set("sl","ko");url.searchParams.set("tl",code);url.searchParams.set("dt","t");url.searchParams.set("q",text);
      let translated=text;
      for(let attempt=0;attempt<3;attempt++){
        try{const response=await fetch(url);if(!response.ok)continue;const data=await response.json();translated=(data[0]||[]).map(part=>part[0]).join("")||text;break}catch{}
      }
      output[code][text]=translated;
    }));
  }
  console.log(`${code}: ${missing.length} added (${sourceTexts.length} total)`);
}
await writeFile(resolve(process.cwd(),"app/app-translations.json"),JSON.stringify(output,null,2));
