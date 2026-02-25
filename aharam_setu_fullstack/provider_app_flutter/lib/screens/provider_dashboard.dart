import 'package:flutter/material.dart';
import 'add_food_donation_activity.dart';
import 'donation_tracking_activity.dart';
import 'impact_screen.dart';

class ProviderDashboard extends StatelessWidget {
  final String providerId;
  const ProviderDashboard({super.key, required this.providerId});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Provider Dashboard')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Card(
            child: ListTile(
              leading: Icon(Icons.favorite),
              title: Text('You are making impact today.'),
              subtitle: Text('Food Rescue • Humanity • Dignity'),
            ),
          ),
          FilledButton(
            onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => AddFoodDonationActivity(providerId: providerId))),
            child: const Text('Add Food Donation'),
          ),
          OutlinedButton(
            onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => DonationTrackingActivity(providerId: providerId))),
            child: const Text('Track Donations'),
          ),
          OutlinedButton(
            onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const ImpactScreen(peopleHelped: 0))),
            child: const Text('View Impact'),
          ),
        ],
      ),
    );
  }
}
