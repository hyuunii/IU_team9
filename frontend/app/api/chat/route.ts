import faq from "../../../public/faq.json";

type Faq={question:string;answer:string;category:string};
function score(question:string,item:Faq){const words=question.replace(/[^가-힣a-zA-Z0-9 ]/g," ").split(/\s+/).filter(w=>w.length>1);return words.reduce((n,w)=>n+(item.question.includes(w)||item.answer.includes(w)||item.category.includes(w)?1:0),0)}
export async function POST(request:Request){
 const {question,profile}=await request.json() as {question?:string;profile?:Record<string,string>};
 if(!question?.trim())return Response.json({error:"질문을 입력해주세요."},{status:400});
 const ranked=(faq as Faq[]).map(item=>({item,score:score(question,item)})).sort((a,b)=>b.score-a.score);
 const context=ranked.filter(x=>x.score>0).slice(0,3).map(x=>`Q. ${x.item.question}\nA. ${x.item.answer}`).join("\n\n");
 const apiKey=process.env.OPENAI_API_KEY;
 if(!apiKey){const answer=ranked[0]?.score>0?ranked[0].item.answer:"현재 준비된 생활가이드에서 정확한 답을 찾지 못했어요. 외국인종합안내센터 1345 또는 관련 공식 기관에서 확인해주세요.";return Response.json({answer,source:ranked[0]?.score>0?"FAQ":"안내"})}
 const response=await fetch("https://api.openai.com/v1/chat/completions",{method:"POST",headers:{"Content-Type":"application/json",Authorization:`Bearer ${apiKey}`},body:JSON.stringify({model:"gpt-4o-mini",temperature:.2,messages:[{role:"system",content:`당신은 인천 외국인 주민 생활 안내 도우미입니다. 다음 검증된 FAQ를 우선 사용하고, 불확실한 행정·의료 정보는 공식 기관 확인을 권하세요. 사용자는 ${profile?.region||"인천"} 거주, 체류기간 ${profile?.duration||"미상"}입니다.\n\n${context}`},{role:"user",content:question}]})});
 if(!response.ok)return Response.json({answer:ranked[0]?.item.answer||"답변을 준비하지 못했어요. 잠시 후 다시 시도해주세요.",source:"FAQ"});
 const data=await response.json();return Response.json({answer:data.choices?.[0]?.message?.content||ranked[0]?.item.answer,source:"AI+FAQ"});
}
