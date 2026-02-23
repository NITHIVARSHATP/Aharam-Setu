class ProviderModel {
  final int id;
  final String name;
  final double score;

  ProviderModel({required this.id, required this.name, required this.score});

  factory ProviderModel.fromJson(Map<String, dynamic> json) {
    return ProviderModel(
      id: json['id'] as int,
      name: (json['name'] ?? '').toString(),
      score: (json['score'] as num?)?.toDouble() ?? 0,
    );
  }
}

class NgoModel {
  final int id;
  final String name;
  final double lat;
  final double lng;
  final double acceptRate;
  final double avgResponseMinutes;
  final int pastPickups;
  final int active;

  NgoModel({
    required this.id,
    required this.name,
    required this.lat,
    required this.lng,
    required this.acceptRate,
    required this.avgResponseMinutes,
    required this.pastPickups,
    required this.active,
  });

  factory NgoModel.fromJson(Map<String, dynamic> json) {
    return NgoModel(
      id: json['id'] as int,
      name: (json['name'] ?? '').toString(),
      lat: (json['lat'] as num?)?.toDouble() ?? 0,
      lng: (json['lng'] as num?)?.toDouble() ?? 0,
      acceptRate: (json['accept_rate'] as num?)?.toDouble() ?? 0,
      avgResponseMinutes: (json['avg_response_minutes'] as num?)?.toDouble() ?? 0,
      pastPickups: (json['past_pickups'] as num?)?.toInt() ?? 0,
      active: (json['active'] as num?)?.toInt() ?? 0,
    );
  }
}

class RescueModel {
  final int id;
  final String providerName;
  final int mealsAvailable;
  final String foodType;
  final String status;

  RescueModel({
    required this.id,
    required this.providerName,
    required this.mealsAvailable,
    required this.foodType,
    required this.status,
  });

  factory RescueModel.fromJson(Map<String, dynamic> json) {
    return RescueModel(
      id: json['id'] as int,
      providerName: (json['provider_name'] ?? '').toString(),
      mealsAvailable: (json['meals_available'] as num?)?.toInt() ?? 0,
      foodType: (json['food_type'] ?? '').toString(),
      status: (json['status'] ?? '').toString(),
    );
  }
}

class RankedNgoModel {
  final int ngoId;
  final String ngoName;
  final double distanceKm;
  final double acceptanceProbability;
  final double speedScore;
  final double reliabilityScore;
  final double finalScore;

  RankedNgoModel({
    required this.ngoId,
    required this.ngoName,
    required this.distanceKm,
    required this.acceptanceProbability,
    required this.speedScore,
    required this.reliabilityScore,
    required this.finalScore,
  });

  factory RankedNgoModel.fromJson(Map<String, dynamic> json) {
    return RankedNgoModel(
      ngoId: json['ngo_id'] as int,
      ngoName: (json['ngo_name'] ?? '').toString(),
      distanceKm: (json['distance_km'] as num?)?.toDouble() ?? 0,
      acceptanceProbability: (json['acceptance_probability'] as num?)?.toDouble() ?? 0,
      speedScore: (json['speed_score'] as num?)?.toDouble() ?? 0,
      reliabilityScore: (json['reliability_score'] as num?)?.toDouble() ?? 0,
      finalScore: (json['final_score'] as num?)?.toDouble() ?? 0,
    );
  }
}

class RankingResponse {
  final int rescueId;
  final int alertWave;
  final List<RankedNgoModel> ngosNotified;

  RankingResponse({
    required this.rescueId,
    required this.alertWave,
    required this.ngosNotified,
  });

  factory RankingResponse.fromJson(Map<String, dynamic> json) {
    return RankingResponse(
      rescueId: json['rescue_id'] as int,
      alertWave: json['alert_wave'] as int,
      ngosNotified: ((json['ngos_notified'] ?? []) as List)
          .map((item) => RankedNgoModel.fromJson(item as Map<String, dynamic>))
          .toList(),
    );
  }
}

class AcceptResponse {
  final bool assigned;
  final String message;

  AcceptResponse({required this.assigned, required this.message});

  factory AcceptResponse.fromJson(Map<String, dynamic> json) {
    return AcceptResponse(
      assigned: json['assigned'] as bool? ?? false,
      message: (json['message'] ?? '').toString(),
    );
  }
}

class NgoJobModel {
  final int rescueId;
  final int wave;
  final String notifiedAt;
  final String responseStatus;
  final double? responseMinutes;
  final String rescueStatus;
  final int mealsAvailable;
  final String foodType;
  final String eventType;
  final String providerName;

  NgoJobModel({
    required this.rescueId,
    required this.wave,
    required this.notifiedAt,
    required this.responseStatus,
    required this.responseMinutes,
    required this.rescueStatus,
    required this.mealsAvailable,
    required this.foodType,
    required this.eventType,
    required this.providerName,
  });

  factory NgoJobModel.fromJson(Map<String, dynamic> json) {
    return NgoJobModel(
      rescueId: (json['rescue_id'] as num?)?.toInt() ?? 0,
      wave: (json['wave'] as num?)?.toInt() ?? 1,
      notifiedAt: (json['notified_at'] ?? '').toString(),
      responseStatus: (json['response_status'] ?? '').toString(),
      responseMinutes: (json['response_minutes'] as num?)?.toDouble(),
      rescueStatus: (json['rescue_status'] ?? '').toString(),
      mealsAvailable: (json['meals_available'] as num?)?.toInt() ?? 0,
      foodType: (json['food_type'] ?? '').toString(),
      eventType: (json['event_type'] ?? '').toString(),
      providerName: (json['provider_name'] ?? '').toString(),
    );
  }
}
