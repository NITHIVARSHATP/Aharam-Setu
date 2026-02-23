import 'package:flutter_test/flutter_test.dart';

import 'package:aharam_setu_flutter/main.dart';

void main() {
  testWidgets('App renders tab labels', (WidgetTester tester) async {
    await tester.pumpWidget(const AharamSetuApp());

    expect(find.text('Enter App'), findsOneWidget);
    await tester.tap(find.text('Enter App'));
    await tester.pumpAndSettle();

    expect(find.text('Provider'), findsWidgets);
    expect(find.text('NGO'), findsWidgets);
    expect(find.text('Admin'), findsWidgets);
  });
}
