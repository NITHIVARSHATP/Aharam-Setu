import 'package:flutter/material.dart';

class ImpactScreen extends StatelessWidget {
  final int peopleHelped;
  const ImpactScreen({super.key, required this.peopleHelped});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Impact')),
      body: Center(
        child: Card(
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Text('Your food helped $peopleHelped people.\nThank you for your kindness!', textAlign: TextAlign.center, style: const TextStyle(fontSize: 20)),
          ),
        ),
      ),
    );
  }
}
