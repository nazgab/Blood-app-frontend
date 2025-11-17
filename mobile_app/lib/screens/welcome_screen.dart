import 'package:flutter/material.dart';
import 'dart:math' as math;

class WelcomeScreen extends StatefulWidget {
  const WelcomeScreen({super.key, this.onLogin, this.onRegister});

  final VoidCallback? onLogin;
  final VoidCallback? onRegister;

  static const _red = Color(0xFFD32F2F);
  static const _blue = Color(0xFF1D4ED8);

  @override
  State<WelcomeScreen> createState() => _WelcomeScreenState();
}

class _WelcomeScreenState extends State<WelcomeScreen> {
  String _currentLang = 'RU'; // начальный язык

  void _changeLanguage(String lang) {
    setState(() {
      _currentLang = lang;
    });

    // Здесь вы можете добавить логику смены языка приложения:
    // например, через пакет easy_localization или provider.
    // context.setLocale(Locale(lang.toLowerCase()));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF3F5FA),
      body: SafeArea(
        child: LayoutBuilder(
          builder: (context, vp) {
            final viewportH = vp.maxHeight.isFinite
                ? vp.maxHeight
                : MediaQuery.of(context).size.height;

            return Stack(
              children: [
                // мягкие круги на фоне
                Positioned(right: -120, top: -80, child: _softCircle(260)),
                Positioned(left: -160, bottom: -140, child: _softCircle(340)),

                // основной контент
                Center(
                  child: SingleChildScrollView(
                    padding: const EdgeInsets.all(16),
                    child: ConstrainedBox(
                      constraints: const BoxConstraints(maxWidth: 440),
                      child: Container(
                        padding: const EdgeInsets.fromLTRB(20, 20, 20, 22),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(32),
                          boxShadow: const [
                            BoxShadow(
                              blurRadius: 26,
                              offset: Offset(0, 12),
                              color: Color(0x1A000000),
                            ),
                          ],
                        ),
                        child: _CardContent(
                          blue: WelcomeScreen._blue,
                          red: WelcomeScreen._red,
                          maxImageHeight: math.min(360.0, viewportH * 0.42),
                          onLogin: widget.onLogin,
                          onRegister: widget.onRegister,
                          currentLang: _currentLang,
                          onLangChange: _changeLanguage,
                        ),
                      ),
                    ),
                  ),
                ),
              ],
            );
          },
        ),
      ),
    );
  }

  Widget _softCircle(double size) => Container(
        width: size,
        height: size,
        decoration: const BoxDecoration(
          shape: BoxShape.circle,
          gradient: RadialGradient(
            colors: [Color(0x11A1A8C4), Color(0x00A1A8C4)],
            stops: [0.0, 1.0],
            radius: 0.85,
          ),
        ),
      );
}

class _CardContent extends StatelessWidget {
  const _CardContent({
    required this.blue,
    required this.red,
    required this.maxImageHeight,
    required this.currentLang,
    required this.onLangChange,
    this.onLogin,
    this.onRegister,
  });

  final Color blue;
  final Color red;
  final double maxImageHeight;
  final String currentLang;
  final ValueChanged<String> onLangChange;
  final VoidCallback? onLogin;
  final VoidCallback? onRegister;

  @override
  Widget build(BuildContext context) {
    final isNarrow = MediaQuery.of(context).size.width < 420;

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        // языковые кнопки
        Align(
          alignment: Alignment.centerRight,
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 4),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(30),
              boxShadow: const [
                BoxShadow(
                  color: Color(0x22000000),
                  blurRadius: 8,
                  offset: Offset(0, 2),
                ),
              ],
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                _langChip('KZ', isActive: currentLang == 'KZ'),
                const SizedBox(width: 6),
                _langChip('RU', isActive: currentLang == 'RU'),
              ],
            ),
          ),
        ),
        const SizedBox(height: 16),

        // изображение
        ClipRRect(
          borderRadius: BorderRadius.circular(24),
          child: Container(
            height: maxImageHeight,
            width: double.infinity,
            color: const Color(0xFFF8FAFF),
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
            child: FittedBox(
              fit: BoxFit.contain,
              alignment: Alignment.topCenter,
              child: Image.asset('assets/images/welcome_illustration.png'),
            ),
          ),
        ),
        const SizedBox(height: 20),

        // заголовок
        Text(
          'BLOODSEEKER',
          textAlign: TextAlign.center,
          style: TextStyle(
            fontSize: isNarrow ? 28 : 34,
            fontWeight: FontWeight.w800,
            letterSpacing: 1.0,
            color: blue,
          ),
        ),
        const SizedBox(height: 12),

        // подзаголовок
        const Text(
          'Give life. Donate blood.\nOne step — one life.',
          textAlign: TextAlign.center,
          style: TextStyle(
            fontSize: 16,
            height: 1.35,
            color: Color(0xFF111827),
          ),
        ),
        const SizedBox(height: 24),

        // кнопки входа и регистрации
        Row(
          children: [
            Expanded(
              child: SizedBox(
                height: 52,
                child: ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: red,
                    foregroundColor: Colors.white,
                    elevation: 8,
                    shadowColor: red.withOpacity(0.45),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                  ),
                  onPressed:
                      onLogin ?? () => Navigator.pushNamed(context, '/login'),
                  child: const Text(
                    'Login',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700),
                  ),
                ),
              ),
            ),
            const SizedBox(width: 18),
            Expanded(
              child: SizedBox(
                height: 52,
                child: TextButton(
                  style: TextButton.styleFrom(
                    foregroundColor: Colors.black,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                  ),
                  onPressed: onRegister ??
                      () => Navigator.pushNamed(context, '/register'),
                  child: const Text(
                    'Register',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w700,
                      shadows: [
                        Shadow(
                          blurRadius: 6,
                          offset: Offset(0, 3),
                          color: Color(0x22000000),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _langChip(String text, {bool isActive = false}) {
    return GestureDetector(
      onTap: () => onLangChange(text),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
        decoration: BoxDecoration(
          color: isActive ? const Color(0xFFD32F2F) : Colors.transparent,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: isActive ? const Color(0xFFD32F2F) : Colors.grey.shade400,
          ),
        ),
        child: Text(
          text,
          style: TextStyle(
            color: isActive ? Colors.white : const Color(0xFF111827),
            fontWeight: FontWeight.w700,
            fontSize: 13,
          ),
        ),
      ),
    );
  }
}
