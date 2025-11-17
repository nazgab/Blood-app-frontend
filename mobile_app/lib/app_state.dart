import 'package:flutter/material.dart';

class AppState extends ChangeNotifier {
  String _city = 'Көкшетау';

  String get city => _city;

  void setCity(String newCity) {
    _city = newCity;
    notifyListeners();
  }
}
