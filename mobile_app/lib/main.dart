import 'package:flutter/material.dart';
import 'dart:math' as math; // можно оставить, если где-то используется

import 'screens/welcome_screen.dart';
import 'screens/login_screen.dart';
import 'screens/register_screen.dart';
import 'screens/forgot_password_screen.dart';
import 'screens/home_screen.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const BloodSeekerApp());
}

class BloodSeekerApp extends StatelessWidget {
  const BloodSeekerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        colorSchemeSeed: const Color(0xFFD32F2F),
        scaffoldBackgroundColor: const Color(0xFFF3F5FA),
        fontFamily: 'Roboto',
      ),
      initialRoute: '/',
      routes: {
        '/': (_) => const WelcomeScreen(), // ✅ теперь берется из screens/welcome_screen.dart
        '/login': (_) => const LoginScreen(),
        '/register': (_) => const RegisterScreen(),
        '/forgot': (_) => const ForgotPasswordScreen(),
        '/home': (_) => const HomeScreen(),
      },
    );
  }
}
