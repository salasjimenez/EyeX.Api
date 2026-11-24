# EyeX — Parte 2: calidad, dependencias, paridad y seguridad

**Base:** `e6df8c3b278cf80ff69fa85ca27801cb98cfc3a9`, posterior a la parte 1.

## Alcance 06–10

06. Toolchain Go mínimo 1.26; ejecución CI/Docker con Go 1.27.4. Node.js 24 LTS en CI. Migración de Java a Spring Boot 4.0.10 y starter Web MVC: **requiere ejecutar `mvn test` y paridad antes de publicar**. PHP 8.4 y Java 21 continúan. Los paquetes npm mantienen los rangos existentes para evitar cambios mayores sin tests.

07. Se incorporan `package-lock.json` en los seis proyectos npm. La generación ocurre en la máquina del mantenedor porque depende de npm y del registro; **no se incluyen hashes ni resoluciones inventadas**. `npm ci` reemplaza `npm install` en CI.

08. CI con versiones de toolchain definidas, `go test -race`, cobertura real, artefactos, tipos, OpenAPI y paridad ampliada. Se conserva el umbral histórico de cobertura Go (50%) hasta revisar el reporte real.

09. `tests/parity_extended.py` ejecuta los casos originales más doce casos adicionales para el contrato v1.5.0 en los cuatro runtimes. No cambia respuestas ni endpoints de negocio.

10. Nuevo workflow de seguridad: revisión de dependencias en PR, CodeQL para Go/Java/JS, Trivy (archivos e imagen) y SBOM SPDX JSON (Syft). Los escaneos Trivy inicialmente **informan** (`exit-code: 0`), no bloquean por vulnerabilidades: es necesario clasificar los hallazgos y cambiar a salida 1 una vez establecido el baseline. Fallos de ejecución del scanner sí pueden fallar el job.

## Aplicación desde ZIP del asistente

```bash
cd ~/OneDrive/Escritorio/EyeX
python ../eyex-parte2-paquete/apply-part2.py --repo . --dry-run
python ../eyex-parte2-paquete/apply-part2.py --repo . --apply
```

No crea ramas, commits, tags ni hace push. Antes de aplicar, comprueba el commit base, la limpieza de archivos versionados y crea un respaldo fuera del repositorio.

## Resolución de lockfiles (requiere internet)

```bash
python scripts/create-lockfiles.py
```

Este script usa `npm install --package-lock-only --ignore-scripts --no-audit --no-fund`. Resuelve dependencias compatibles con los rangos declarados, no ejecuta scripts de instalación ni modifica `package.json`. Para actualizar versiones dentro de esos rangos posteriormente, revisar Dependabot y `npm audit` antes de aceptar cambios.

## Validaciones locales obligatorias

```bash
go version                        # Go >= 1.26
node --version                    # Node 24 recomendado
java -version                     # Java 21
mvn -B -ntp -f implementations/java/pom.xml test

go test -race -count=1 ./...
go vet ./...
python3 -m py_compile tests/parity.py tests/parity_extended.py
python scripts/verify-part2.py
```

Para validar Node, ejecutar `npm ci` y `npm run build` en cada una de las seis carpetas npm. Para PHP, revisar sintaxis de los tres archivos en `implementations/php`. Para Flutter, ejecutar `dart pub get` y `dart analyze` en `sdk/flutter`; no hay lockfile de aplicación obligatorio para un SDK de librería.

Las pruebas HTTP completas requieren iniciar los cuatro backends o ejecutar el job `parity` de GitHub Actions:

```bash
python3 tests/parity_extended.py --wait 120
```

Una vez resueltas las dependencias npm y terminadas las validaciones:

```bash
python scripts/package-part2.py
unzip -t ../eyex-part2-modified-files.zip
```

No hacer push hasta que `mvn test`, los builds npm y la paridad de Go/PHP/Node/Java terminen correctamente. Si la migración de Spring Boot cambia la serialización o errores, ajustar primero el backend Java y las pruebas.

## Fuentes oficiales de versiones

- Go: https://go.dev/doc/devel/release
- Node LTS: https://nodejs.org/en/about/previous-releases
- Spring Boot 4 migration: https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide
- npm ci: https://docs.npmjs.com/cli/commands/npm-ci/
- CodeQL: https://github.com/github/codeql-action
- Trivy: https://github.com/aquasecurity/trivy-action

## Limitaciones

- No se realizaron instalaciones npm ni Maven en el entorno de preparación por falta de conectividad con sus registros.
- No se certifica aún paridad en cuatro lenguajes ni ausencia de vulnerabilidades.
- Dockerfile: **solo** se actualiza la imagen de compilación Go para compatibilidad; hardening integral, Kubernetes y Terraform pertenecen a la parte 3.

## Correccion adicional detectada en integracion local

- `web/tsconfig.json` incorpora `rootDir: src` para que TypeScript 6 conserve la estructura `dist/assets` sin el error TS5011.
- Antes de publicar, revisar el aviso de dos dependencias npm HIGH en Vue: ejecutar `cd frontend/vue && npm audit --audit-level=high` y corregir solo despues de evaluar impacto; no usar `npm audit fix --force` de manera automatica.
- Los tests Maven previos a aplicar Parte 2 ejecutan Spring Boot 3, no certifican la migracion a Spring Boot 4.
