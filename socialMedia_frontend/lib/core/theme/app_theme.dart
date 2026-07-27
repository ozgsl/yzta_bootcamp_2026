import 'package:flutter/material.dart';

class AppTheme {
  // Pastel Disco Vibe Colors (Soft & Harmonized)
  static const Color primaryDark =
      Color(0xFF1E1A29); // Yumuşak koyu pastel mor/gri
  static const Color surfaceDark = Color(0xFF2A233A); // Daha açık yüzey
  static const Color cardDark = Color(0xFF332B47); // Kart arka planı

  // Accents (Keeping for compatibility, but maybe less saturated)
  static const Color accentViolet = Color(0xFFDDB8F7);
  static const Color accentPurple = Color(0xFFCBA1EB);
  static const Color accentPink = Color(0xFFFFB3D9);
  static const Color accentCyan = Color(0xFFA3FFF0);
  static const Color accentGold = Color(0xFFFFEBB3);

  static const Color textPrimary = Color(0xFFEBEBF5); // iOS tarzı yumuşak beyaz
  static const Color textSecondary = Color(0xFF9E99A8); // Soft gray purple
  static const Color textMuted = Color(0xFF736E7D); // Darker gray purple
  static const Color dividerColor = Color(0xFF3E3654); // Subtle border color
  static const Color errorColor = Color(0xFFFF6B6B);
  static const Color successColor = Color(0xFF51CF66);

  // Spacing
  static const double spacingXS = 4.0;
  static const double spacingS = 8.0;
  static const double spacingM = 16.0;
  static const double spacingL = 24.0;
  static const double spacingXL = 32.0;
  static const double spacingXXL = 40.0;

  // Border Radius
  static const double radiusSmall = 8.0;
  static const double radiusMedium = 16.0;
  static const double radiusLarge = 24.0;
  static const double radiusRound = 100.0;

  // Gradients
  static const LinearGradient primaryGradient = LinearGradient(
    colors: [accentViolet, accentPink],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  // Decorations
  static BoxDecoration glassDecoration({double opacity = 0.1}) {
    return BoxDecoration(
      color: Colors.white.withValues(alpha: opacity),
      borderRadius: BorderRadius.circular(radiusMedium),
      border: Border.all(color: Colors.white.withValues(alpha: 0.2)),
    );
  }

  static BoxDecoration gradientButtonDecoration() {
    return BoxDecoration(
      gradient: primaryGradient,
      borderRadius: BorderRadius.circular(radiusRound),
    );
  }

  static ThemeData get darkTheme {
    return ThemeData(
      brightness: Brightness.dark,
      primaryColor: primaryDark,
      scaffoldBackgroundColor: primaryDark,
      fontFamily: 'Inter',
      appBarTheme: const AppBarTheme(
        backgroundColor: primaryDark,
        elevation: 0,
        centerTitle: false,
      ),
      colorScheme: const ColorScheme.dark(
        primary: accentViolet,
        secondary: accentPink,
        surface: surfaceDark,
        error: errorColor,
      ),
      cardTheme: CardThemeData(
        color: cardDark,
        elevation: 8,
        shadowColor: Colors.black.withValues(alpha: 0.3),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      ),
      useMaterial3: true,
    );
  }

  static ThemeData get lightTheme {
    return ThemeData(
      brightness: Brightness.light,
      primaryColor: const Color(0xFFFFFFFF), // Pure white background
      scaffoldBackgroundColor: const Color(0xFFFFFFFF), // Pure white background
      fontFamily: 'Inter',
      appBarTheme: const AppBarTheme(
        backgroundColor: Color(0xFFFFFFFF),
        elevation: 0,
        centerTitle: false,
        iconTheme: IconThemeData(color: Color(0xFF1E1A29)),
        titleTextStyle: TextStyle(
            color: Color(0xFF1E1A29),
            fontSize: 18,
            fontWeight: FontWeight.w600),
      ),
      colorScheme: const ColorScheme.light(
        primary: accentPurple,
        secondary: accentPink,
        surface: Color(0xFFF5E6FB), // Light soft purple for surfaces/cards
        onSurface: Color(0xFF1E1A29), // Black text
        error: errorColor,
      ),
      cardTheme: CardThemeData(
        color: const Color(0xFFF9F1FD), // Very light purple for cards
        elevation: 2,
        shadowColor: const Color(0xFF1E1A29).withValues(alpha: 0.05),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      ),
      useMaterial3: true,
    );
  }
}
