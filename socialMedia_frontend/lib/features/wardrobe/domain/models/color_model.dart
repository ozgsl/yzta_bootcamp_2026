class SubColor {
  final String id;
  final String name;
  final String hex;

  const SubColor({
    required this.id,
    required this.name,
    required this.hex,
  });
}

class MainColor {
  final String id;
  final String name;
  final String primaryHex;
  final bool isPattern;
  final List<SubColor> subColors;

  const MainColor({
    required this.id,
    required this.name,
    required this.primaryHex,
    this.isPattern = false,
    this.subColors = const [],
  });
}

class SelectedColor {
  final String name;
  final String hexCode;
  final String parentCategoryId;

  const SelectedColor({
    required this.name,
    required this.hexCode,
    required this.parentCategoryId,
  });
}

const List<MainColor> clothingColors = [
  MainColor(
    id: 'siyah',
    name: 'Siyah',
    primaryHex: '#000000',
    subColors: [
      SubColor(id: 'siyah_mat', name: 'Mat Siyah', hex: '#1C1C1C'),
      SubColor(id: 'siyah_parlak', name: 'Parlak Siyah', hex: '#0a0a0a'),
      SubColor(id: 'kuzgun', name: 'Kuzgun Siyah', hex: '#050505'),
    ],
  ),
  MainColor(
    id: 'beyaz',
    name: 'Beyaz',
    primaryHex: '#FFFFFF',
    subColors: [
      SubColor(id: 'beyaz_kar', name: 'Kar Beyazı', hex: '#F9F9F9'),
      SubColor(id: 'beyaz_kirik', name: 'Kırık Beyaz', hex: '#F5F5DC'),
      SubColor(id: 'fildisi', name: 'Fildişi', hex: '#FFFFF0'),
    ],
  ),
  MainColor(
    id: 'gri',
    name: 'Gri',
    primaryHex: '#808080',
    subColors: [
      SubColor(id: 'gri_acik', name: 'Açık Gri', hex: '#D3D3D3'),
      SubColor(id: 'gri_koyu', name: 'Koyu Gri', hex: '#A9A9A9'),
      SubColor(id: 'antrasit', name: 'Antrasit', hex: '#383E42'),
      SubColor(id: 'gumus', name: 'Gümüş', hex: '#C0C0C0'),
    ],
  ),
  MainColor(
    id: 'lacivert',
    name: 'Lacivert',
    primaryHex: '#000080',
    subColors: [
      SubColor(id: 'lacivert_gece', name: 'Gece Mavisi', hex: '#191970'),
      SubColor(id: 'lacivert_koyu', name: 'Koyu Lacivert', hex: '#00008B'),
    ],
  ),
  MainColor(
    id: 'mavi',
    name: 'Mavi',
    primaryHex: '#0000FF',
    subColors: [
      SubColor(id: 'mavi_acik', name: 'Açık Mavi', hex: '#ADD8E6'),
      SubColor(id: 'mavi_gok', name: 'Gök Mavisi', hex: '#87CEEB'),
      SubColor(id: 'mavi_turkuaz', name: 'Turkuaz', hex: '#40E0D0'),
      SubColor(id: 'mavi_kraliyet', name: 'Kraliyet Mavisi', hex: '#4169E1'),
      SubColor(id: 'mavi_bebek', name: 'Bebek Mavisi', hex: '#89CFF0'),
    ],
  ),
  MainColor(
    id: 'kirmizi',
    name: 'Kırmızı',
    primaryHex: '#FF0000',
    subColors: [
      SubColor(id: 'kirmizi_koyu', name: 'Koyu Kırmızı', hex: '#8B0000'),
      SubColor(id: 'kirmizi_ates', name: 'Ateş Kırmızısı', hex: '#FF2400'),
      SubColor(id: 'kirmizi_yakut', name: 'Yakut', hex: '#E0115F'),
    ],
  ),
  MainColor(
    id: 'pembe',
    name: 'Pembe',
    primaryHex: '#FFC0CB',
    subColors: [
      SubColor(id: 'pembe_acik', name: 'Açık Pembe', hex: '#FFB6C1'),
      SubColor(id: 'pembe_fusya', name: 'Fuşya', hex: '#FF00FF'),
      SubColor(id: 'pembe_somon', name: 'Somon', hex: '#FA8072'),
      SubColor(id: 'pembe_pudra', name: 'Pudra', hex: '#FFF0F5'),
    ],
  ),
  MainColor(
    id: 'yesil',
    name: 'Yeşil',
    primaryHex: '#008000',
    subColors: [
      SubColor(id: 'yesil_acik', name: 'Açık Yeşil', hex: '#90EE90'),
      SubColor(id: 'yesil_zeytin', name: 'Zeytin Yeşili', hex: '#808000'),
      SubColor(id: 'yesil_zumrut', name: 'Zümrüt Yeşili', hex: '#50C878'),
      SubColor(id: 'yesil_haki', name: 'Haki', hex: '#C3B091'),
      SubColor(id: 'yesil_nane', name: 'Nane Yeşili', hex: '#98FF98'),
    ],
  ),
  MainColor(
    id: 'sari',
    name: 'Sarı',
    primaryHex: '#FFFF00',
    subColors: [
      SubColor(id: 'sari_acik', name: 'Açık Sarı', hex: '#FFFFE0'),
      SubColor(id: 'sari_hardal', name: 'Hardal', hex: '#FFDB58'),
      SubColor(id: 'sari_limon', name: 'Limon Sarısı', hex: '#FFF44F'),
    ],
  ),
  MainColor(
    id: 'turuncu',
    name: 'Turuncu',
    primaryHex: '#FFA500',
    subColors: [
      SubColor(id: 'turuncu_koyu', name: 'Koyu Turuncu', hex: '#FF8C00'),
      SubColor(id: 'turuncu_mercankosk', name: 'Mercan', hex: '#FF7F50'),
      SubColor(id: 'turuncu_seftali', name: 'Şeftali', hex: '#FFE5B4'),
    ],
  ),
  MainColor(
    id: 'mor',
    name: 'Mor',
    primaryHex: '#800080',
    subColors: [
      SubColor(id: 'mor_lila', name: 'Lila', hex: '#C8A2C8'),
      SubColor(id: 'mor_lavanta', name: 'Lavanta', hex: '#E6E6FA'),
      SubColor(id: 'mor_patlican', name: 'Patlıcan Moru', hex: '#483248'),
      SubColor(id: 'mor_menekse', name: 'Menekşe', hex: '#EE82EE'),
    ],
  ),
  MainColor(
    id: 'kahverengi',
    name: 'Kahverengi',
    primaryHex: '#8B4513',
    subColors: [
      SubColor(id: 'kahverengi_acik', name: 'Açık Kahverengi', hex: '#D2B48C'),
      SubColor(id: 'kahverengi_koyu', name: 'Koyu Kahverengi', hex: '#654321'),
      SubColor(id: 'kahverengi_cikolata', name: 'Çikolata', hex: '#D2691E'),
      SubColor(id: 'kahverengi_toprak', name: 'Toprak', hex: '#CC7722'),
    ],
  ),
  MainColor(
    id: 'bej',
    name: 'Bej / Krem',
    primaryHex: '#F5F5DC',
    subColors: [
      SubColor(id: 'bej_krem', name: 'Krem', hex: '#FFFDD0'),
      SubColor(id: 'bej_vizon', name: 'Vizon', hex: '#8F7E75'),
      SubColor(id: 'bej_kum', name: 'Kum', hex: '#C2B280'),
    ],
  ),
  MainColor(
    id: 'bordo',
    name: 'Bordo',
    primaryHex: '#800000',
    subColors: [
      SubColor(id: 'bordo_sarap', name: 'Şarap Rengi', hex: '#722F37'),
      SubColor(id: 'bordo_koyu', name: 'Koyu Bordo', hex: '#3B0918'),
    ],
  ),
  MainColor(
    id: 'karisik',
    name: 'Desenli / Çok Renkli',
    primaryHex: '#FFFFFF',
    isPattern: true,
  ),
];
