export type GuideItem = { id:string; icon:string; title:string; desc:string; category:string; badge:"생활 팁"|"공식 정보" };
export const guideItems:GuideItem[] = [
  {id:"transit-card",icon:"🚌",title:"대중교통 카드는 어디서 충전하나요?",desc:"편의점이나 지하철역에서 티머니 카드를 충전할 수 있고, 모바일 앱으로도 충전할 수 있어요.",category:"교통",badge:"생활 팁"},
  {id:"bus-booking",icon:"🎫",title:"터미널 가기 전에 미리 예매하기",desc:"시외·고속버스는 고속버스티머니와 버스타고 앱으로 미리 예매할 수 있어요.",category:"교통",badge:"생활 팁"},
  {id:"phone",icon:"📱",title:"외국인도 휴대폰 개통이 가능한가요?",desc:"외국인등록증이 있으면 대리점에서 개통할 수 있고, 발급 전에는 선불 유심을 이용할 수 있어요.",category:"통신",badge:"공식 정보"},
  {id:"bank",icon:"💳",title:"외국인도 은행 계좌를 만들 수 있나요?",desc:"외국인등록증과 여권이 필요하며 은행에 따라 재직증명서 등 추가서류를 요청할 수 있어요.",category:"은행·금융",badge:"공식 정보"},
  {id:"clinic",icon:"🏥",title:"증상에 맞는 병원을 고르세요",desc:"한국 병원은 내과·이비인후과·정형외과·피부과 등으로 세분화되어 있어요.",category:"의료",badge:"생활 팁"},
  {id:"insurance",icon:"🩺",title:"건강보험 가입 상태 확인하기",desc:"6개월 이상 국내에 체류하는 외국인은 건강보험 의무가입 대상이 될 수 있어요.",category:"의료",badge:"공식 정보"},
  {id:"visa",icon:"🏛️",title:"외국인등록증은 언제까지 만들어야 하나요?",desc:"입국일로부터 90일 이내에 관할 출입국·외국인청에서 외국인등록을 해야 해요.",category:"행정·비자",badge:"공식 정보"},
  {id:"address",icon:"📮",title:"주소가 바뀌면 변경 신고가 필요해요",desc:"체류지가 변경되면 주민센터 또는 하이코리아에서 변경 신고를 진행하세요.",category:"행정·비자",badge:"공식 정보"},
  {id:"lease",icon:"🏠",title:"계약 전 등기부등본을 확인하세요",desc:"건물 소유자와 근저당 여부를 확인하고 확정일자를 받아두면 보증금 보호에 도움이 돼요.",category:"주거",badge:"생활 팁"},
  {id:"labor",icon:"💼",title:"임금을 못 받았을 때 도움받는 방법",desc:"고용노동부 또는 외국인노동자 지원센터에 상담·신고할 수 있어요.",category:"직장·노동",badge:"공식 정보"},
  {id:"waste",icon:"♻️",title:"쓰레기 분리배출 이해하기",desc:"종량제 봉투와 재활용 분리배출 요일은 거주지 행정복지센터에서 확인할 수 있어요.",category:"일상생활",badge:"생활 팁"},
  {id:"emergency",icon:"🚨",title:"긴급 연락처를 저장해두세요",desc:"응급·화재는 119, 범죄 신고는 112, 외국인 안내는 1345로 연락하세요.",category:"긴급상황",badge:"공식 정보"},
];
export const categories=["전체","행정·비자","교통","의료","은행·금융","주거","통신","일상생활","직장·노동","긴급상황"];
export const checklistByDuration:Record<string,[string,string,string][]>={
 "1개월 미만":[["transport","대중교통 이용법 익히기","교통"],["phone","휴대폰 개통하기","통신"],["bank","은행 기본 이해하기","은행·금융"],["hospital","병원 이용법 알기","의료"],["waste","쓰레기 분리배출 이해하기","일상생활"],["support","가까운 지원기관 찾기","행정·비자"],["apps","유용한 한국 앱 익히기","일상생활"]],
 "1개월~6개월":[["address","주소 변경 신고 확인하기","행정·비자"],["insurance","건강보험 확인하기","의료"],["contract","근로계약서 확인하기","직장·노동"],["banking","모바일뱅킹 익히기","은행·금융"],["korean","한국어 교육기관 찾기","일상생활"],["lease","임대차 계약 확인하기","주거"],["emergency","긴급 연락처 저장하기","긴급상황"]],
 "6개월~1년":[["visa","체류기간 연장 확인하기","행정·비자"],["tax","세금 기본 알아보기","직장·노동"],["checkup","건강검진 확인하기","의료"],["housing","주거 계약 갱신 확인하기","주거"],["fraud","금융사기 예방 익히기","은행·금융"],["career","직업훈련 알아보기","직장·노동"],["community","지역 커뮤니티 찾기","일상생활"]],
 "1년 이상":[["renewal","장기 체류 갱신 점검하기","행정·비자"],["pension","국민연금 확인하기","직장·노동"],["housing-support","주거지원 알아보기","주거"],["family","가족·자녀 지원 알아보기","일상생활"],["health","정기검진 관리하기","의료"],["finance","신용관리 점검하기","은행·금융"],["participation","지역사회 참여하기","일상생활"]]
};
