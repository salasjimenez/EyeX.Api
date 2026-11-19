# EyeX Flutter SDK

Cliente Dart para EyeX API `v1.5.0`.

## Instalación

Para trabajar dentro del repositorio:

```bash
cd sdk/flutter
dart pub get
dart analyze
```

Para consumirlo como dependencia local desde otra aplicación:

```yaml
dependencies:
  eyex:
    path: ../EyeX.Api/sdk/flutter
```

## Uso mínimo

```dart
import 'package:eyex/eyex.dart';

final client = EyeXClient('http://localhost:8080');

final theme = await client.theme(
  'deuteranopia',
  severity: 'moderate',
  mode: 'dark',
);

print(theme.palette.primary);
```

## Simulación

```dart
final simulated = await client.simulate(
  '#FF0000',
  'protanopia',
  severity: 0.65,
);

print(simulated.simulated); // #A05A00
```

Batch:

```dart
final batch = await client.simulateBatch(
  ['#FF0000', '#00FF00', '#0000FF'],
  'deuteranopia',
  severity: 0.5,
);
```

## Sugerencia ampliada y feedback (v1.5.0)

La respuesta `suggest` incluye `severity` (`mild`, `moderate` o `severe`)
y `high_contrast` (booleano), además de los campos históricos.
Las cinco señales visuales nuevas son opcionales y no modifican la firma
obligatoria de los cuatro indicadores anteriores.

La operación `feedback` envía `suggested_type` y `helpful` a
`POST /api/v1/feedback`; devuelve `status: recorded`. En la implementación
actual, el servidor registra la respuesta en logs, sin persistencia garantizada.

Métodos disponibles: `types`, `theme`, `custom`, `suggest`, `feedback`, `simulate` y `simulateBatch`.
