import GuideDetail from "./GuideDetail";
export default async function Page({params}:{params:Promise<{id:string}>}){const {id}=await params;return <GuideDetail id={id}/>}
