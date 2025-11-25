// lib/constants.dart

// Для Android-эмулятора localhost хоста доступен через 10.0.2.2
// Если будешь запускать на реальном устройстве — замени на IP машины:
//   const String API_BASE = "http://192.168.0.101:8000";
const String API_BASE = "http://localhost:8000";

const String LOGIN_PATH = "/api/v1/auth/login/";
const String REGISTER_PATH = "/api/v1/auth/register/";
const String REFRESH_PATH = "/api/v1/auth/refresh/";
