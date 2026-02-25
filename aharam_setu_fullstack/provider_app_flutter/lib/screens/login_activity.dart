import 'package:flutter/material.dart';
import 'provider_dashboard.dart';

class LoginActivity extends StatelessWidget {
  const LoginActivity({super.key});

  @override
  Widget build(BuildContext context) {
    final emailController = TextEditingController();
    return Scaffold(
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Text('Aharam Setu', style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold)),
            const Text('Every meal shared saves a life.'),
            const SizedBox(height: 24),
            TextField(controller: emailController, decoration: const InputDecoration(labelText: 'Email')),
            const SizedBox(height: 12),
            FilledButton(
              onPressed: () {
                Navigator.pushReplacement(
                  context,
                  MaterialPageRoute(builder: (_) => ProviderDashboard(providerId: 'usr_1')),
                );
              },
              child: const Text('Login / Register as Provider'),
            ),
          ],
        ),
      ),
    );
  }
}
