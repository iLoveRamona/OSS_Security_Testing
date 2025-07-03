## SonarQube инструкция

Запустить сервер
```sh
docker compose up -d sonarqub
```
Нужно установить следующие переменные окружения: `SONAR_TOKEN`, `PROJECT_KEY`, `PROJECT_PATH`.

Запустить скан
```sh
docker compose run --rm sonar-scanner -Dsonar.token="$SONAR_TOKEN" -Dsonar.projectKey="$PROJECT_KEY"
```
Получить json файл с проблемами безопасности
```sh
curl -u $SONAR_TOKEN: "http://localhost:9000/api/issues/search?componentKeys=$PROJECT_KEY&ps=500&impactSoftwareQualities=SECURITY" > issues.json
```
