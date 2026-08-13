import {readFile,writeFile} from "node:fs/promises";
import {resolve} from "node:path";

const root=process.cwd();
const faq=JSON.parse(await readFile(resolve(root,"public/faq.json"),"utf8"));
const env=await readFile(resolve(root,".env.local"),"utf8").catch(()=>"");
const keyLine=env.split(/\r?\n/).find(line=>line.startsWith("OPENAI_API_KEY="));
const apiKey=process.env.OPENAI_API_KEY||keyLine?.slice("OPENAI_API_KEY=".length).replace(/^['"]|['"]$/g,"");
if(!apiKey)throw new Error("OPENAI_API_KEY가 필요합니다.");
const input=faq.map(item=>`${item.category}\n질문: ${item.question}\n답변: ${item.answer}`);
const response=await fetch("https://api.openai.com/v1/embeddings",{method:"POST",headers:{"Content-Type":"application/json",Authorization:`Bearer ${apiKey}`},body:JSON.stringify({model:"text-embedding-3-small",input,dimensions:512})});
if(!response.ok)throw new Error(`임베딩 생성 실패 (${response.status}): ${await response.text()}`);
const data=await response.json();
const output={model:"text-embedding-3-small",dimensions:512,createdAt:new Date().toISOString(),items:faq.map((item,index)=>({id:item.id,embedding:data.data[index].embedding}))};
await writeFile(resolve(root,"public/faq_embeddings.json"),JSON.stringify(output));
console.log(`FAQ ${output.items.length}건 임베딩 저장 완료`);
