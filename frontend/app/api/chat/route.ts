import faq from "../../../public/faq.json";
import contacts from "../../../public/institution_contacts.json";

type Faq = { question:string; answer:string; category:string };
type Contact = {
  id:string; district:string; institution:string; department:string; team:string;
  category:string; service:string; phone:string; address:string;
  type:"public-office"|"medical"; searchText:string;
};
const localeCodes=new Set(["en","zh","vi","ja","th","mn","ru","uz","tl","km","ne"]);
async function translateAnswer(text:string,locale?:string){if(!locale||!localeCodes.has(locale))return text;try{const protectedText=text.replace(/인천/g,"INJOY_INCHEON");const url=new URL("https://translate.googleapis.com/translate_a/single");url.searchParams.set("client","gtx");url.searchParams.set("sl","ko");url.searchParams.set("tl",locale);url.searchParams.set("dt","t");url.searchParams.set("q",protectedText);const response=await fetch(url);if(!response.ok)return text;const data=await response.json();return ((data[0]||[]).map((part:string[])=>part[0]).join("")||text).replace(/INJOY_INCHEON/gi,"Incheon").replace(/Seoul/gi,"Incheon")}catch{return text}}

const STOP_WORDS = new Set(["어디", "어떻게", "하나요", "해야", "문의", "전화", "알려", "주세요", "관련", "내용", "있나요", "싶어요"]);
const INTENTS:[RegExp,string[]][] = [
  [/쓰레기|폐기물|분리배출|재활용|종량제/, ["쓰레기", "폐기물", "재활용", "청소", "자원순환", "환경"]],
  [/주차|주정차|차량|자동차/, ["교통", "주차", "자동차", "차량"]],
  [/임금|급여|근로|노동|해고|산재|취업/, ["일자리", "고용", "노동", "근로", "산업", "경제"]],
  [/비자|체류|외국인등록|출입국|국적/, ["외국인", "체류", "등록", "민원", "행정"]],
  [/전입|주소|등본|증명서|주민등록/, ["민원", "전입", "주민", "행정", "총무"]],
  [/복지|생계|기초생활|장애|노인|아동|보육/, ["복지", "생활", "노인", "장애", "아동", "보육"]],
  [/세금|지방세|재산세|자동차세/, ["세무", "세금", "지방세", "재산세"]],
  [/병원|진료|아파|통증|내과|외과|피부|치과|산부인과|정형외과|이비인후과/, ["병원", "의료", "진료", "건강"]],
  [/여권|가족관계|혼인|출생/, ["민원", "여권", "가족", "출생"]],
  [/사업|영업|창업|허가|위생/, ["경제", "기업", "일자리", "위생", "허가"]],
];

function tokens(text:string) {
  return [...new Set(text.toLowerCase().replace(/[^가-힣a-z0-9 ]/g, " ").split(/\s+/).filter(word => word.length > 1 && !STOP_WORDS.has(word)))];
}
function expandedTokens(question:string) {
  const result = tokens(question);
  for (const [pattern, words] of INTENTS) if (pattern.test(question)) result.push(...words);
  return [...new Set(result)];
}
function faqScore(question:string, item:Faq) {
  const haystack = `${item.question} ${item.answer} ${item.category}`.toLowerCase();
  return expandedTokens(question).reduce((score, word) => score + (haystack.includes(word) ? 1 : 0), 0);
}
function compatibleDistricts(region:string) {
  const map:Record<string,string[]> = {
    검단구:["검단구", "서구"], 서해구:["서해구", "서구"],
    영종도구:["영종도구", "중구"], 제물포구:["제물포구", "중구", "동구"],
  };
  return map[region] || [region];
}
function rankContacts(question:string, region:string) {
  const words = expandedTokens(question);
  const medical = /병원|진료|아파|통증|내과|외과|피부|치과|산부인과|정형외과|이비인후과/.test(question);
  const districts = compatibleDistricts(region);
  return (contacts as Contact[]).map(item => {
    const haystack = item.searchText.toLowerCase();
    const match = words.reduce((sum, word) => sum + (haystack.includes(word) ? (word.length >= 3 ? 3 : 2) : 0), 0);
    const district = districts.includes(item.district) ? 12 : 0;
    const type = medical ? (item.type === "medical" ? 8 : -8) : (item.type === "public-office" ? 3 : -6);
    return { item, score:match + district + type, match };
  }).filter(result => result.match > 0 && (medical || result.item.type === "public-office"))
    .sort((a,b) => b.score - a.score || b.match - a.match);
}

export async function POST(request:Request) {
  const { question, profile } = await request.json() as { question?:string; profile?:Record<string,string> };
  if (!question?.trim()) return Response.json({ error:"질문을 입력해주세요." }, { status:400 });
  const region = profile?.region || "인천";
  const rankedFaq = (faq as Faq[]).map(item => ({ item, score:faqScore(question, item) })).sort((a,b) => b.score-a.score);
  const faqContext = rankedFaq.filter(result => result.score >= 2).slice(0,3).map(({item}) => `Q. ${item.question}\nA. ${item.answer}`).join("\n\n");
  const rankedContacts = rankContacts(question, region);
  const recommendation = rankedContacts[0]?.item;
  const contactContext = rankedContacts.slice(0,5).map(({item}) =>
    `${item.institution} / ${item.department}${item.team ? ` / ${item.team}` : ""} / ${item.phone}${item.address ? ` / ${item.address}` : ""}`
  ).join("\n");
  const contact = recommendation ? {
    institution:recommendation.institution, department:recommendation.department,
    team:recommendation.team, phone:recommendation.phone, address:recommendation.address,
    district:recommendation.district, type:recommendation.type,
  } : null;
  const fallbackBase = rankedFaq[0]?.score >= 2 ? rankedFaq[0].item.answer : recommendation
    ? "보유한 인천 기관 데이터를 기준으로 문의할 곳을 찾았어요."
    : "현재 준비된 생활가이드에서 정확한 답을 찾지 못했어요.";
  const fallbackContact = recommendation
    ? `\n\n${region} 기준으로 ${recommendation.institution} ${recommendation.department}${recommendation.team ? `(${recommendation.team})` : ""}에 문의해 보세요. 전화번호는 ${recommendation.phone}입니다.`
    : "\n\n외국인종합안내센터 1345 또는 관련 공식 기관에서 확인해주세요.";
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) return Response.json({ answer:await translateAnswer(fallbackBase + fallbackContact,profile?.locale), source:recommendation ? "FAQ+기관 데이터" : "FAQ", contact });

  const response = await fetch("https://api.openai.com/v1/chat/completions", {
    method:"POST",
    headers:{ "Content-Type":"application/json", Authorization:`Bearer ${apiKey}` },
    body:JSON.stringify({ model:"gpt-4o-mini", temperature:.1, messages:[
      { role:"system", content:`당신은 인천 외국인 주민 생활 안내 도우미입니다. 검증된 FAQ와 기관 후보만 근거로 간결하고 친절하게 답하세요. 사용자가 선택한 언어는 ${profile?.language || "한국어"}이며 반드시 그 언어로 답하세요. 사용자는 ${region} 거주, 체류기간 ${profile?.duration || "미상"}입니다. 기관 후보가 있으면 가장 관련 높은 기관·부서·전화번호를 반드시 답변 마지막에 안내하세요. 이 추천은 사용자의 구 단위 위치 기준이며 정확한 거리순이라고 표현하지 마세요. 불확실한 행정·의료 정보는 공식 기관 재확인을 권하세요.\n\n[FAQ]\n${faqContext || "관련 FAQ 없음"}\n\n[${region} 우선 기관 후보]\n${contactContext || "관련 기관 후보 없음"}` },
      { role:"user", content:question }
    ]})
  });
  if (!response.ok) return Response.json({ answer:await translateAnswer(fallbackBase + fallbackContact,profile?.locale), source:"FAQ+기관 데이터", contact });
  const data = await response.json();
  return Response.json({ answer:data.choices?.[0]?.message?.content || fallbackBase + fallbackContact, source:"AI+FAQ+기관 데이터", contact });
}
