# mini_mute_bot

Телеграм-бот для супергруппы. Два независимых режима:

- **только мьют** — бот и больше ничего, база и сайт не нужны (по умолчанию);
- **мьют + турнир** — добавляется postgres, регистрация участников и таблица на сайте.

Режим переключается переменной `ENABLE_TOURNAMENT` в `.env` и тем, с каким
compose-файлом запускается проект.

## Мьют

В ответ на сообщение пишем `!mute <минуты>`, например `!mute 20`.

- Время: **от 10 до 60 минут**.
- Работает только в группах/супергруппах.
- Пользователей из `ADMIN_ID` замьютить нельзя.
- Пользователю с id `512563919` команда недоступна (список в
  `MUTE_BLOCKED_IDS` в `backend/tg/mute.py`).

## Турнир

Регистрация участников через бота, внесение и редактирование результатов игр,
таблица с автообновлением на `/tournament`, выгрузка итогов в Excel.

Формат результата: `Имя игрока - Имя игрока 5 - 0`
Овертайм — приписка `от` в конце, буллиты — `бул`.

---

# Развёртывание на сервере

## 1. Что нужно на сервере

Ubuntu/Debian, docker с плагином compose:

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-plugin git
sudo systemctl enable --now docker
sudo usermod -aG docker $USER   # перелогиниться после этого
```

## 2. Забрать код

```bash
git clone <url-репозитория> ~/mini_mute_bot
cd ~/mini_mute_bot
```

## 3. Создать .env

```bash
cp .env.example .env
nano .env
```

Для режима «только мьют» достаточно двух строк:

```
BOT_TOKEN=<токен от @BotFather>
ADMIN_ID=[512563919]
ENABLE_TOURNAMENT=false
```

`.env` в git не попадает (`.gitignore`), на сервере его создаём руками.

## 4. Запуск

**Только мьют:**

```bash
./restart.sh
```

Поднимается один контейнер `bot`. Ни postgres, ни портов наружу.

**С турниром:** в `.env` выставить `ENABLE_TOURNAMENT=true`, заполнить блок
`DB_*` (`DB_HOST=db`, пароль придумать свой) и запустить:

```bash
./restart.sh tournament
```

Порядок запуска: `db` → `migrate` (`alembic upgrade head`) → `bot` и `api`.
Миграции прогоняются сами, вручную ничего запускать не надо.

Скрипт перед стартом гасит контейнеры обоих режимов, поэтому переключаться
туда-обратно можно спокойно.

Проверить:

```bash
docker compose ps
docker compose logs bot     # должно быть "Турнир выключен, работает только мьют"
```

## 5. Права бота в Telegram

Бот должен быть **администратором** группы с правом «Блокировка пользователей»,
иначе `!mute` не сработает. Ещё в @BotFather нужно выключить Privacy Mode
(`/setprivacy` → Disable), иначе бот не увидит `!mute` в чате.

Этого достаточно, если турнир не нужен — дальше можно не читать.

---

# Дополнительно для режима с турниром

## Nginx + HTTPS для таблицы

```nginx
server {
    server_name nhl.originaltournament.ru;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo certbot --nginx -d nhl.originaltournament.ru
```

Когда nginx настроен, порт 8000 лучше закрыть снаружи — в
`docker-compose.tournament.yml` заменить `"8000:8000"` на
`"127.0.0.1:8000:8000"` и перезапустить.

## Перенос базы со старого сервера

Раньше postgres стоял на самом сервере, теперь он в контейнере. Если в старой
базе есть данные:

```bash
# на старом сервере
pg_dump -U <старый_юзер> -d <старая_база> -F c -f dump.bak
scp dump.bak user@новый-сервер:~/

# на новом, после ./restart.sh tournament
docker compose -f docker-compose.yml -f docker-compose.tournament.yml cp ~/dump.bak db:/tmp/dump.bak
docker compose -f docker-compose.yml -f docker-compose.tournament.yml exec db \
    pg_restore -U $DB_USER -d $DB_NAME --clean --if-exists /tmp/dump.bak
```

Если база не нужна — просто пропустить, схема создастся миграциями.

## Оставить postgres на хосте

В `.env` поставить `DB_HOST=host.docker.internal`, а в
`docker-compose.tournament.yml` удалить сервис `db`, блок `volumes:` и
`depends_on: db` у `migrate`, добавив каждому сервису:

```yaml
    extra_hosts:
      - "host.docker.internal:host-gateway"
```

## Бэкап базы

```bash
docker compose -f docker-compose.yml -f docker-compose.tournament.yml \
    exec -T db pg_dump -U mute_bot mute_bot | gzip > backup_$(date +%F).sql.gz
```

---

## Повседневные команды

```bash
docker compose logs -f bot        # логи бота
docker compose restart bot        # перезапуск
git pull && ./restart.sh          # обновление
```
