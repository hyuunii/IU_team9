"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import {languages,LocaleCode,translations} from "./onboarding-i18n";

const regions = ["연수구", "남동구", "검단구", "서해구", "영종도구", "제물포구"];
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

function Choice({ name, value, label, selected, onChange }: { name: string; value: string; label:string; selected: string; onChange: (value: string) => void }) {
  return (
    <label className="choice">
      <input type="radio" name={name} value={value} checked={selected === value} onChange={() => onChange(value)} />
      <span>{label}</span>
    </label>
  );
}

export default function OnboardingPage() {
  const currentYear = new Date().getFullYear();
  const years = useMemo(() => Array.from({ length: 101 }, (_, index) => currentYear - index), [currentYear]);
  const [language, setLanguage] = useState<LocaleCode>("ko");
  const t = translations[language];
  const [nickname, setNickname] = useState("");
  const [birthYear, setBirthYear] = useState(currentYear - 25);
  const [region, setRegion] = useState(regions[0]);
  const [duration, setDuration] = useState(durations[0]);
  const [hasArc, setHasArc] = useState("yes");
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [name, setName] = useState("");
  const [country, setCountry] = useState("");
  const [purpose, setPurpose] = useState(purposes[0]);
  const [phone, setPhone] = useState("");
  const [hasAccount, setHasAccount] = useState("no");
  const [error, setError] = useState("");
  const [started,setStarted]=useState(false);

  useEffect(() => {
    try {
      const previous = JSON.parse(localStorage.getItem("injoy-profile") || "null") as Profile|null;
      const raw = localStorage.getItem("injoy-language") || previous?.language || "ko";
      const legacy:Record<string,LocaleCode>={"한국어":"ko","English":"en"};
      const preferred=(legacy[raw]||raw) as LocaleCode;
      if (languages.some(item=>item.code===preferred)) setLanguage(preferred);
    } catch {}
  }, []);
  useEffect(() => { document.documentElement.lang = language; document.documentElement.dir="ltr"; }, [language]);

  function changeLanguage(value:LocaleCode) {
    setLanguage(value);
    localStorage.setItem("injoy-language", value);
    setError("");
  }

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!nickname.trim()) {
      setError(t.error);
      return;
    }
    const profile: Profile = {
      nickname: nickname.trim(), birthYear, region, duration,
      hasArc: hasArc === "yes", language, name: name.trim(), country: country.trim(),
      purpose, phone: phone.trim(), hasAccount: hasAccount === "yes",
    };
    localStorage.setItem("injoy-profile", JSON.stringify(profile));
    setError("");
    location.href="/home";
  }

  if(!started)return <main className="welcome-shell"><section className="welcome-card"><header><span className="brand"><i>INJOY</i><b>INCHEON</b></span><label className="language-select"><select aria-label={t.languageLabel} value={language} onChange={event=>changeLanguage(event.target.value as LocaleCode)}>{languages.map(item=><option value={item.code} key={item.code}>{item.flag} {item.name}</option>)}</select></label></header><div className="welcome-visual"><div className="map-scene" aria-hidden="true"><span/><span/><span/><i/><i/><i/></div><img src="/characters/smile-cutout-v2.png" alt="INJOY 인천 생활 도우미 캐릭터"/></div><p className="eyebrow">YOUR INCHEON LIFE COMPANION</p><h1>{t.heroTop}<br/><span>{t.heroAccent}</span></h1><p className="welcome-copy">{t.heroBody}</p><button className="primary-button" onClick={()=>setStarted(true)}>{t.submit} <span>→</span></button><small>{t.privacy}</small></section></main>;

  return (
    <main className="shell onboarding-shell">
      <div className="onboarding-glow glow-one"/><div className="onboarding-glow glow-two"/>
      <section className="phone-frame">
      <div className="phone-speaker"/>
      <header className="intro">
        <div className="intro-top">
          <span className="brand"><i>INJOY</i><b>INCHEON</b></span>
          <label className="language-select">
            <span>{t.languageLabel}</span>
            <select aria-label={t.languageLabel} value={language} onChange={event=>changeLanguage(event.target.value as LocaleCode)}>
              {languages.map(item=><option value={item.code} key={item.code}>{item.flag} {item.name}</option>)}
            </select>
          </label>
        </div>
        <div className="intro-copy"><div><p className="intro-kicker">YOUR INCHEON LIFE COMPANION</p><h1>{t.heroTop}<br /><span>{t.heroAccent}</span></h1><p>{t.heroBody}</p></div><img className="onboarding-character" src="/characters/emoji-question.png" alt="궁금해하는 INJOY 캐릭터"/></div>
        <div className="progress"><span /><span /><span /></div>
      </header>

      <form className="form-card" onSubmit={submit}>
        <div className="section-heading">
          <span className="section-number">01</span>
          <div><h2>{t.basic}</h2><p>{t.basicSub}</p></div>
        </div>

        <div className="field-grid two-columns">
          <label className="field"><span>{t.nickname} <b>*</b></span><input value={nickname} onChange={(e) => setNickname(e.target.value)} placeholder={t.nicknamePlaceholder} /></label>
          <label className="field"><span>{t.birthYear} <b>*</b></span><select value={birthYear} onChange={(e) => setBirthYear(Number(e.target.value))}>{years.map((year) => <option key={year} value={year}>{year}{t.yearSuffix}</option>)}</select></label>
          <label className="field"><span>{t.region} <b>*</b></span><select value={region} onChange={(e) => setRegion(e.target.value)}>{regions.map((item,index) => <option key={item} value={item}>{t.regions[index]}</option>)}</select></label>
          <label className="field"><span>{t.duration} <b>*</b></span><select value={duration} onChange={(e) => setDuration(e.target.value)}>{durations.map((item,index) => <option key={item} value={item}>{t.durations[index]}</option>)}</select></label>
        </div>

        <div className="radio-field">
          <span>{t.arc} <b>*</b></span>
          <div className="choices"><Choice name="arc" value="yes" label={t.yes} selected={hasArc} onChange={setHasArc} /><Choice name="arc" value="no" label={t.no} selected={hasArc} onChange={setHasArc} /></div>
        </div>

        <button className="details-trigger" type="button" aria-expanded={detailsOpen} onClick={() => setDetailsOpen(!detailsOpen)}>
          <span><b>{t.optional}</b><small>{t.optionalSub}</small></span><i className={detailsOpen ? "open" : ""} />
        </button>

        {detailsOpen && (
          <section className="optional-fields">
            <div className="field-grid two-columns">
              <label className="field"><span>{t.name}</span><input value={name} onChange={(e) => setName(e.target.value)} placeholder={t.optionalInput} /></label>
              <label className="field"><span>{t.country}</span><input value={country} onChange={(e) => setCountry(e.target.value)} placeholder={t.countryPlaceholder} /></label>
              <label className="field"><span>{t.purpose}</span><select value={purpose} onChange={(e) => setPurpose(e.target.value)}>{purposes.map((item,index) => <option key={item} value={item}>{t.purposes[index]}</option>)}</select></label>
              <label className="field"><span>{t.phone}</span><input value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="010-0000-0000" /></label>
            </div>
            <div className="radio-field compact"><span>{t.account}</span><div className="choices"><Choice name="account" value="yes" label={t.yes} selected={hasAccount} onChange={setHasAccount} /><Choice name="account" value="no" label={t.no} selected={hasAccount} onChange={setHasAccount} /></div></div>
          </section>
        )}

        {error && <p className="error" role="alert">{error}</p>}
        <button className="primary-button" type="submit">{t.submit} <span>→</span></button>
        <p className="privacy">{t.privacy}</p>
      </form>
      <div className="onboarding-leaves" aria-hidden="true"><i>●</i><i>●</i><i>●</i></div>
      </section>
    </main>
  );
}
