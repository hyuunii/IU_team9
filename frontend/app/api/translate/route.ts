const supported=new Set(["en","zh","vi","ja","th","mn","ru","uz","tl","km","ne"]);

async function translate(text:string,locale:string){
 if(!text||locale==="ko"||!supported.has(locale))return text;
 try{
  const safe=text.replace(/인천/g,"INJOY_INCHEON");
  const url=new URL("https://translate.googleapis.com/translate_a/single");
  url.searchParams.set("client","gtx");url.searchParams.set("sl","ko");url.searchParams.set("tl",locale);url.searchParams.set("dt","t");url.searchParams.set("q",safe);
  const response=await fetch(url);if(!response.ok)return text;
  const data=await response.json();
  return ((data[0]||[]).map((part:string[])=>part[0]).join("")||text).replace(/INJOY_INCHEON/gi,"Incheon").replace(/Seoul/gi,"Incheon");
 }catch{return text}
}

export async function POST(request:Request){
 const {texts,locale}=await request.json() as {texts?:string[];locale?:string};
 if(!Array.isArray(texts)||!locale)return Response.json({translations:texts||[]});
 const unique=[...new Set(texts)].slice(0,100);
 const values=await Promise.all(unique.map(text=>translate(text,locale)));
 const result=Object.fromEntries(unique.map((text,index)=>[text,values[index]]));
 return Response.json({translations:texts.map(text=>result[text]||text)});
}
