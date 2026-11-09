# Rajasthan ke 7 divisions aur 41 districts - Reel script (Digital Banjaaraa)

Format: 1080x1920, 30fps, about 80-85 s of voiceover (around 215 words at a fast Hinglish pace).
Map data: `data/rajasthan_districts.geojson` (`district`, `division`, `new_2023`, `label` = [lon, lat] for the name) and `data/divisions.geojson`.
Look: satellite base, Rajasthan in blue, white division borders. Each division zooms in and its districts fill in one colour at a time while the name pops up.

| # | Time | Voiceover (Hinglish, Roman letters) | Map / animation | On-screen text |
|---|------|-------------------------------|-----------------|----------------|
| 0 | 0.0-2.5 | "Rajasthan mein kitne district hain? 50? **Galat.**" | Full state glows blue; "50" flashes, then a red cross slams over it | **50?** then **GALAT** (red, shake) |
| 1 | 2.5-8 | "December 2024 mein sarkar ne 9 naye district aur 3 naye sambhag khatam kar diye. Ab hain sirf **41 district** aur **7 sambhag**. Chalo, ek-ek karke dekhte hain." | White division borders draw in; counter runs from 50 down to 41 | **41 DISTRICTS - 7 DIVISIONS** |
| 2 | 8-19 | "Pehla, **Jaipur sambhag**: Jaipur, Dausa, Alwar, Sikar, Jhunjhunu, aur naye Kotputli-Behror aur Khairthal-Tijara. Fact: Jaipur ka walled city UNESCO World Heritage hai." | Zoom to Jaipur division; 7 districts fill in, with the 2 new ones getting a "NEW" tag | **JAIPUR DIVISION (7)** + names; fact strip: "Jaipur walled city = UNESCO World Heritage (2019)" |
| 3 | 19-31 | "**Jodhpur sambhag** sabse bada: Jodhpur, Phalodi, Barmer, Balotra, Jaisalmer, Jalore, Sirohi, Pali. Jaisalmer akela 38 hazaar varg kilometre, Rajasthan ka sabse bada district." | Pan west; 8 districts fill; Jaisalmer pulses | **JODHPUR DIVISION (8)**; fact: "Jaisalmer = 38,401 sq km, sabse bada district" |
| 4 | 31-41 | "**Ajmer sambhag**: Ajmer, Beawar, Bhilwara, Tonk, Nagaur aur Didwana-Kuchaman. Taj Mahal ka marble? Makrana se, jo ab Didwana-Kuchaman mein hai." | Pan to the centre; 6 districts fill; a pin drops on Makrana | **AJMER DIVISION (6)**; fact: "Taj Mahal ka marble = Makrana" |
| 5 | 41-52 | "**Udaipur sambhag**: Udaipur, Salumber, Rajsamand, Chittorgarh, Pratapgarh, Banswara, Dungarpur. Udaipur ko kehte hain City of Lakes." | Pan south; 7 districts fill | **UDAIPUR DIVISION (7)**; fact: "City of Lakes" |
| 6 | 52-59 | "**Kota sambhag**: Kota, Bundi, Baran, Jhalawar. Kota, desh ki coaching capital." | Pan south-east; 4 districts fill | **KOTA DIVISION (4)**; fact: "Coaching capital of India" |
| 7 | 59-67 | "**Bikaner sambhag**: Bikaner, Churu, Sri Ganganagar, Hanumangarh. Bikaner mein hai desh ka National Research Centre on Camel." | Pan north; 4 districts fill; camel icon | **BIKANER DIVISION (4)**; fact: "NRC on Camel - Bikaner" |
| 8 | 67-77 | "Aur last, **Bharatpur sambhag**: Bharatpur, Deeg, Dholpur, Karauli, Sawai Madhopur. Bharatpur ka Keoladeo bird park bhi UNESCO World Heritage hai." | Pan east; 5 districts fill; birds fly over | **BHARATPUR DIVISION (5)**; fact: "Keoladeo NP = UNESCO (1985)" |
| 9 | 77-83 | "Toh total: 7 sambhag, 41 district. **Aapka district kaunsa hai? Comment karo.**" | Zoom out to the full state with every district coloured; names fade in quickly | **7 + 41**; then **Aapka district kaunsa hai? Comment karo** + Digital Banjaaraa handle |

Check: 7 + 8 + 6 + 7 + 4 + 4 + 5 = **41**.

## Notes for edit and VO
- Say "sambhag" in the VO and write "DIVISION" on screen, so both words are covered. You can also swap to "division" in the VO.
- "NEW" tag (optional): Kotputli-Behror, Khairthal-Tijara, Phalodi, Balotra, Beawar, Didwana-Kuchaman, Salumber and Deeg are the 8 districts created in 2023 that were kept in Dec 2024.
- Do not say "50 districts the" as a current fact. The hook only rejects 50 (the count after the 2023 expansion: 33 + 17 districts).
- Jaisalmer is the largest district by area at 38,401 sq km, as per the district list and census figures. Barmer lost area to Balotra, so Jaisalmer stays number 1.
- Some boundaries in the map data are approximate (see the report), so avoid tight close-ups on exact borders of the 8 new districts.
