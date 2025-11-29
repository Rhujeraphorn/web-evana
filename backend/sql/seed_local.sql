BEGIN;

-- Ensure base provinces exist
INSERT INTO provinces (slug_en, name_th) VALUES
  ('chiang-mai', 'เชียงใหม่'),
  ('lamphun', 'ลำพูน'),
  ('lampang', 'ลำปาง'),
  ('mae-hong-son', 'แม่ฮ่องสอน')
ON CONFLICT (slug_en) DO NOTHING;

-- Attractions (Chiang Mai focus)
INSERT INTO attractions (
  id, name_th, name_en, kind, lat, lon, province_id,
  source_id, address_th, district_th, subdistrict_th, province_th, detail_th, type_th, region_th
) VALUES
  ('attraction-doi-suthep', 'ดอยสุเทพ', 'Doi Suthep', 'CTA', 18.8040, 98.9215,
    (SELECT id FROM provinces WHERE slug_en = 'chiang-mai'),
    'TAT-001', 'ถนนศรีวิชัย', 'เมืองเชียงใหม่', 'สุเทพ', 'เชียงใหม่',
    'วัดพระธาตุดอยสุเทพ จุดชมวิวเมืองเชียงใหม่', 'ธรรมชาติ', 'เหนือ'),
  ('attraction-ang-khang', 'ขุนช่างเคี่ยน', 'Khun Chang Khian', 'NTA', 18.8639, 98.9032,
    (SELECT id FROM provinces WHERE slug_en = 'chiang-mai'),
    'TAT-002', 'อุทยานแห่งชาติขุนข่าง', 'แม่ริม', 'โป่งแยง', 'เชียงใหม่',
    'ชมดอกพญาเสือโคร่งช่วงหน้าหนาว', 'ธรรมชาติ', 'เหนือ'),
  ('attraction-walking-street', 'ถนนคนเดินท่าแพ', 'Tha Phae Walking Street', 'AVT', 18.7888, 98.9931,
    (SELECT id FROM provinces WHERE slug_en = 'chiang-mai'),
    'TAT-003', 'ท่าแพ', 'เมืองเชียงใหม่', 'ศรีภูมิ', 'เชียงใหม่',
    'ถนนคนเดินสุดคึกคัก ทุกเย็นวันอาทิตย์', 'ชุมชน', 'เหนือ')
ON CONFLICT (id) DO NOTHING;

-- Chargers
INSERT INTO chargers (id, name, type, kw, capacity, lat, lon, province_id, brand, address) VALUES
  ('charger-cnx-airport', 'CNX Airport Charger', 'DC', 120, 4, 18.7697, 98.9740,
    (SELECT id FROM provinces WHERE slug_en = 'chiang-mai'),
    'EA Anywhere', 'สนามบินเชียงใหม่'),
  ('charger-nimman', 'Nimman Fast Charge', 'DC', 60, 2, 18.7995, 98.9673,
    (SELECT id FROM provinces WHERE slug_en = 'chiang-mai'),
    'PEA VOLTA', 'ถนนนิมมานเหมินท์')
ON CONFLICT (id) DO NOTHING;

-- Cafes
INSERT INTO cafes (id, name_th, name_en, lat, lon, province_id, open_hours_json) VALUES
  ('cafe-ristr8to', 'ริสเทรตโต้', 'Ristr8to', 18.7965, 98.9660,
    (SELECT id FROM provinces WHERE slug_en = 'chiang-mai'),
    '{"open": "07:00", "close": "18:00"}'),
  ('cafe-graph', 'กราฟคาเฟ่', 'Graph Cafe', 18.7923, 98.9992,
    (SELECT id FROM provinces WHERE slug_en = 'chiang-mai'),
    '{"open": "08:00", "close": "17:00"}')
ON CONFLICT (id) DO NOTHING;

-- Food
INSERT INTO foods (id, name_th, name_en, price_range, lat, lon, province_id, open_hours_json) VALUES
  ('food-khao-soi-mae-sai', 'ข้าวซอยแม่สาย', 'Khao Soi Mae Sai', '$$', 18.8048, 98.9719,
    (SELECT id FROM provinces WHERE slug_en = 'chiang-mai'),
    '{"open": "08:00", "close": "16:00"}'),
  ('food-huen-phen', 'เฮือนเพ็ญ', 'Huen Phen', '$$', 18.7839, 98.9876,
    (SELECT id FROM provinces WHERE slug_en = 'chiang-mai'),
    '{"open": "10:00", "close": "21:00"}')
ON CONFLICT (id) DO NOTHING;

-- Hotels
INSERT INTO hotels (id, name_th, name_en, stars, phone, address, lat, lon, province_id) VALUES
  ('hotel-udara', 'ยูดารา โฮเทล', 'U Nimman Chiang Mai', 5, '+66-53-222-111', 'นิมมานเหมินท์ ซอย 1', 18.7990, 98.9675,
    (SELECT id FROM provinces WHERE slug_en = 'chiang-mai')),
  ('hotel-yaang', 'โรงแรมยางกู๊ด', 'Yaang Come Village', 4, '+66-53-237-222', 'ถนนลอยเคราะห์', 18.7852, 99.0010,
    (SELECT id FROM provinces WHERE slug_en = 'chiang-mai'))
ON CONFLICT (id) DO NOTHING;

COMMIT;
