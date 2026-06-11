// Character name → image filename mapping
const characterMap = {
  "AKUMA": "gouki",
  "GOUKI": "gouki",
  "DEE JAY": "deejay",
  "E. HONDA": "honda",
  "A.K.I.": "aki",
  "M. BISON": "vega",
  "C. VIPER": "cviper",
};

export const toImageName = (charName) => {
  const cleaned = charName.toUpperCase().trim();
  if (characterMap[cleaned]) return characterMap[cleaned];
  return cleaned.toLowerCase().replace(/[^a-z0-9]/g, "");
};

export const characterImageURL = (name) => {
  const img = toImageName(name);
  return `https://www.streetfighter.com/6/buckler/assets/images/material/character/character_${img}_l.png`;
};

// MR → Rank Icon (for Master rank players)
export const getRankIcon = (mr) => {
  if (mr >= 1800)
    return "https://www.streetfighter.com/6/buckler/assets/images/material/rank/rank42_s.png";
  if (mr >= 1700)
    return "https://www.streetfighter.com/6/buckler/assets/images/material/rank/rank41_s.png";
  if (mr >= 1600)
    return "https://www.streetfighter.com/6/buckler/assets/images/material/rank/rank40_s.png";
  return "https://www.streetfighter.com/6/buckler/assets/images/material/rank/rank36_s.png";
};

// LP → Rank Icon (for non-Master rank players)
export const getLPRankIcon = (lp) => {
  if (lp >= 23800) return "https://www.streetfighter.com/6/buckler/assets/images/material/rank/rank35_s.png";
  if (lp >= 22600) return "https://www.streetfighter.com/6/buckler/assets/images/material/rank/rank34_s.png";
  if (lp >= 21400) return "https://www.streetfighter.com/6/buckler/assets/images/material/rank/rank33_s.png";
  if (lp >= 20200) return "https://www.streetfighter.com/6/buckler/assets/images/material/rank/rank32_s.png";
  if (lp >= 19000) return "https://www.streetfighter.com/6/buckler/assets/images/material/rank/rank31_s.png";
  if (lp >= 17800) return "https://www.streetfighter.com/6/buckler/assets/images/material/rank/rank30_s.png";
  if (lp >= 16600) return "https://www.streetfighter.com/6/buckler/assets/images/material/rank/rank29_s.png";
  if (lp >= 15400) return "https://www.streetfighter.com/6/buckler/assets/images/material/rank/rank28_s.png";
  if (lp >= 14200) return "https://www.streetfighter.com/6/buckler/assets/images/material/rank/rank27_s.png";
  if (lp >= 13000) return "https://www.streetfighter.com/6/buckler/assets/images/material/rank/rank26_s.png";
  if (lp >= 12200) return "https://www.streetfighter.com/6/buckler/assets/images/material/rank/rank25_s.png";
  if (lp >= 11400) return "https://www.streetfighter.com/6/buckler/assets/images/material/rank/rank24_s.png";
  if (lp >= 10600) return "https://www.streetfighter.com/6/buckler/assets/images/material/rank/rank23_s.png";
  if (lp >= 9800) return "https://www.streetfighter.com/6/buckler/assets/images/material/rank/rank22_s.png";
  if (lp >= 9000) return "https://www.streetfighter.com/6/buckler/assets/images/material/rank/rank21_s.png";
  if (lp >= 8200) return "https://www.streetfighter.com/6/buckler/assets/images/material/rank/rank20_s.png";
  if (lp >= 7400) return "https://www.streetfighter.com/6/buckler/assets/images/material/rank/rank19_s.png";
  if (lp >= 6600) return "https://www.streetfighter.com/6/buckler/assets/images/material/rank/rank18_s.png";
  if (lp >= 5800) return "https://www.streetfighter.com/6/buckler/assets/images/material/rank/rank17_s.png";
  if (lp >= 5000) return "https://www.streetfighter.com/6/buckler/assets/images/material/rank/rank16_s.png";
  if (lp >= 4600) return "https://www.streetfighter.com/6/buckler/assets/images/material/rank/rank15_s.png";
  if (lp >= 4200) return "https://www.streetfighter.com/6/buckler/assets/images/material/rank/rank14_s.png";
  if (lp >= 3800) return "https://www.streetfighter.com/6/buckler/assets/images/material/rank/rank13_s.png";
  if (lp >= 3400) return "https://www.streetfighter.com/6/buckler/assets/images/material/rank/rank12_s.png";
  if (lp >= 3000) return "https://www.streetfighter.com/6/buckler/assets/images/material/rank/rank11_s.png";
  if (lp >= 2600) return "https://www.streetfighter.com/6/buckler/assets/images/material/rank/rank10_s.png";
  if (lp >= 2200) return "https://www.streetfighter.com/6/buckler/assets/images/material/rank/rank9_s.png";
  if (lp >= 1800) return "https://www.streetfighter.com/6/buckler/assets/images/material/rank/rank8_s.png";
  if (lp >= 1400) return "https://www.streetfighter.com/6/buckler/assets/images/material/rank/rank7_s.png";
  if (lp >= 1000) return "https://www.streetfighter.com/6/buckler/assets/images/material/rank/rank6_s.png";
  if (lp >= 800) return "https://www.streetfighter.com/6/buckler/assets/images/material/rank/rank5_s.png";
  if (lp >= 600) return "https://www.streetfighter.com/6/buckler/assets/images/material/rank/rank4_s.png";
  if (lp >= 400) return "https://www.streetfighter.com/6/buckler/assets/images/material/rank/rank3_s.png";
  return "https://www.streetfighter.com/6/buckler/assets/images/material/rank/rank3_s.png";
};

export const formatLastUpdated = (isoTimestamp) => {
  const date = new Date(isoTimestamp);
  const options = {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    timeZoneName: 'short'
  };
  return `Last updated: ${date.toLocaleString('en-US', options)}`;
};
