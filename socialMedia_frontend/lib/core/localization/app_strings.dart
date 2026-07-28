/// Spot App — Localization Strings
enum AppLocale { en, tr, de, fr, ja, ko, zh }

class AppStrings {
  final AppLocale locale;
  const AppStrings(this.locale);

  bool get isTr => locale == AppLocale.tr;

  // Helper method for quick translations
  String _t(String en, String tr, String de, String fr, String ja, String ko,
      String zh) {
    switch (locale) {
      case AppLocale.tr:
        return tr;
      case AppLocale.de:
        return de;
      case AppLocale.fr:
        return fr;
      case AppLocale.ja:
        return ja;
      case AppLocale.ko:
        return ko;
      case AppLocale.zh:
        return zh;
      case AppLocale.en:
      default:
        return en;
    }
  }

  // ── General ──────────────────────────────────────────────────
  String get appName => 'Spot';

  // ── Onboarding ───────────────────────────────────────────────
  String get onbWardrobeTitle => _t(
      'Your Digital\nWardrobe',
      'Dijital\nGardırobun',
      'Dein Digitaler\nKleiderschrank',
      'Votre Garde-robe\nNumérique',
      'デジタル\nワードローブ',
      '디지털\n옷장',
      '你的数字\n衣橱');
  String get onbWardrobeSub => _t(
      'Carry your entire closet in your pocket.',
      'Tüm kıyafetlerini cebinde taşı.',
      'Trage deinen gesamten Kleiderschrank in der Tasche.',
      'Transportez tout votre placard dans votre poche.',
      'ポケットの中にクローゼット全体を持ち歩く。',
      '옷장 전체를 주머니에 휴대하세요.',
      '把整个衣橱装进口袋。');
  String get onbARTitle => _t('Virtual\nTry-On', 'Sanal\nDeneme Kabini',
      'Virtuelle\nAnprobe', 'Essai\nVirtuel', 'バーチャル\n試着', '가상\n피팅', '虚拟\n试穿');
  String get onbARSub => _t(
      'Try outfits virtually before you wear them.',
      'Sanal deneme kabinimizle kıyafetleri üstünde gör.',
      'Probiere Outfits virtuell an, bevor du sie trägst.',
      'Essayez virtuellement les tenues avant de les porter.',
      '着る前にバーチャルで試着しよう。',
      '입기 전에 가상으로 옷을 입어보세요.',
      '在穿戴之前虚拟试穿服装。');
  String get onbAITitle => _t(
      'AI Stylist\nAssistant',
      'Yapay Zeka\nStilist Asistanı',
      'KI-Stylist\nAssistent',
      'Assistant\nStyliste IA',
      'AIスタイリスト\nアシスタント',
      'AI 스타일리스트\n어시스턴트',
      'AI造型师\n助手');
  String get onbAISub => _t(
      'Get personalized outfit recommendations.',
      'Kişiselleştirilmiş kombin önerileri al.',
      'Erhalte personalisierte Outfit-Empfehlungen.',
      'Obtenez des recommandations de tenues personnalisées.',
      'パーソナライズされたコーディネートの提案を受け取ろう。',
      '맞춤형 옷차림 추천을 받으세요.',
      '获取个性化的穿搭建议。');
  String get onbSocialTitle => _t(
      'Share with\nthe Community',
      'Toplulukla\nPaylaş',
      'Teilen mit der\nCommunity',
      'Partager avec\nla Communauté',
      'コミュニティと\n共有する',
      '커뮤니티와\n공유하기',
      '与社区\n分享');
  String get onbSocialSub => _t(
      'Showcase your style and discover trends.',
      'Tarzını sergile ve trendleri keşfet.',
      'Zeige deinen Stil und entdecke Trends.',
      'Exposez votre style et découvrez les tendances.',
      '自分のスタイルを披露してトレンドを発見しよう。',
      '자신의 스타일을 뽐내고 트렌드를 발견하세요.',
      '展示你的风格并发现趋势。');

  String get skip =>
      _t('Skip', 'Geç', 'Überspringen', 'Passer', 'スキップ', '건너뛰기', '跳过');
  String get next =>
      _t('Next', 'İleri', 'Weiter', 'Suivant', '次へ', '다음', '下一步');
  String get letsGo => _t("Let's Go", 'Başlayalım', "Los geht's", "Allons-y",
      '行きましょう', '시작하기', '开始吧');

  // ── Auth ─────────────────────────────────────────────────────
  String get welcomeBack => _t('Welcome back', 'Tekrar Hoş Geldin',
      'Willkommen zurück', 'Bon retour', 'お帰りなさい', '환영합니다', '欢迎回来');
  String get signInToSpot => _t(
      'Sign in to Spot',
      "Spot'a Giriş Yap",
      'Bei Spot anmelden',
      'Se connecter à Spot',
      'Spotにサインイン',
      'Spot에 로그인',
      '登录Spot');
  String get emailAddress => _t('Email address', 'E-posta Adresi',
      'E-Mail-Adresse', 'Adresse e-mail', 'メールアドレス', '이메일 주소', '电子邮件');
  String get password => _t(
      'Password', 'Şifre', 'Passwort', 'Mot de passe', 'パスワード', '비밀번호', '密码');
  String get forgotPassword => _t(
      'Forgot password?',
      'Şifremi Unuttum',
      'Passwort vergessen?',
      'Mot de passe oublié?',
      'パスワードを忘れた？',
      '비밀번호를 잊으셨나요?',
      '忘记密码？');
  String get signIn => _t(
      'Sign In', 'Giriş Yap', 'Anmelden', 'Se connecter', 'サインイン', '로그인', '登录');
  String get noAccount => _t("Don't have an account?", 'Hesabın yok mu?',
      'Kein Konto?', 'Pas de compte?', 'アカウントがない？', '계정이 없으신가요?', '没有账户？');
  String get signUp => _t(
      'Sign up', 'Kayıt Ol', 'Registrieren', "S'inscrire", '登録', '가입하기', '注册');
  String get haveAccount => _t(
      'Already have an account?',
      'Zaten hesabın var mı?',
      'Bereits ein Konto?',
      'Déjà un compte?',
      'すでにアカウントをお持ちですか？',
      '이미 계정이 있으신가요?',
      '已有账户？');
  String get createAccount => _t('Create Account', 'Hesap Oluştur',
      'Konto erstellen', 'Créer un compte', 'アカウント作成', '계정 만들기', '创建账户');
  String get joinSpot => _t('Join Spot', "Spot'a Katıl", 'Spot beitreten',
      'Rejoindre Spot', 'Spotに参加', 'Spot 가입', '加入Spot');
  String get username => _t('Username', 'Kullanıcı Adı', 'Benutzername',
      "Nom d'utilisateur", 'ユーザー名', '사용자 이름', '用户名');
  String get register => _t(
      'Register', 'Kayıt Ol', 'Registrieren', "S'inscrire", '登録', '등록', '注册');
  String get pleaseEnterEmail => _t(
      'Please enter your email',
      'Lütfen e-posta adresinizi girin',
      'Bitte E-Mail eingeben',
      'Entrez votre e-mail',
      'メールを入力してください',
      '이메일을 입력하세요',
      '请输入电子邮件');
  String get invalidEmail => _t(
      'Only @gmail.com, @hotmail.com or @outlook.com',
      'Sadece @gmail vb.',
      'Nur @gmail usw.',
      'Seulement @gmail etc.',
      '@gmailなどのみ',
      '@gmail 등만 가능',
      '仅限@gmail等');
  String get pleaseEnterPassword => _t(
      'Please enter your password',
      'Lütfen şifrenizi girin',
      'Bitte Passwort eingeben',
      'Entrez votre mot de passe',
      'パスワードを入力してください',
      '비밀번호를 입력하세요',
      '请输入密码');
  String get loginFailed => _t(
      'Login failed. Please check your credentials.',
      'Giriş yapılamadı, kontrol edin.',
      'Login fehlgeschlagen.',
      'Échec de la connexion.',
      'ログインに失敗しました。',
      '로그인 실패.',
      '登录失败。');

  // ── Main Home ────────────────────────────────────────────────
  String get mainSubtitle => _t(
      'Define your digital style.',
      'Dijital tarzına yön ver.',
      'Definiere deinen digitalen Stil.',
      'Définissez votre style numérique.',
      'デジタルのスタイルを定義する。',
      '디지털 스타일을 정의하세요.',
      '定义你的数字风格。');
  String get wardrobe => _t(
      'Wardrobe', 'Gardırop', 'Garderobe', 'Garde-robe', 'ワードローブ', '옷장', '衣橱');
  String get wardrobeSub => _t('Manage your clothes', 'Kıyafetlerini yönet',
      'Kleidung verwalten', 'Gérer vos vêtements', '服を管理する', '옷 관리', '管理衣服');
  String get aiStylist => _t('AI Stylist', 'AI Stilist', 'KI-Stylist',
      'Styliste IA', 'AIスタイリスト', 'AI 스타일리스트', 'AI造型师');
  String get aiStylistSub => _t('AI powered looks', 'Yapay zeka önerileri',
      'KI-gestützte Looks', 'Looks par IA', 'AI搭載のルック', 'AI 룩', 'AI穿搭');
  String get arMirror => _t('Virtual Try On', 'Sanal Deneme',
      'Virtuelle Anprobe', 'Essai Virtuel', 'バーチャル試着', '가상 피팅', '虚拟试穿');
  String get arMirrorSub => _t(
      'Virtual fitting room',
      'Sanal deneme kabini',
      'Virtuelle Umkleide',
      "Cabine d'essayage virtuelle",
      '仮想試着室',
      '가상 피팅룸',
      '虚拟试衣间');
  String get social =>
      _t('Social', 'Sosyal', 'Sozial', 'Social', 'ソーシャル', '소셜', '社交');
  String get socialSub => _t(
      'Share with community',
      'Toplulukla paylaş',
      'Mit Community teilen',
      'Partager avec la communauté',
      'コミュニティと共有',
      '커뮤니티와 공유',
      '与社区分享');
  String get comingSoon => _t('Coming Soon', 'Yakında', 'Bald verfügbar',
      'Bientôt', '近日公開', '곧 출시', '即将推出');

  // ── Feed ────────────────────────────────────────────────────
  String get feed => _t('Feed', 'Akış', 'Feed', 'Flux', 'フィード', '피드', '动态');
  String get noPostsYet => _t(
      'No posts yet',
      'Henüz gönderi yok',
      'Noch keine Beiträge',
      'Aucune publication',
      '投稿はありません',
      '게시물 없음',
      '暂无内容');
  String get followPeopleHint => _t(
      'Follow people or create the first post!',
      'Birileri takip et veya ilk gönderiyi oluştur!',
      'Leuten folgen oder ersten Beitrag erstellen!',
      'Suivez des gens ou créez!',
      'フォローするか投稿を作成！',
      '사람들을 팔로우하거나 게시물을 만드세요!',
      '关注他人或发布帖子！');
  String get errorLoading => _t(
      'Failed to load',
      'Yükleme başarısız',
      'Laden fehlgeschlagen',
      'Échec du chargement',
      '読み込み失敗',
      '불러오기 실패',
      '加载失败');
  String get retry => _t(
      'Retry', 'Tekrar Dene', 'Wiederholen', 'Réessayer', '再試行', '재시도', '重试');

  // ── Create Post ──────────────────────────────────────────────
  String get newPost => _t('New Post', 'Yeni Paylaşım', 'Neuer Beitrag',
      'Nouveau', '新規投稿', '새 게시물', '新贴');
  String get photo => _t('📸 Photo', '📸 Fotoğraf', '📸 Foto', '📸 Photo',
      '📸 写真', '📸 사진', '📸 照片');
  String get outfitPieces => _t(
      '👗 Outfit Pieces',
      '👗 Kombin Parçaları',
      '👗 Outfit-Teile',
      '👗 Pièces de tenue',
      '👗 衣装パーツ',
      '👗 의상 부품',
      '👗 服装备件');
  String get caption => _t('✏️ Caption', '✏️ Açıklama', '✏️ Beschreibung',
      '✏️ Légende', '✏️ キャプション', '✏️ 캡션', '✏️ 说明');
  String get privacy => _t('🔐 Privacy', '🔐 Gizlilik', '🔐 Privatsphäre',
      '🔐 Confidentialité', '🔐 プライバシー', '🔐 프라이버시', '🔐 隐私');
  String get aiConsent => _t(
      'This image may be used to improve our AI model',
      'Bu görsel, modelin gelişmesi için kullanılabilir',
      'Dieses Bild kann für KI genutzt werden',
      "Image utilisable pour l'IA",
      'この画像はAIのために使用されます',
      '이 이미지는 AI 모델에 사용될 수 있습니다',
      '此图像可用于改善AI模型');
  String get share =>
      _t('Share', 'Paylaş', 'Teilen', 'Partager', '共有', '공유', '分享');
  String get close =>
      _t('Close', 'Kapat', 'Schließen', 'Fermer', '閉じる', '닫기', '关闭');
  String get pickFromGallery => _t(
      'Pick from Gallery',
      'Galeriden Seç',
      'Aus Galerie wählen',
      'Choisir depuis la galerie',
      'ギャラリーから選択',
      '갤러리에서 선택',
      '从相册选择');
  String get pickHint => _t(
      'Pick a photo to share your outfit',
      'Kombinini paylaşmak için fotoğraf seç',
      'Wähle ein Foto deines Outfits',
      'Choisissez une photo de tenue',
      '衣装の写真を共有する',
      '의상 사진을 공유하세요',
      '选择照片分享穿搭');
  String get change =>
      _t('Change', 'Değiştir', 'Ändern', 'Changer', '変更', '변경', '更改');
  String get captionHint => _t(
      'Write something about your outfit...',
      'Kombinin hakkında bir şeyler yaz...',
      'Schreibe etwas über dein Outfit...',
      'Écrivez sur votre tenue...',
      '衣装について何か書いて...',
      '의상에 대해 적어주세요...',
      '写点关于你的穿搭...');
  String get aiSuggest => _t('✨ AI Suggest', '✨ AI Öneri Al', '✨ KI-Vorschlag',
      '✨ Suggestion IA', '✨ AI提案', '✨ AI 제안', '✨ AI建议');
  String get suggesting => _t('Suggesting...', 'Öneri alınıyor...',
      'Vorschlagen...', 'Suggestion...', '提案中...', '제안 중...', '建议中...');
  String get sharedSuccess => _t(
      'Post shared successfully! 🎉',
      'Paylaşım başarıyla oluşturuldu! 🎉',
      'Erfolgreich geteilt! 🎉',
      'Partagé avec succès! 🎉',
      '正常に共有されました！🎉',
      '성공적으로 공유되었습니다! 🎉',
      '分享成功！🎉');

  // ── Profile ──────────────────────────────────────────────────
  String get profile =>
      _t('Profile', 'Profil', 'Profil', 'Profil', 'プロフィール', '프로필', '个人资料');
  String get posts =>
      _t('Posts', 'Gönderi', 'Beiträge', 'Publications', '投稿', '게시물', '帖子');
  String get followers =>
      _t('Followers', 'Takipçi', 'Follower', 'Abonnés', 'フォロワー', '팔로워', '粉丝');
  String get following =>
      _t('Following', 'Takip', 'Folgt', 'Abonnements', 'フォロー中', '팔로잉', '关注');
  String get editProfile => _t('Edit Profile', 'Profili Düzenle',
      'Profil bearbeiten', 'Modifier le profil', 'プロフィール編集', '프로필 편집', '编辑资料');
  String get shareProfile => _t('Share Profile', 'Profili Paylaş',
      'Profil teilen', 'Partager le profil', 'プロフィール共有', '프로필 공유', '分享资料');
  String get logout => _t('Sign Out', 'Çıkış Yap', 'Abmelden', 'Déconnexion',
      'サインアウト', '로그아웃', '登出');

  String get language =>
      _t('Language', 'Dil', 'Sprache', 'Langue', '言語', '언어', '语言');
  String get languageTitle => _t('App Language', 'Uygulama Dili', 'App-Sprache',
      "Langue de l'app", 'アプリの言語', '앱 언어', '应用语言');
  String get english => 'English';
  String get turkish => 'Türkçe';

  String get theme => _t('Appearance', 'Görünüm', 'Erscheinungsbild',
      'Apparence', '外観', '테마', '外观');
  String get lightTheme =>
      _t('Light', 'Açık', 'Hell', 'Clair', 'ライト', '라이트', '浅色');
  String get darkTheme =>
      _t('Dark', 'Koyu', 'Dunkel', 'Sombre', 'ダーク', '다크', '深色');
  String get systemTheme =>
      _t('System', 'Sistem', 'System', 'Système', 'システム', '시스템', '系统');
  String get bodyMeasurements => _t('Body Measurements', 'Vücut Ölçüleri',
      'Körpermaße', 'Mensurations', '身体測定', '신체 치수', '身体测量');
  String get settings => _t(
      'Settings', 'Ayarlar', 'Einstellungen', 'Paramètres', '設定', '설정', '设置');
  
  // ── More Screen ──────────────────────────────────────────────
  String get manageAccount => _t('Manage your account', 'Hesabını yönet', 'Konto verwalten', 'Gérer votre compte', 'アカウントの管理', '계정 관리', '管理您的帐户');
  String get stylePreferences => _t('Style Preferences', 'Stil Tercihleri', 'Stilpräferenzen', 'Préférences de style', 'スタイルの好み', '스타일 기본 설정', '风格偏好');
  String get locationTimezone => _t('Location & Timezone', 'Konum ve Saat Dilimi', 'Standort & Zeitzone', 'Lieu et fuseau horaire', '場所とタイムゾーン', '위치 및 시간대', '位置和时区');
  String get outfitSchedule => _t('Outfit Schedule', 'Kıyafet Planı', 'Outfit-Zeitplan', 'Calendrier des tenues', '衣装のスケジュール', '의상 일정', '服装时间表');
  String get subscription => _t('Subscription', 'Abonelik', 'Abonnement', 'Abonnement', 'サブスクリプション', '구독', '订阅');
  String get termsOfUse => _t('Terms of Use', 'Kullanım Koşulları', 'Nutzungsbedingungen', "Conditions d'utilisation", '利用規約', '이용 약款', '使用条款');
  String get privacyPolicy => _t('Privacy Policy', 'Gizlilik Politikası', 'Datenschutzrichtlinie', 'Politique de confidentialité', 'プライバシーポリシー', '개인정보 처리방침', '隐私政策');
  String get deleteAccount => _t('Delete Account', 'Hesabı Sil', 'Konto löschen', 'Supprimer le compte', 'アカウントを削除', '계정 삭제', '删除帐户');

  // ── Dashboard Greeting ───────────────────────────────────────
  String get goodMorning => _t('Good morning', 'Günaydın', 'Guten Morgen', 'Bonjour', 'おはようございます', '좋은 아침입니다', '早上好');
  String get goodAfternoon => _t('Good afternoon', 'Tünaydın', 'Guten Tag', 'Bon après-midi', 'こんにちは', '좋은 오후입니다', '下午好');
  String get goodEvening => _t('Good evening', 'İyi akşamlar', 'Guten Abend', 'Bonsoir', 'こんばんは', '좋은 저녁입니다', '晚上好');
  String get goodNight => _t('Good night', 'İyi geceler', 'Gute Nacht', 'Bonne nuit', 'おやすみなさい', '안녕히 주무세요', '晚安');
  String get whatToWear => _t('What should we wear today? 🤔', 'Bugün ne giysek? 🤔', 'Was sollen wir heute tragen? 🤔', 'Que devrions-nous porter aujourd\'hui? 🤔', '今日は何を着ようか？ 🤔', '오늘은 무엇을 입을까? 🤔', '今天穿什么？ 🤔');

  // ── Navigation ───────────────────────────────────────────────
  String get navFeed => _t('Feed', 'Akış', 'Feed', 'Flux', 'フィード', '피드', '动态');
  String get navCreate =>
      _t('Create', 'Oluştur', 'Erstellen', 'Créer', '作成', '만들기', '创建');
  String get navProfile =>
      _t('Profile', 'Profil', 'Profil', 'Profil', 'プロフィール', '프로필', '个人资料');
  String get navMore =>
      _t('More', 'Daha Fazla', 'Mehr', 'Plus', 'もっと', '더보기', '更多');
  String get accountSettings =>
      _t('Account Settings', 'Hesap Ayarları', 'Kontoeinstellungen', 'Paramètres du compte', 'アカウント設定', '계정 설정', '帐户设置');

  // ── Comments / Likes / Save ──────────────────────────────────
  String get viewAllComments => _t(
      ' view all comments',
      ' yorumun tümünü gör',
      ' alle Kommentare ansehen',
      ' voir tous les commentaires',
      ' 全てのコメントを見る',
      ' 모든 댓글 보기',
      ' 查看所有评论');
  String get save =>
      _t('Save', 'Kaydet', 'Speichern', 'Enregistrer', '保存', '저장', '保存');
  String get unsave => _t('Unsave', 'Kaydedilenlerden Çıkar', 'Nicht speichern',
      'Ne plus enregistrer', '保存解除', '저장 취소', '取消保存');

  // ── Wardrobe & AI Stylist ────────────────────────────────────
  String get digitalWardrobe => _t(
      'Digital Wardrobe',
      'Dijital Gardırop',
      'Digital Wardrobe',
      'Garde-robe Numérique',
      'デジタルワードローブ',
      '디지털 옷장',
      '数字衣橱');
  String get noClothesFound => _t(
      'No clothes found. Add some!',
      'Henüz kıyafet yok. Biraz ekle!',
      'Keine Kleidung gefunden.',
      'Aucun vêtement.',
      '服が見つかりません。',
      '옷이 없습니다.',
      '没有找到衣服。');
  String get askForSuggestions => _t(
      'Ask for outfit suggestions...',
      'Kombin önerisi iste...',
      'Nach Vorschlägen fragen...',
      'Demander des suggestions...',
      '提案を求める...',
      '의상 추천 요청...',
      '请求建议...');
  String get cannotGenerateResponse => _t(
      'I could not generate a response.',
      'Yanıt oluşturulamadı.',
      'Ich konnte keine Antwort generieren.',
      'Aucune réponse générée.',
      '応答を生成できませんでした。',
      '응답을 생성할 수 없습니다.',
      '无法生成回复。');

  String translateWardrobe(String val) {
    if (isTr) return val;
    final trimmed = val.trim();
    if (trimmed.isEmpty) return val;

    final lower = trimmed.toLowerCase();

    final map = {
      // Types
      'tişör': 'T-Shirt',
      'tişört': 'T-Shirt',
      't-shirt': 'T-Shirt',
      'tshirt': 'T-Shirt',
      'gömlek': 'Shirt',
      'bluz': 'Blouse',
      'kazak': 'Sweater',
      'sweatshirt': 'Sweatshirt',
      'pantolon': 'Pants',
      'jean': 'Jeans',
      'jeans': 'Jeans',
      'şort': 'Shorts',
      'etek': 'Skirt',
      'elbise': 'Dress',
      'ceket': 'Jacket',
      'mont': 'Coat',
      'kaban': 'Overcoat',
      'ayakkabı': 'Shoes',
      'bot': 'Boots',
      'sneaker': 'Sneakers',
      'çanta': 'Bag',
      'aksesuar': 'Accessory',
      'diğer': 'Other',
      'üst giyim': 'Top Wear',
      'alt giyim': 'Bottom Wear',
      'dış giyim': 'Outerwear',

      // Colors
      'siyah': 'Black',
      'beyaz': 'White',
      'gri': 'Grey',
      'lacivert': 'Navy Blue',
      'mavi': 'Blue',
      'açık mavi': 'Light Blue',
      'koyu mavi': 'Dark Blue',
      'kırmızı': 'Red',
      'pembe': 'Pink',
      'açık pembe': 'Light Pink',
      'toz pembe': 'Powder Pink',
      'yeşil': 'Green',
      'açık yeşil': 'Light Green',
      'zeytin yeşili': 'Olive Green',
      'zümrüt yeşili': 'Emerald Green',
      'haki': 'Khaki',
      'nane yeşili': 'Mint Green',
      'sarı': 'Yellow',
      'açık sarı': 'Light Yellow',
      'turuncu': 'Orange',
      'mor': 'Purple',
      'leylak': 'Lilac',
      'eflatun': 'Magenta',
      'kahverengi': 'Brown',
      'açık kahverengi': 'Light Brown',
      'koyu kahverengi': 'Dark Brown',
      'taba': 'Tan',
      'bej': 'Beige',
      'krem': 'Cream',
      'ekru': 'Ecru',
      'bordo': 'Burgundy',
      'karışık': 'Mixed',
      'çok renkli': 'Multicolor',
      'altın': 'Gold',
      'gümüş': 'Silver',
      'bronz': 'Bronze',

      // Seasons
      'yaz': 'Summer',
      'kış': 'Winter',
      'ilkbahar': 'Spring',
      'sonbahar': 'Autumn',
      'tüm sezon': 'All Seasons',
    };

    return map[lower] ?? (trimmed[0].toUpperCase() + trimmed.substring(1));
  }
}
