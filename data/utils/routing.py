"""
지역(구) 정보를 받아서 담당부서 안내 문구를 만드는 로직.
부서 데이터는 공식 통합 API가 없어서 팀이 직접 조사해 data/dept_routing.json에 하드코딩했다.
"""
import json


def load_dept_routing(path: str = "data/dept_routing.json") -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def get_department_info(region: str, dept_data: dict) -> str | None:
    """지역명을 받아 '이 문의는 OO구 OO과로 연결하세요' 형태의 안내 문구 생성.
    지역이 '미상'이거나 매핑에 없으면 None 반환.
    """
    if region not in dept_data:
        return None

    info = dept_data[region]
    return f"{region} 관련 문의는 {info['부서']}({info.get('전화', '전화번호 확인 필요')})로 연결하시면 됩니다."
