import 'package:flutter/material.dart';
import 'screens/login_activity.dart';

void main() {
  runApp(const AharamSetuProviderApp());
}

class AharamSetuProviderApp extends StatelessWidget {
  const AharamSetuProviderApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Aharam Setu - Provider',
      theme: ThemeData(useMaterial3: true, colorSchemeSeed: const Color(0xFF7A5C2E)),
      home: const LoginActivity(),
    );
  }
}
