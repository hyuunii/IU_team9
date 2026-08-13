"use client";
import {useEffect,useState} from "react";
import Link from "next/link";
import {guideItems} from "../../data";

const details:Record<string,{why:string;steps:string[];service:string;caution:string;official:string}>={
 "transit-card":{why:"인천 i-패스는 K-패스를 기반으로 인천시민의 대중교통비 일부를 돌려주는 제도예요. 인천에 주소를 둔 19세 이상 주민은 외국인등록번호로 주소지 검증을 완료한 경우에도 이용할 수 있어요.",steps:["카드사에서 선불형 또는 후불형 K-패스 카드를 신청해 수령하세요.","K-패스 앱이나 누리집에서 카드번호를 등록하고 회원가입하세요.","주민등록번호 또는 외국인등록번호를 입력해 인천 주소지 검증을 완료하세요.","등록한 카드로 월 15회 이상 시내·마을·광역버스와 도시철도·GTX를 이용하세요.","일반 20%, 청년 19~39세와 65세 이상 30%, 저소득층 53% 등 본인 조건에 맞는 환급을 확인하세요.","다음 달 카드사 방식에 따라 청구할인·계좌입금·선불카드 충전으로 환급받으세요."],service:"인천 i-패스 제도 문의 032-120 · K-패스 이용·적립금 문의 031-427-4415",caution:"시외·고속버스, KTX·SRT·새마을·무궁화호, 택시 등은 환급 대상이 아니에요. 가입한 첫 달을 제외하고 월 15회 미만 이용하면 환급되지 않으며, 혜택은 중복 지급되지 않고 가장 큰 환급액이 적용돼요.",official:"2026년 2월 4일 기준 인천광역시 공식 안내를 반영했어요. 카드 발급 후 K-패스 앱 또는 korea-pass.kr에서 카드 등록과 주소지 검증을 모두 완료해야 인천 i-패스가 자동 적용됩니다."},
 "bus-booking":{why:"주말과 공휴일에는 버스 좌석이 빠르게 매진될 수 있어요.",steps:["버스타고 또는 티머니GO 앱을 설치하세요.","출발지와 도착지, 날짜를 선택하세요.","좌석을 고르고 결제하세요.","출발 전에 모바일 승차권과 터미널을 확인하세요."],service:"인천종합터미널 안내창구",caution:"예매한 회사와 실제 탑승 터미널을 꼭 확인하세요.",official:"운행시간과 환불 규정은 해당 예매 앱에서 확인하세요."},
 phone:{why:"본인 인증, 은행 앱, 행정 서비스 이용에 한국 전화번호가 자주 필요해요.",steps:["여권과 외국인등록증을 준비하세요.","통신사 대리점에서 요금제를 비교하세요.","약정 기간과 해지 비용을 확인하세요.","등록증 발급 전에는 선불 유심도 고려하세요."],service:"통신사 고객센터 및 가까운 공식 대리점",caution:"명의 대여나 비공식 개통 제안은 피하세요.",official:"요금제와 약정 조건은 통신사 공식 문서로 다시 확인하세요."},
 bank:{why:"급여 수령, 월세 이체와 일상 결제를 위해 계좌가 필요할 수 있어요.",steps:["여권과 외국인등록증을 준비하세요.","재직·재학 또는 거주 증빙을 챙기세요.","가까운 은행 영업점을 방문하세요.","통장, 카드, 모바일뱅킹 신청 여부를 확인하세요."],service:"은행 외국인 고객 상담 및 영업점",caution:"은행과 체류자격에 따라 추가 서류를 요구할 수 있어요.",official:"필요 서류와 수수료는 방문 전 해당 은행에 확인하세요."},
 clinic:{why:"한국 병원은 증상에 따라 진료과가 나뉘어 있어 적절한 병원을 고르면 더 빠르게 진료받을 수 있어요.",steps:["신분증과 건강보험 정보를 준비하세요.","증상과 발생 기간, 복용약을 메모하세요.","증상에 맞는 진료과를 선택하세요.","예약 필요 여부와 진료시간을 확인하세요.","영수증과 처방전을 보관하세요."],service:"병원 접수처, 다누리콜센터 1577-1366 통역",caution:"호흡곤란·의식저하 등 응급 증상은 즉시 119에 연락하세요.",official:"건강보험 자격과 비용은 국민건강보험공단에서 확인하세요."},
 insurance:{why:"가입 상태에 따라 병원에서 내는 비용이 크게 달라질 수 있어요.",steps:["외국인등록번호와 체류자격을 확인하세요.","건강보험 가입 여부를 조회하세요.","보험료와 납부 상태를 확인하세요.","변경 사항이 있다면 공단에 신고하세요."],service:"국민건강보험공단 1577-1000",caution:"체류자격과 체류기간에 따라 적용 기준이 달라요.",official:"최신 자격 기준은 국민건강보험공단에서 확인하세요."},
 visa:{why:"기한을 넘기면 과태료나 체류상 불이익이 생길 수 있어요.",steps:["입국일과 체류기간 만료일을 확인하세요.","여권, 사진, 체류지 증빙을 준비하세요.","하이코리아에서 방문 예약을 하세요.","관할 출입국·외국인청에서 신청하세요."],service:"외국인종합안내센터 1345",caution:"체류자격마다 요구 서류와 신청 기한이 다릅니다.",official:"최종 서류 목록은 하이코리아 또는 1345에서 확인하세요."},
 address:{why:"체류지 변경 신고를 하지 않으면 과태료가 부과될 수 있어요.",steps:["새 임대차계약서 등 거주 증빙을 준비하세요.","전입한 날을 확인하세요.","주민센터 또는 하이코리아에서 신고하세요.","처리 결과를 확인해 보관하세요."],service:"거주지 행정복지센터 또는 1345",caution:"신고 기한을 놓치지 않도록 이사 직후 처리하세요.",official:"체류지 변경 기준은 하이코리아에서 확인하세요."},
 lease:{why:"계약 전 권리관계를 확인하면 보증금 피해 위험을 줄일 수 있어요.",steps:["등기부등본에서 소유자를 확인하세요.","근저당과 압류 여부를 살펴보세요.","계약 상대방의 신분을 확인하세요.","계약 후 전입신고와 확정일자를 받으세요."],service:"주택임대차 상담 또는 가까운 공인중개사",caution:"보증금을 개인 명의의 다른 계좌로 보내지 마세요.",official:"등기 정보와 임대차 보호제도는 정부24·대법원 인터넷등기소에서 확인하세요."},
 labor:{why:"임금 문제는 근무 기록과 계약서를 갖추면 상담과 신고가 수월해요.",steps:["근로계약서와 급여명세서를 모으세요.","출퇴근·근무시간 기록을 정리하세요.","사업주에게 지급 일정을 확인하세요.","해결되지 않으면 노동기관에 상담하세요."],service:"고용노동부 1350 또는 외국인노동자 지원센터",caution:"확인하지 않은 합의서나 사직서에 서명하지 마세요.",official:"신고 절차는 고용노동부 공식 안내에서 확인하세요."},
 waste:{why:"지역별 배출 요일과 방법이 달라 과태료를 예방하려면 기준을 확인해야 해요.",steps:["일반쓰레기는 종량제 봉투에 담으세요.","재활용품은 종류별로 분리하세요.","음식물쓰레기는 전용 용기를 사용하세요.","거주지의 배출 요일과 장소를 확인하세요."],service:"거주지 구청 청소 담당 부서 또는 행정복지센터",caution:"대형폐기물은 스티커나 온라인 신고 없이 버리면 안 돼요.",official:"정확한 배출 기준은 거주지 구청 홈페이지에서 확인하세요."},
 emergency:{why:"긴급 상황에서는 정확한 번호로 빠르게 신고하는 것이 중요해요.",steps:["응급·화재는 119에 전화하세요.","범죄·위험 상황은 112에 신고하세요.","현재 위치와 상황을 짧고 정확하게 말하세요.","통화가 어렵다면 주변 사람에게 도움을 요청하세요."],service:"119 응급·화재, 112 경찰, 1345 외국인 안내",caution:"생명이나 안전이 위험하면 일반 상담보다 긴급번호를 먼저 이용하세요.",official:"긴급기관 안내에 따라 안전한 장소에서 기다리세요."}
};

export default function GuideDetail({id}:{id:string}){
 const item=guideItems.find(value=>value.id===id);const info=details[id];
 const [saved,setSaved]=useState(false);
 useEffect(()=>{try{setSaved(JSON.parse(localStorage.getItem("injoy-saved")||"[]").includes(id))}catch{}},[id]);
 function toggle(){const list:string[]=JSON.parse(localStorage.getItem("injoy-saved")||"[]");const next=list.includes(id)?list.filter(value=>value!==id):[...list,id];localStorage.setItem("injoy-saved",JSON.stringify(next));setSaved(next.includes(id))}
 if(!item||!info)return <main className="guide-detail-shell"><p>해당 생활가이드 정보를 찾을 수 없어요.</p><Link href="/guide">생활가이드로 돌아가기</Link></main>;
 const sameCategory=guideItems.filter(value=>value.id!==id&&value.category===item.category);
 const fallbackRelated=guideItems.filter(value=>value.id!==id&&value.category!==item.category);
 const related=[...sameCategory,...fallbackRelated].slice(0,2);
 return <main className="guide-detail-shell"><header className="detail-top"><Link href="/guide">‹ 생활가이드</Link><span>INJOY · GUIDE</span></header><article className="guide-detail">
  <section className="detail-hero"><div className="detail-meta"><span className="detail-main-icon">{item.icon}</span><em>{item.badge}</em></div><h1>{item.title}</h1><p>{item.desc}</p><div className="detail-actions"><button onClick={toggle}>{saved?"✓ 저장됨":"♡ 저장"}</button><Link href={`/ask?question=${encodeURIComponent(item.title)}`}>◉ AI에게 질문</Link><Link href="/nearby">⌖ 가까운 도움처</Link></div></section>
  <section className="detail-block"><h2>왜 중요한가요</h2><p>{info.why}</p></section>
  <section className="detail-block steps-block"><h2>이렇게 하면 돼요</h2><ol>{info.steps.map((step,index)=><li key={step}><span>{index+1}</span><p>{step}</p></li>)}</ol></section>
  <section className="detail-callout service"><h2>도움이 되는 서비스</h2><p>{info.service}</p></section>
  <section className="detail-callout caution"><h2>△ 주의할 점</h2><p>{info.caution}</p></section>
  <section className="detail-callout official"><h2>▤ 공식 정보 확인</h2><p>{info.official}</p></section>
  <section className="related-section"><h2>관련 정보</h2><p>이것도 알아두면 좋아요</p>{related.map(value=><Link href={`/guide/${value.id}`} key={value.id}><span>{value.icon}</span><div><b>{value.title}</b><small>{value.desc}</small></div><i>›</i></Link>)}</section>
 </article><nav className="bottom-nav detail-bottom-nav"><Link href="/home"><span>⌂</span>홈</Link><Link className="active" href="/guide"><span>▤</span>생활가이드</Link><Link href="/ask"><span>?</span>AI에게 질문</Link><Link href="/nearby"><span>⌖</span>내 주변</Link><Link href="/my"><span>♙</span>마이 라이프</Link></nav></main>
}
