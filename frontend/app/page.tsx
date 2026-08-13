"use client";

import { FormEvent, useMemo, useState } from "react";

const regions = ["연수구", "남동구", "서구", "중구"];
const durations = ["1개월 미만", "1개월~6개월", "6개월~1년", "1년 이상"];
const purposes = ["개인", "가정", "노동자", "유학생", "기타"];

type Profile = {
  nickname: string;
  birthYear: number;
  region: string;
  duration: string;
  hasArc: boolean;
  language: string;
  name: string;
  country: string;
  purpose: string;
  phone: string;
  hasAccount: boolean;
};

function Choice({ name, value, selected, onChange }: { name: string; value: string; selected: string; onChange: (value: string) => void }) {
  return (
    <label className="choice">
      <input type="radio" name={name} value={value} checked={selected === value} onChange={() => onChange(value)} />
      <span>{value}</span>
    </label>
  );
}

export default function OnboardingPage() {
  const currentYear = new Date().getFullYear();
  const years = useMemo(() => Array.from({ length: 101 }, (_, index) => currentYear - index), [currentYear]);
  const [language, setLanguage] = useState("한국어");
  const [nickname, setNickname] = useState("");
  const [birthYear, setBirthYear] = useState(currentYear - 25);
  const [region, setRegion] = useState(regions[0]);
  const [duration, setDuration] = useState(durations[0]);
  const [hasArc, setHasArc] = useState("예");
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [name, setName] = useState("");
  const [country, setCountry] = useState("");
  const [purpose, setPurpose] = useState(purposes[0]);
  const [phone, setPhone] = useState("");
  const [hasAccount, setHasAccount] = useState("아니오");
  const [error, setError] = useState("");
  const [saved, setSaved] = useState<Profile | null>(null);

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!nickname.trim()) {
      setError("닉네임을 입력해주세요.");
      return;
    }
    const profile: Profile = {
      nickname: nickname.trim(), birthYear, region, duration,
      hasArc: hasArc === "예", language, name: name.trim(), country: country.trim(),
      purpose, phone: phone.trim(), hasAccount: hasAccount === "예",
    };
    localStorage.setItem("injoy-profile", JSON.stringify(profile));
    setSaved(profile);
    setError("");
  }

  if (saved) {
    return (
      <main className="shell success-shell">
        <section className="success-card">
          <div className="success-icon">✓</div>
          <p className="eyebrow">준비 완료</p>
          <h1>{saved.nickname}님을 위한<br />인천 생활 안내를 준비했어요</h1>
          <p>{saved.region} · 체류기간 {saved.duration}</p>
          <button className="primary-button" onClick={() => { location.href="/home" }}>홈으로 이동</button>
        </section>
      </main>
    );
  }

  return (
    <main className="shell">
      <header className="intro">
        <div className="intro-top">
          <span className="brand">INJOY · INCHEON</span>
          <div className="language-toggle" aria-label="언어 선택">
            {[
              ["한국어", "KO"], ["English", "EN"],
            ].map(([value, label]) => (
              <button key={value} type="button" className={language === value ? "active" : ""} onClick={() => setLanguage(value)}>{label}</button>
            ))}
          </div>
        </div>
        <h1>인천 생활,<br /><span>함께 시작해요</span></h1>
        <p>몇 가지만 알려주시면 지금 필요한 생활정보를<br className="desktop-break" /> 맞춤으로 준비할게요.</p>
        <div className="progress"><span /><span /><span /></div>
      </header>

      <form className="form-card" onSubmit={submit}>
        <div className="section-heading">
          <span className="section-number">01</span>
          <div><h2>기본 정보</h2><p>맞춤 안내에 꼭 필요한 정보예요.</p></div>
        </div>

        <div className="field-grid two-columns">
          <label className="field"><span>닉네임 <b>*</b></span><input value={nickname} onChange={(e) => setNickname(e.target.value)} placeholder="어떻게 불러드릴까요?" /></label>
          <label className="field"><span>출생연도 <b>*</b></span><select value={birthYear} onChange={(e) => setBirthYear(Number(e.target.value))}>{years.map((year) => <option key={year} value={year}>{year}년</option>)}</select></label>
          <label className="field"><span>거주지역 <b>*</b></span><select value={region} onChange={(e) => setRegion(e.target.value)}>{regions.map((item) => <option key={item}>{item}</option>)}</select></label>
          <label className="field"><span>체류기간 <b>*</b></span><select value={duration} onChange={(e) => setDuration(e.target.value)}>{durations.map((item) => <option key={item}>{item}</option>)}</select></label>
        </div>

        <div className="radio-field">
          <span>외국인등록증을 가지고 있나요? <b>*</b></span>
          <div className="choices"><Choice name="arc" value="예" selected={hasArc} onChange={setHasArc} /><Choice name="arc" value="아니오" selected={hasArc} onChange={setHasArc} /></div>
        </div>

        <button className="details-trigger" type="button" aria-expanded={detailsOpen} onClick={() => setDetailsOpen(!detailsOpen)}>
          <span><b>선택 정보</b><small>몰라도 괜찮아요</small></span><i className={detailsOpen ? "open" : ""} />
        </button>

        {detailsOpen && (
          <section className="optional-fields">
            <div className="field-grid two-columns">
              <label className="field"><span>이름</span><input value={name} onChange={(e) => setName(e.target.value)} placeholder="선택 입력" /></label>
              <label className="field"><span>본국</span><input value={country} onChange={(e) => setCountry(e.target.value)} placeholder="예: 베트남" /></label>
              <label className="field"><span>체류목적</span><select value={purpose} onChange={(e) => setPurpose(e.target.value)}>{purposes.map((item) => <option key={item}>{item}</option>)}</select></label>
              <label className="field"><span>한국 전화번호</span><input value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="010-0000-0000" /></label>
            </div>
            <div className="radio-field compact"><span>한국 계좌가 있나요?</span><div className="choices"><Choice name="account" value="예" selected={hasAccount} onChange={setHasAccount} /><Choice name="account" value="아니오" selected={hasAccount} onChange={setHasAccount} /></div></div>
          </section>
        )}

        {error && <p className="error" role="alert">{error}</p>}
        <button className="primary-button" type="submit">내 맞춤 생활 시작하기 <span>→</span></button>
        <p className="privacy">입력한 정보는 이 기기의 맞춤 안내에만 사용돼요.</p>
      </form>
    </main>
  );
}
