import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

import 'models.dart';

class ApiService {
  ApiService({String? baseUrl})
  : _baseUrl = baseUrl ?? _defaultBaseUrl();

  final String _baseUrl;

  static String _defaultBaseUrl() {
    if (kIsWeb) {
      return 'http://127.0.0.1:8000';
    }
    switch (defaultTargetPlatform) {
      case TargetPlatform.android:
        return 'http://10.0.2.2:8000';
      default:
        return 'http://127.0.0.1:8000';
    }
  }

  Future<List<ProviderModel>> listProviders() async {
    final data = await _get('/providers');
    return (data as List)
        .map((item) => ProviderModel.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<List<NgoModel>> listNgos() async {
    final data = await _get('/ngos');
    return (data as List)
        .map((item) => NgoModel.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<List<RescueModel>> listLiveRescues() async {
    final data = await _get('/rescues/live');
    return (data as List)
        .map((item) => RescueModel.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<Map<String, dynamic>> createRescue(Map<String, dynamic> payload) async {
    return await _post('/rescues', payload) as Map<String, dynamic>;
  }

  Future<RankingResponse> getRescueRanking(int rescueId) async {
    final data = await _get('/rescues/$rescueId/ranking');
    return RankingResponse.fromJson(data as Map<String, dynamic>);
  }

  Future<AcceptResponse> acceptRescue(int rescueId, int ngoId) async {
    final data = await _post('/rescues/$rescueId/accept/$ngoId', {});
    return AcceptResponse.fromJson(data as Map<String, dynamic>);
  }

  Future<Map<String, dynamic>> updateRescueStatus(int rescueId, String status) async {
    return await _patch('/rescues/$rescueId/status', {'status': status}) as Map<String, dynamic>;
  }

  Future<List<ProviderModel>> providerScores() async {
    final data = await _get('/admin/provider-scores');
    return (data as List)
        .map((item) => ProviderModel.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<Map<String, dynamic>> retrainModel() async {
    return await _post('/admin/retrain', {}) as Map<String, dynamic>;
  }

  Future<dynamic> _get(String path) async {
    final response = await http.get(Uri.parse('$_baseUrl$path'));
    return _decodeResponse(response);
  }

  Future<dynamic> _post(String path, Map<String, dynamic> payload) async {
    final response = await http.post(
      Uri.parse('$_baseUrl$path'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    );
    return _decodeResponse(response);
  }

  Future<dynamic> _patch(String path, Map<String, dynamic> payload) async {
    final response = await http.patch(
      Uri.parse('$_baseUrl$path'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    );
    return _decodeResponse(response);
  }

  dynamic _decodeResponse(http.Response response) {
    final body = response.body.isEmpty ? null : jsonDecode(response.body);
    if (response.statusCode >= 200 && response.statusCode < 300) {
      return body;
    }
    if (body is Map<String, dynamic> && body['detail'] != null) {
      throw Exception(body['detail'].toString());
    }
    throw Exception('Request failed (${response.statusCode})');
  }
}
