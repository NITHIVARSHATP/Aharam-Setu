import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class DonationTrackingActivity extends StatefulWidget {
  final String providerId;
  const DonationTrackingActivity({super.key, required this.providerId});

  @override
  State<DonationTrackingActivity> createState() => _DonationTrackingActivityState();
}

class _DonationTrackingActivityState extends State<DonationTrackingActivity> {
  final baseUrl = const String.fromEnvironment('BASE_URL', defaultValue: 'http://127.0.0.1:8000');
  List<dynamic> donations = [];

  @override
  void initState() {
    super.initState();
    load();
  }

  Future<void> load() async {
    final res = await http.get(
      Uri.parse('$baseUrl/provider/donations/me'),
      headers: {'x-user-id': widget.providerId, 'x-role': 'provider'},
    );
    setState(() => donations = jsonDecode(res.body) as List<dynamic>);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Donation Tracking')),
      body: RefreshIndicator(
        onRefresh: load,
        child: ListView(
          padding: const EdgeInsets.all(12),
          children: donations
              .map((d) => Card(
                    child: ListTile(
                      title: Text(d['foodType'] ?? ''),
                      subtitle: Text('Status: ${d['status']}'),
                    ),
                  ))
              .toList(),
        ),
      ),
    );
  }
}
