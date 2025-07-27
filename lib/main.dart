import 'package:flutter/material.dart';
import 'widgets/ChatScreen.dart';

void main() {
  runApp(DentAssistApp());
}

class DentAssistApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'DentAssist',
      routerDelegate: _AppRouterDelegate(),
      routeInformationParser: _AppRouteParser(),
    );
  }
}

class _AppRouterDelegate extends RouterDelegate<RouteSettings>
    with ChangeNotifier, PopNavigatorRouterDelegateMixin<RouteSettings> {
  final GlobalKey<NavigatorState> navigatorKey = GlobalKey<NavigatorState>();

  @override
  Widget build(BuildContext context) {
    return Navigator(
      key: navigatorKey,
      pages: [
        MaterialPage(child: ChatScreen()),
      ],
      onPopPage: (route, result) => route.didPop(result),
    );
  }

  @override
  Future<void> setNewRoutePath(RouteSettings configuration) async {}
}

class _AppRouteParser extends RouteInformationParser<RouteSettings> {
  @override
  Future<RouteSettings> parseRouteInformation(
      RouteInformation routeInformation) async {
    return RouteSettings(name: routeInformation.uri.toString());
  }

  @override
  RouteInformation restoreRouteInformation(RouteSettings configuration) {
    final loc = configuration.name ?? '/';
    return RouteInformation(uri: Uri.parse(loc));
  }
}

