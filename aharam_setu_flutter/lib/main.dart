import 'package:flutter/material.dart';

import 'api_service.dart';
import 'models.dart';

void main() {
  runApp(const AharamSetuApp());
}

class AharamSetuApp extends StatelessWidget {
  const AharamSetuApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Aharam Setu',
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFFFF9500)),
      ),
      home: const LaunchPage(),
    );
  }
}

class LaunchPage extends StatefulWidget {
  const LaunchPage({super.key});

  @override
  State<LaunchPage> createState() => _LaunchPageState();
}

class _LaunchPageState extends State<LaunchPage> {
  void _openApp() {
    Navigator.of(context).pushReplacement(
      MaterialPageRoute(builder: (_) => const HomePage()),
    );
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    return Scaffold(
      body: Container(
        width: double.infinity,
        padding: const EdgeInsets.symmetric(horizontal: 24),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              colorScheme.primaryContainer,
              colorScheme.surface,
            ],
          ),
        ),
        child: SafeArea(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              BrandLogo(size: 112),
              const SizedBox(height: 20),
              const Text(
                'Aharam Setu',
                style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              const SizedBox(height: 12),
              Text(
                'Smart ML-powered excess food rescue routing',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 15, color: colorScheme.onSurfaceVariant),
              ),
              const SizedBox(height: 32),
              FilledButton.icon(
                onPressed: _openApp,
                icon: const Icon(Icons.arrow_forward_rounded),
                label: const Text('Enter App'),
              ),
              const SizedBox(height: 10),
              Text(
                'Tap to continue',
                style: TextStyle(color: colorScheme.onSurfaceVariant),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    return DefaultTabController(
      length: 3,
      child: Scaffold(
        appBar: AppBar(
          toolbarHeight: 92,
          title: const Row(
            children: [
              BrandLogo(size: 36),
              SizedBox(width: 12),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text('Aharam Setu', style: TextStyle(fontWeight: FontWeight.w700)),
                  Text('Food Rescue Network', style: TextStyle(fontSize: 12)),
                ],
              ),
            ],
          ),
          bottom: TabBar(
            indicatorSize: TabBarIndicatorSize.tab,
            indicator: BoxDecoration(
              color: colorScheme.primaryContainer,
              borderRadius: BorderRadius.circular(12),
            ),
            dividerColor: Colors.transparent,
            labelStyle: const TextStyle(fontWeight: FontWeight.w700),
            tabs: const [
              Tab(icon: Icon(Icons.storefront_outlined), text: 'Provider'),
              Tab(icon: Icon(Icons.volunteer_activism_outlined), text: 'NGO'),
              Tab(icon: Icon(Icons.admin_panel_settings_outlined), text: 'Admin'),
            ],
          ),
        ),
        body: const TabBarView(
          children: [
            ProviderTab(),
            NgoTab(),
            AdminTab(),
          ],
        ),
      ),
    );
  }
}

class BrandLogo extends StatelessWidget {
  final double size;

  const BrandLogo({super.key, this.size = 48});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            colorScheme.primary,
            colorScheme.tertiary,
          ],
        ),
      ),
      alignment: Alignment.center,
      child: Text(
        'AS',
        style: TextStyle(
          color: colorScheme.onPrimary,
          fontWeight: FontWeight.bold,
          fontSize: size * 0.34,
          letterSpacing: 0.6,
        ),
      ),
    );
  }
}

class ProviderTab extends StatefulWidget {
  const ProviderTab({super.key});

  @override
  State<ProviderTab> createState() => _ProviderTabState();
}

class _ProviderTabState extends State<ProviderTab> {
  final ApiService _api = ApiService();
  final _formKey = GlobalKey<FormState>();

  List<ProviderModel> _providers = [];
  List<RescueModel> _rescues = [];
  RankingResponse? _ranking;

  int? _providerId;
  int? _selectedRescueId;
  final TextEditingController _eventType = TextEditingController(text: 'Wedding');
  final TextEditingController _meals = TextEditingController(text: '100');
  final TextEditingController _foodType = TextEditingController(text: 'Mixed Veg Meals');
  final TextEditingController _lat = TextEditingController(text: '13.0827');
  final TextEditingController _lng = TextEditingController(text: '80.2707');

  String _causeTag = 'overestimated_attendance';
  TimeOfDay _readyTime = TimeOfDay.fromDateTime(DateTime.now());
  TimeOfDay _pickupDeadline = TimeOfDay.fromDateTime(DateTime.now().add(const Duration(minutes: 45)));
  TimeOfDay _expiryTime = TimeOfDay.fromDateTime(DateTime.now().add(const Duration(hours: 3)));

  bool _loading = false;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  @override
  void dispose() {
    _eventType.dispose();
    _meals.dispose();
    _foodType.dispose();
    _lat.dispose();
    _lng.dispose();
    super.dispose();
  }

  Future<void> _loadData() async {
    setState(() => _loading = true);
    try {
      final providers = await _api.listProviders();
      final rescues = await _api.listLiveRescues();
      setState(() {
        _providers = providers;
        _rescues = rescues;
        _providerId = providers.isNotEmpty ? (_providerId ?? providers.first.id) : null;
        _selectedRescueId = rescues.isNotEmpty ? (_selectedRescueId ?? rescues.first.id) : null;
      });
    } catch (error) {
      _showError(error);
    } finally {
      setState(() => _loading = false);
    }
  }

  Future<void> _pickTime(ValueSetter<TimeOfDay> onPick, TimeOfDay current) async {
    final selected = await showTimePicker(context: context, initialTime: current);
    if (selected != null) {
      setState(() {
        onPick(selected);
      });
    }
  }

  DateTime _todayWith(TimeOfDay time) {
    final now = DateTime.now();
    return DateTime(now.year, now.month, now.day, time.hour, time.minute);
  }

  Future<void> _createRescue() async {
    if (_providerId == null || !_formKey.currentState!.validate()) {
      return;
    }

    final ready = _todayWith(_readyTime);
    final pickup = _todayWith(_pickupDeadline);
    final expiry = _todayWith(_expiryTime);

    if (!expiry.isAfter(ready)) {
      _showMessage('Expiry time must be after ready time.');
      return;
    }

    final payload = {
      'provider_id': _providerId,
      'meals_available': int.parse(_meals.text.trim()),
      'food_type': _foodType.text.trim(),
      'ready_time': ready.toIso8601String(),
      'pickup_deadline': pickup.toIso8601String(),
      'expiry_time': expiry.toIso8601String(),
      'lat': double.parse(_lat.text.trim()),
      'lng': double.parse(_lng.text.trim()),
      'event_type': _eventType.text.trim(),
      'cause_tag': _causeTag,
    };

    try {
      final result = await _api.createRescue(payload);
      _showMessage('Rescue #${result['rescue_id']} created successfully.');
      await _loadData();
    } catch (error) {
      _showError(error);
    }
  }

  Future<void> _viewRanking() async {
    if (_selectedRescueId == null) {
      return;
    }
    try {
      final ranking = await _api.getRescueRanking(_selectedRescueId!);
      setState(() => _ranking = ranking);
    } catch (error) {
      _showError(error);
    }
  }

  void _showError(Object error) {
    _showMessage(error.toString().replaceFirst('Exception: ', ''));
  }

  void _showMessage(String message) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Center(child: CircularProgressIndicator());
    }

    final totalMeals = _rescues.fold<int>(0, (sum, rescue) => sum + rescue.mealsAvailable);
    return RefreshIndicator(
      onRefresh: _loadData,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _sectionTitle('Create Rescue Request', Icons.edit_note_outlined),
          const SizedBox(height: 10),
          Card(
            elevation: 1.5,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Form(
                key: _formKey,
                child: Column(
                  children: [
                    DropdownButtonFormField<int>(
                      initialValue: _providerId,
                      items: _providers
                          .map((provider) => DropdownMenuItem(value: provider.id, child: Text('${provider.id} - ${provider.name}')))
                          .toList(),
                      onChanged: (value) => setState(() => _providerId = value),
                      decoration: const InputDecoration(labelText: 'Provider'),
                    ),
                    TextFormField(
                      controller: _eventType,
                      decoration: const InputDecoration(labelText: 'Event Type'),
                      validator: _required,
                    ),
                    TextFormField(
                      controller: _meals,
                      keyboardType: TextInputType.number,
                      decoration: const InputDecoration(labelText: 'Meals'),
                      validator: _validatePositiveInt,
                    ),
                    TextFormField(
                      controller: _foodType,
                      decoration: const InputDecoration(labelText: 'Food Type'),
                      validator: _required,
                    ),
                    TextFormField(
                      controller: _lat,
                      keyboardType: const TextInputType.numberWithOptions(decimal: true),
                      decoration: const InputDecoration(labelText: 'Latitude'),
                      validator: _validateDouble,
                    ),
                    TextFormField(
                      controller: _lng,
                      keyboardType: const TextInputType.numberWithOptions(decimal: true),
                      decoration: const InputDecoration(labelText: 'Longitude'),
                      validator: _validateDouble,
                    ),
                    DropdownButtonFormField<String>(
                      initialValue: _causeTag,
                      items: const [
                        DropdownMenuItem(value: 'overestimated_attendance', child: Text('overestimated_attendance')),
                        DropdownMenuItem(value: 'guest_no_show', child: Text('guest_no_show')),
                        DropdownMenuItem(value: 'weather_issue', child: Text('weather_issue')),
                        DropdownMenuItem(value: 'buffer_cooking_policy', child: Text('buffer_cooking_policy')),
                        DropdownMenuItem(value: 'unknown', child: Text('unknown')),
                      ],
                      onChanged: (value) => setState(() => _causeTag = value ?? _causeTag),
                      decoration: const InputDecoration(labelText: 'Cause Tag'),
                    ),
                    const SizedBox(height: 8),
                    _timeTile('Ready Time', _readyTime, (time) => _readyTime = time),
                    _timeTile('Pickup Deadline', _pickupDeadline, (time) => _pickupDeadline = time),
                    _timeTile('Expiry Time', _expiryTime, (time) => _expiryTime = time),
                    const SizedBox(height: 14),
                    FilledButton.icon(
                      onPressed: _createRescue,
                      icon: const Icon(Icons.check_circle_outline),
                      label: const Text('Submit Rescue Request'),
                    ),
                  ],
                ),
              ),
            ),
          ),
          const SizedBox(height: 20),
          _sectionTitle('Live Rescues', Icons.insights_outlined),
          const SizedBox(height: 10),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              _metricCard('Active Rescues', _rescues.length.toString(), Icons.local_fire_department_outlined),
              _metricCard('Total Meals', totalMeals.toString(), Icons.restaurant_menu_outlined),
              _metricCard('NGO Wave 1', '5 notified', Icons.notifications_active_outlined),
            ],
          ),
          const SizedBox(height: 10),
          ..._rescues.map(
            (rescue) => Card(
              child: ListTile(
                title: Text('#${rescue.id} - ${rescue.foodType}'),
                subtitle: Text('${rescue.providerName} • ${rescue.mealsAvailable} meals'),
                trailing: Chip(label: Text(rescue.status.toUpperCase())),
              ),
            ),
          ),
          const SizedBox(height: 8),
          if (_rescues.isNotEmpty)
            DropdownButtonFormField<int>(
              initialValue: _selectedRescueId,
              items: _rescues
                  .map((rescue) => DropdownMenuItem(value: rescue.id, child: Text('#${rescue.id} - ${rescue.foodType}')))
                  .toList(),
              onChanged: (value) => setState(() => _selectedRescueId = value),
              decoration: const InputDecoration(labelText: 'Select Rescue for Ranking'),
            ),
          const SizedBox(height: 8),
          OutlinedButton(onPressed: _rescues.isEmpty ? null : _viewRanking, child: const Text('View NGO Rankings')),
          if (_ranking != null) ...[
            const SizedBox(height: 8),
            Text('Alert Wave ${_ranking!.alertWave} — ${_ranking!.ngosNotified.length} NGOs notified'),
            const SizedBox(height: 8),
            ..._ranking!.ngosNotified.take(10).map(
                  (ngo) => Card(
                    child: ListTile(
                      title: Text(ngo.ngoName),
                      subtitle: Text(
                        '${ngo.distanceKm.toStringAsFixed(1)} km • ${(ngo.acceptanceProbability * 100).toStringAsFixed(0)}% acceptance',
                      ),
                      trailing: Text(ngo.finalScore.toStringAsFixed(3)),
                    ),
                  ),
                ),
          ],
        ],
      ),
    );
  }

  Widget _timeTile(String label, TimeOfDay value, ValueSetter<TimeOfDay> setter) {
    return ListTile(
      contentPadding: EdgeInsets.zero,
      title: Text(label),
      subtitle: Text(value.format(context)),
      trailing: IconButton(
        onPressed: () => _pickTime(setter, value),
        icon: const Icon(Icons.schedule),
      ),
    );
  }
}

class NgoTab extends StatefulWidget {
  const NgoTab({super.key});

  @override
  State<NgoTab> createState() => _NgoTabState();
}

class _NgoTabState extends State<NgoTab> {
  final ApiService _api = ApiService();

  List<NgoJobModel> _jobs = [];
  List<NgoModel> _ngos = [];
  RankingResponse? _ranking;
  int? _selectedRescueId;
  int? _selectedNgoId;
  String _nextStatus = 'accepted';
  bool _loading = false;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() => _loading = true);
    try {
      final ngos = await _api.listNgos();
      setState(() {
        _ngos = ngos;
        _selectedNgoId = ngos.isNotEmpty ? (_selectedNgoId ?? ngos.first.id) : null;
      });
      await _loadJobs();
      await _loadRanking();
    } catch (error) {
      _showError(error);
    } finally {
      setState(() => _loading = false);
    }
  }

  Future<void> _loadJobs() async {
    if (_selectedNgoId == null) {
      setState(() {
        _jobs = [];
        _selectedRescueId = null;
      });
      return;
    }
    final jobs = await _api.listNgoJobs(_selectedNgoId!);
    setState(() {
      _jobs = jobs;
      final jobRescueIds = jobs.map((item) => item.rescueId).toSet();
      if (_selectedRescueId == null || !jobRescueIds.contains(_selectedRescueId)) {
        _selectedRescueId = jobs.isNotEmpty ? jobs.first.rescueId : null;
      }
    });
  }

  Future<void> _loadRanking() async {
    if (_selectedRescueId == null) {
      setState(() => _ranking = null);
      return;
    }
    try {
      final ranking = await _api.getRescueRanking(_selectedRescueId!);
      setState(() => _ranking = ranking);
    } catch (_) {
      setState(() => _ranking = null);
    }
  }

  Future<void> _acceptRescue() async {
    if (_selectedRescueId == null || _selectedNgoId == null) {
      return;
    }
    try {
      final result = await _api.acceptRescue(_selectedRescueId!, _selectedNgoId!);
      _showMessage(result.message);
      await _loadData();
    } catch (error) {
      _showError(error);
    }
  }

  Future<void> _updateStatus() async {
    if (_selectedRescueId == null) {
      return;
    }
    try {
      final result = await _api.updateRescueStatus(_selectedRescueId!, _nextStatus);
      _showMessage('Pickup #${result['rescue_id']} → ${result['status']}');
      await _loadData();
    } catch (error) {
      _showError(error);
    }
  }

  void _showError(Object error) {
    _showMessage(error.toString().replaceFirst('Exception: ', ''));
  }

  void _showMessage(String message) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_jobs.isEmpty) {
      return RefreshIndicator(
        onRefresh: _loadData,
        child: ListView(
          children: const [
            SizedBox(height: 250),
            Center(child: Text('No dispatched jobs for this NGO right now.')),
          ],
        ),
      );
    }

    final selectedJob =
        _jobs.firstWhere((item) => item.rescueId == _selectedRescueId, orElse: () => _jobs.first);
    final pendingJobs = _jobs.where((item) => item.responseStatus == 'pending').length;
    final avgResponse = _jobs
        .where((item) => item.responseMinutes != null)
        .map((item) => item.responseMinutes!)
        .toList();
    final avgResponseLabel = avgResponse.isEmpty
        ? '-'
        : '${(avgResponse.reduce((a, b) => a + b) / avgResponse.length).toStringAsFixed(1)}m';

    return RefreshIndicator(
      onRefresh: _loadData,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text('NGO Rescue Jobs', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              _metricCard('Pending Jobs', pendingJobs.toString(), Icons.warning_amber_outlined),
              _metricCard('Avg Response', avgResponseLabel, Icons.timer_outlined),
            ],
          ),
          const SizedBox(height: 8),
          DropdownButtonFormField<int>(
            initialValue: _selectedNgoId,
            items: _ngos
                .map((ngo) => DropdownMenuItem(value: ngo.id, child: Text('${ngo.id} - ${ngo.name}')))
                .toList(),
            onChanged: (value) async {
              setState(() => _selectedNgoId = value);
              await _loadJobs();
              await _loadRanking();
            },
            decoration: const InputDecoration(labelText: 'Your NGO'),
          ),
          const SizedBox(height: 8),
          DropdownButtonFormField<int>(
            initialValue: _selectedRescueId,
            items: _jobs
                .map((job) => DropdownMenuItem(
                      value: job.rescueId,
                      child: Text('#${job.rescueId} - ${job.foodType} (${job.mealsAvailable} meals)'),
                    ))
                .toList(),
            onChanged: (value) async {
              setState(() => _selectedRescueId = value);
              await _loadRanking();
            },
            decoration: const InputDecoration(labelText: 'Select Rescue Job'),
          ),
          const SizedBox(height: 8),
          Card(
            child: ListTile(
              title: Text(selectedJob.foodType),
              subtitle: Text('${selectedJob.providerName} • ${selectedJob.mealsAvailable} meals • Wave ${selectedJob.wave}'),
              trailing: Text('${selectedJob.responseStatus.toUpperCase()} / ${selectedJob.rescueStatus.toUpperCase()}'),
            ),
          ),
          const SizedBox(height: 8),
          const Text('NGO Rankings', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          if (_ranking != null) ...[
            const SizedBox(height: 6),
            Text('Wave ${_ranking!.alertWave} — ${_ranking!.ngosNotified.length} NGOs notified'),
            ..._ranking!.ngosNotified.take(5).map(
                  (ngo) => Card(
                    child: ListTile(
                      title: Text(ngo.ngoName),
                      subtitle: Text(
                        '${ngo.distanceKm.toStringAsFixed(1)} km • ${(ngo.acceptanceProbability * 100).toStringAsFixed(0)}% accept',
                      ),
                      trailing: Text(ngo.finalScore.toStringAsFixed(3)),
                    ),
                  ),
                ),
          ],
          const SizedBox(height: 10),
          FilledButton(onPressed: _acceptRescue, child: const Text('Accept This Rescue')),
          const SizedBox(height: 12),
          DropdownButtonFormField<String>(
            initialValue: _nextStatus,
            items: const [
              DropdownMenuItem(value: 'accepted', child: Text('Accepted')),
              DropdownMenuItem(value: 'on_the_way', child: Text('On the Way')),
              DropdownMenuItem(value: 'picked_up', child: Text('Picked Up')),
              DropdownMenuItem(value: 'completed', child: Text('Completed')),
            ],
            onChanged: (value) => setState(() => _nextStatus = value ?? _nextStatus),
            decoration: const InputDecoration(labelText: 'Next Status'),
          ),
          const SizedBox(height: 8),
          OutlinedButton(onPressed: _updateStatus, child: const Text('Update Status')),
        ],
      ),
    );
  }
}

class AdminTab extends StatefulWidget {
  const AdminTab({super.key});

  @override
  State<AdminTab> createState() => _AdminTabState();
}

class _AdminTabState extends State<AdminTab> {
  final ApiService _api = ApiService();

  List<ProviderModel> _scores = [];
  List<NgoModel> _ngos = [];
  bool _loading = false;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() => _loading = true);
    try {
      final scores = await _api.providerScores();
      final ngos = await _api.listNgos();
      setState(() {
        _scores = scores;
        _ngos = ngos;
      });
    } catch (error) {
      _showError(error);
    } finally {
      setState(() => _loading = false);
    }
  }

  Future<void> _retrain() async {
    try {
      final result = await _api.retrainModel();
      if (result['retrained'] == true) {
        _showMessage('Successfully retrained using ${result['rows']} rescue logs.');
      } else {
        _showMessage(result['reason']?.toString() ?? 'Retraining skipped.');
      }
    } catch (error) {
      _showError(error);
    }
  }

  void _showError(Object error) {
    _showMessage(error.toString().replaceFirst('Exception: ', ''));
  }

  void _showMessage(String message) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Center(child: CircularProgressIndicator());
    }

    final averageScore = _scores.isEmpty
        ? 0.0
        : _scores.map((item) => item.score).reduce((a, b) => a + b) / _scores.length;
    final activeNgos = _ngos.where((ngo) => ngo.active == 1).length;
    final averageAcceptRate = _ngos.isEmpty
        ? 0.0
        : _ngos.map((ngo) => ngo.acceptRate).reduce((a, b) => a + b) / _ngos.length;

    return RefreshIndicator(
      onRefresh: _loadData,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text('Admin Control Panel', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              _metricCard('Avg Fairness Score', averageScore.toStringAsFixed(3), Icons.balance_outlined),
              _metricCard('Total NGOs', _ngos.length.toString(), Icons.groups_outlined),
              _metricCard('Active NGOs', activeNgos.toString(), Icons.check_circle_outline),
              _metricCard('Avg Accept Rate', '${(averageAcceptRate * 100).toStringAsFixed(1)}%', Icons.trending_up_outlined),
            ],
          ),
          const SizedBox(height: 12),
          const Text('Provider Fairness Scores', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          ..._scores.map(
            (provider) => Card(
              child: ListTile(
                title: Text(provider.name),
                subtitle: LinearProgressIndicator(value: provider.score.clamp(0, 1)),
                trailing: Text(provider.score.toStringAsFixed(3)),
              ),
            ),
          ),
          const SizedBox(height: 8),
          FilledButton.icon(
            onPressed: _retrain,
            icon: const Icon(Icons.refresh),
            label: const Text('Retrain ML Model Now'),
          ),
          const SizedBox(height: 12),
          const Text('Registered NGOs', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          ..._ngos.map(
            (ngo) => Card(
              child: ListTile(
                title: Text(ngo.name),
                subtitle: Text(
                  '(${ngo.lat.toStringAsFixed(3)}, ${ngo.lng.toStringAsFixed(3)}) • ${(ngo.acceptRate * 100).toStringAsFixed(1)}% accept • ${ngo.avgResponseMinutes.toStringAsFixed(1)}m response',
                ),
                trailing: Text(ngo.active == 1 ? 'Active' : 'Inactive'),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

Widget _sectionTitle(String title, IconData icon) {
  return Row(
    children: [
      Icon(icon, size: 20),
      const SizedBox(width: 8),
      Text(title, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
    ],
  );
}

Widget _metricCard(String title, String value, IconData icon) {
  return SizedBox(
    width: 170,
    child: Card(
      elevation: 1.2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(icon, size: 18),
            const SizedBox(height: 6),
            Text(title, style: const TextStyle(fontSize: 12)),
            const SizedBox(height: 6),
            Text(value, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w700)),
          ],
        ),
      ),
    ),
  );
}

String? _required(String? value) {
  if (value == null || value.trim().isEmpty) {
    return 'Required';
  }
  return null;
}

String? _validatePositiveInt(String? value) {
  if (value == null || value.trim().isEmpty) {
    return 'Required';
  }
  final parsed = int.tryParse(value.trim());
  if (parsed == null || parsed <= 0) {
    return 'Must be > 0';
  }
  return null;
}

String? _validateDouble(String? value) {
  if (value == null || value.trim().isEmpty) {
    return 'Required';
  }
  if (double.tryParse(value.trim()) == null) {
    return 'Invalid number';
  }
  return null;
}
