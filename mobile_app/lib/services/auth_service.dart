// name/lib/services/auth_service.dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../constants.dart';

class AuthService {
  // Login with email & password
  static Future<Map<String, dynamic>> login(String email, String password) async {
    final url = Uri.parse(API_BASE + LOGIN_PATH);
    final resp = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'email': email, 'password': password}),
    );

    if (resp.statusCode == 200) {
      final data = jsonDecode(resp.body);
      await _saveTokens(data);
      return {'ok': true, 'data': data};
    } else {
      String message = 'Ошибка авторизации';
      try {
        final body = jsonDecode(resp.body);
        if (body is Map && body.containsKey('detail')) message = body['detail'].toString();
      } catch (_) {}
      return {'ok': false, 'error': message, 'status': resp.statusCode};
    }
  }

  static Future<void> _saveTokens(Map<String, dynamic> data) async {
    final prefs = await SharedPreferences.getInstance();
    if (data.containsKey('access')) await prefs.setString('access', data['access']);
    if (data.containsKey('refresh')) await prefs.setString('refresh', data['refresh']);
  }

  static Future<String?> getAccessToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('access');
  }

  static Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('access');
    await prefs.remove('refresh');
  }

  static Future<bool> refreshAccess() async {
    final prefs = await SharedPreferences.getInstance();
    final refresh = prefs.getString('refresh');
    if (refresh == null) return false;
    final url = Uri.parse(API_BASE + REFRESH_PATH);
    final resp = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'refresh': refresh}),
    );
    if (resp.statusCode == 200) {
      final data = jsonDecode(resp.body);
      if (data['access'] != null) {
        await prefs.setString('access', data['access']);
        return true;
      }
    }
    await logout();
    return false;
  }

  // Example: authorized GET (auto-refresh if needed)
  static Future<http.Response> authorizedGet(String path) async {
    String? token = await getAccessToken();
    final headers = {'Content-Type': 'application/json'};
    if (token != null) headers['Authorization'] = 'Bearer $token';
    final url = Uri.parse(API_BASE + path);
    var resp = await http.get(url, headers: headers);
    if (resp.statusCode == 401) {
      final ok = await refreshAccess();
      if (ok) {
        token = await getAccessToken();
        if (token != null) headers['Authorization'] = 'Bearer $token';
        resp = await http.get(url, headers: headers);
      }
    }
    return resp;
  }
}
