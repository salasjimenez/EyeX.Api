# @eyex/react-native

Cliente TypeScript para consumir EyeX API v1.5.0 desde React Native.

## Instalación

Desde el repositorio:

```bash
cd sdk/react-native
npm install
npm run build
```

Cuando el paquete esté publicado:

```bash
npm install @eyex/react-native
```

El runtime debe proporcionar `fetch`, como ocurre en las versiones actuales de React Native.

## Uso mínimo

```ts
import { EyeXClient } from '@eyex/react-native';

const client = new EyeXClient('http://localhost:8080');

const theme = await client.theme('tritanopia', {
  severity: 'moderate',
  mode: 'dark',
});

console.log(theme.palette.primary);
```

## Simulación

```ts
const simulated = await client.simulate('#FF0000', 'protanopia', 0.65);
console.log(simulated.simulated); // #A05A00

const batch = await client.simulateBatch(
  ['#FF0000', '#00FF00'],
  'deuteranopia',
  0.5,
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
