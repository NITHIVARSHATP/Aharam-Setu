import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class AddFoodDonationActivity extends StatefulWidget {
  final String providerId;
  const AddFoodDonationActivity({super.key, required this.providerId});

  @override
  State<AddFoodDonationActivity> createState() => _AddFoodDonationActivityState();
}

class _AddFoodDonationActivityState extends State<AddFoodDonationActivity> {
  final baseUrl = const String.fromEnvironment('BASE_URL', defaultValue: 'http://127.0.0.1:8000');
  final foodType = TextEditingController();
  final quantity = TextEditingController(text: '10');
  final category = TextEditingController(text: 'Cooked Meal');
  final location = TextEditingController(text: 'Chennai');
  bool isVeg = true;

  Future<void> submit() async {
    final now = DateTime.now().toIso8601String();
    final later = DateTime.now().add(const Duration(hours: 2)).toIso8601String();
    final payload = {
      'foodType': foodType.text,
      'quantity': double.tryParse(quantity.text) ?? 0,
      'category': category.text,
      'freshnessTime': later,
      'pickupLocation': location.text,
      'availableFrom': now,
      'availableTo': later,
      'imageUrl': null,
      'isVeg': isVeg,
    };
    final res = await http.post(
      Uri.parse('$baseUrl/provider/donations'),
      headers: {'Content-Type': 'application/json', 'x-user-id': widget.providerId, 'x-role': 'provider'},
      body: jsonEncode(payload),
    );
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(res.statusCode < 300 ? 'Donation posted successfully.' : res.body)));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Add Food Donation')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          TextField(controller: foodType, decoration: const InputDecoration(labelText: 'Food type')),
          TextField(controller: quantity, decoration: const InputDecoration(labelText: 'Quantity (kg)'), keyboardType: TextInputType.number),
          TextField(controller: category, decoration: const InputDecoration(labelText: 'Category')),
          TextField(controller: location, decoration: const InputDecoration(labelText: 'Pickup location')),
          SwitchListTile(value: isVeg, onChanged: (v) => setState(() => isVeg = v), title: const Text('Veg')),
          FilledButton(onPressed: submit, child: const Text('Post Donation')),
        ],
      ),
    );
  }
}
