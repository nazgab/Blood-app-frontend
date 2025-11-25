import 'package:flutter/material.dart';
import 'bonus_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> with TickerProviderStateMixin {
  int _currentIndex = 0;
  String _selectedCity = 'Көкшетау';
  double _bonuses = 1341.60;

  final List<String> _cities = [
    'Астана',
    'Алматы',
    'Шымкент',
    'Көкшетау',
    'Қарағанды',
    'Орал',
    'Ақтөбе',
    'Түркістан',
    'Павлодар',
    'Қызылорда',
  ];

  final List<Map<String, String>> _newsList = [
    {
      'title': 'Қан тапсыру',
      'date': '2025-10-22',
      'time': '14:30 - 20:00',
      'place': 'Облыстық қан орталығы',
      'address': 'Темірбеков көшесі 69',
    },
    {
      'title': 'Қан тапсыру',
      'date': '2025-10-23',
      'time': '16:10 - 19:00',
      'place': 'Облыстық қан орталығы',
      'address': 'Темірбеков көшесі 69',
    },
    {
      'title': 'Қан тапсыру',
      'date': '2025-10-24',
      'time': '10:00 - 18:00',
      'place': 'Қалалық қан орталығы',
      'address': 'Абылай хан даңғылы 45',
    },
  ];

  void _openBonusScreen() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => BonusScreen(bonuses: _bonuses),
      ),
    );
  }

  void _openCityPicker() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) {
        return _CityPickerSheet(
          cities: _cities,
          onSelected: (city) {
            setState(() => _selectedCity = city);
          },
        );
      },
    );
  }

  Widget _buildBody() {
    switch (_currentIndex) {
      case 0:
        return _buildHomeBody();
      case 1:
        return _buildHistoryBody();
      default:
        return _buildHomeBody();
    }
  }

  Widget _buildHomeBody() {
    const red = Color(0xFFD32F2F);
    return SafeArea(
      child: Column(
        children: [
          _buildHeader(red),
          const SizedBox(height: 16),
          const Text(
            'BLOODSEEKER',
            style: TextStyle(color: red, fontSize: 26, fontWeight: FontWeight.w800),
          ),
          const SizedBox(height: 6),
          const Text(
            'Өмір сыйлағаныңызға алғысымыз шексіз',
            style: TextStyle(fontSize: 15, color: Colors.black87),
          ),
          const SizedBox(height: 14),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20),
            child: TextField(
              decoration: InputDecoration(
                hintText: 'Іздеу бойынша сұрыптау',
                prefixIcon: const Icon(Icons.search),
                filled: true,
                fillColor: const Color(0xFFEAEAEA),
                contentPadding: const EdgeInsets.symmetric(horizontal: 18, vertical: 12),
                border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(14), borderSide: BorderSide.none),
              ),
            ),
          ),
          const SizedBox(height: 16),
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
              child: Column(
                children: _newsList.map((news) {
                  return Container(
                    margin: const EdgeInsets.only(bottom: 20),
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: const Color(0xFFF5F5F5),
                      borderRadius: BorderRadius.circular(16),
                      boxShadow: [
                        BoxShadow(
                            color: Colors.black12.withOpacity(0.05),
                            blurRadius: 5,
                            offset: const Offset(0, 2))
                      ],
                    ),
                    child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(news['title']!,
                              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w700)),
                          const SizedBox(height: 6),
                          Text(news['date']!,
                              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                          Text(news['time']!, style: const TextStyle(fontSize: 15)),
                          const SizedBox(height: 8),
                          Text(news['place']!,
                              style:
                                  const TextStyle(fontWeight: FontWeight.w600, fontSize: 15)),
                          Text(news['address']!, style: const TextStyle(fontSize: 15)),
                          const SizedBox(height: 10),
                          ElevatedButton(
                            style: ElevatedButton.styleFrom(
                                backgroundColor: red,
                                foregroundColor: Colors.white,
                                shape:
                                    RoundedRectangleBorder(borderRadius: BorderRadius.circular(8))),
                            onPressed: () {},
                            child: const Text('Кездесуді көрсету'),
                          ),
                        ]),
                  );
                }).toList(),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHistoryBody() {
    const red = Color(0xFFD32F2F);
    return SafeArea(
      child: Column(
        children: [
          _buildHeader(red),
          const SizedBox(height: 10),
          const Text('История',
              style: TextStyle(color: red, fontWeight: FontWeight.bold, fontSize: 26)),
          const SizedBox(height: 16),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: const [
                _InfoCard(title: 'Барлық тапсырылған қан көлемі', value: '5400 ml'),
                _InfoCard(title: 'Донaциялар саны', value: '12'),
                _InfoCard(title: 'Соңғы тапсыру күні', value: '30.10.2025'),
              ],
            ),
          ),
          const SizedBox(height: 20),
          const Text('История бонусов',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
          const SizedBox(height: 12),
          Expanded(
            child: ListView(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              children: const [
                _BonusRow(index: 1, date: '25.10.25', address: 'Пушкина 14', volume: '450', done: true),
                _BonusRow(index: 2, date: '06.10.25', address: 'Абая 4а', volume: '300', done: true),
                _BonusRow(index: 3, date: '10.10.25', address: 'Абая 4а', volume: '320', done: false),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHeader(Color red) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.only(
          bottomLeft: Radius.circular(24),
          bottomRight: Radius.circular(24),
        ),
        boxShadow: [
          BoxShadow(color: Colors.black12, blurRadius: 6, offset: Offset(0, 3)),
        ],
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          InkWell(
            onTap: _openBonusScreen,
            borderRadius: BorderRadius.circular(18),
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(18),
                gradient: const LinearGradient(
                  colors: [Color(0xFFEB5757), Color(0xFF56CCF2)],
                ),
              ),
              child: Row(
                children: [
                  Text(
                    '${_bonuses.toStringAsFixed(2)} ',
                    style: const TextStyle(
                        color: Colors.white, fontSize: 15, fontWeight: FontWeight.w600),
                  ),
                  const Icon(Icons.bloodtype_rounded, color: Colors.white, size: 18),
                ],
              ),
            ),
          ),
          InkWell(
            onTap: _openCityPicker,
            borderRadius: BorderRadius.circular(8),
            child: Row(
              children: [
                const Icon(Icons.map_outlined, color: Colors.black87),
                const SizedBox(width: 6),
                Text(
                  _selectedCity,
                  style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w500),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    const red = Color(0xFFD32F2F);
    return Scaffold(
      backgroundColor: Colors.white,
      body: _buildBody(),
      bottomNavigationBar: ClipRRect(
        borderRadius: const BorderRadius.only(
            topLeft: Radius.circular(24), topRight: Radius.circular(24)),
        child: BottomNavigationBar(
          currentIndex: _currentIndex,
          onTap: (index) => setState(() => _currentIndex = index),
          selectedItemColor: red,
          unselectedItemColor: Colors.black54,
          showUnselectedLabels: false,
          items: const [
            BottomNavigationBarItem(icon: Icon(Icons.home_outlined), label: ''),
            BottomNavigationBarItem(icon: Icon(Icons.pie_chart_outline), label: ''),
            BottomNavigationBarItem(icon: Icon(Icons.description_outlined), label: ''),
            BottomNavigationBarItem(
              icon: CircleAvatar(
                  radius: 14,
                  backgroundImage: AssetImage('assets/images/profile.jpg')),
              label: '',
            ),
          ],
        ),
      ),
    );
  }
}

class _InfoCard extends StatelessWidget {
  final String title;
  final String value;
  const _InfoCard({required this.title, required this.value});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 110,
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: const [
          BoxShadow(color: Colors.black12, blurRadius: 6, offset: Offset(0, 3)),
        ],
      ),
      child: Column(
        children: [
          Text(value,
              style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  color: Color(0xFFD32F2F),
                  fontSize: 18)),
          const SizedBox(height: 4),
          Text(title,
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 11, color: Colors.black87)),
        ],
      ),
    );
  }
}

class _BonusRow extends StatelessWidget {
  final int index;
  final String date;
  final String address;
  final String volume;
  final bool done;

  const _BonusRow({
    required this.index,
    required this.date,
    required this.address,
    required this.volume,
    required this.done,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 8),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(10),
        color: Colors.grey.shade100,
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text('$index'),
          SizedBox(width: 60, child: Text(date)),
          Expanded(child: Text(address, textAlign: TextAlign.center)),
          SizedBox(width: 50, child: Text(volume, textAlign: TextAlign.center)),
          Icon(done ? Icons.check_circle : Icons.hourglass_empty,
              color: done ? Colors.green : Colors.grey),
        ],
      ),
    );
  }
}

class _CityPickerSheet extends StatelessWidget {
  final List<String> cities;
  final ValueChanged<String> onSelected;

  const _CityPickerSheet({
    required this.cities,
    required this.onSelected,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 20),
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.only(
          topLeft: Radius.circular(24),
          topRight: Radius.circular(24),
        ),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 50,
            height: 5,
            margin: const EdgeInsets.only(bottom: 16),
            decoration: BoxDecoration(
              color: Colors.grey.shade300,
              borderRadius: BorderRadius.circular(10),
            ),
          ),
          const Text(
            'Қаланы таңдаңыз',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 16),

          ...cities.map((city) {
            return ListTile(
              title: Text(city, style: const TextStyle(fontSize: 16)),
              onTap: () {
                onSelected(city);
                Navigator.pop(context);
              },
            );
          }).toList(),
        ],
      ),
    );
  }
}
