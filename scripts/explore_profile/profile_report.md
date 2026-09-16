# S-A1 Exploration Profile
_generated 2026-09-16T14:35:30 · bucket=60s · alarms=3000_

## Basic counts

- **alarm rows**: 3000
- **columns**: ['alarm_id', 'timestamp', 'source_system', 'host', 'service', 'severity', 'alarm_type', 'message', 'veri_merkezi', 'kabin', 'ortam']
- **null cells per column**: {'alarm_id': 0, 'timestamp': 0, 'source_system': 0, 'host': 0, 'service': 0, 'severity': 0, 'alarm_type': 0, 'message': 0, 'veri_merkezi': 0, 'kabin': 0, 'ortam': 0}
- **duplicate full rows**: 0
- **unique alarm_id**: 3000
- **time span**: 2026-09-10 01:30:20 .. 2026-09-10 03:30:20

## Distributions


### alarm_type (25 distinct)

| alarm_type | count |
|---|---|
| latency_high | 402 |
| timeout | 271 |
| mem_high | 240 |
| cpu_high | 230 |
| cert_expiry | 220 |
| network_flap | 202 |
| http_5xx | 198 |
| log_rotate | 196 |
| ntp_drift | 193 |
| disk_warn | 189 |
| backup_warn | 177 |
| txn_fail | 148 |
| thread_pool | 79 |
| db_conn_pool | 72 |
| db_write_fail | 34 |
| conn_refused | 28 |
| pkt_loss | 22 |
| gc_pressure | 18 |
| disk_full | 17 |
| ext_slow | 13 |
| network_down | 12 |
| oom_risk | 12 |
| batch_slow | 12 |
| ext_unreach | 11 |
| batch_overlap | 4 |

### severity (5 distinct)

| severity | count |
|---|---|
| 3 | 800 |
| 2 | 709 |
| 4 | 629 |
| 1 | 614 |
| 5 | 248 |

### source_system (5 distinct)

| source_system | count |
|---|---|
| SyslogNG | 645 |
| Zabbix | 607 |
| OBM | 604 |
| AppDynamics | 585 |
| Prometheus | 559 |

### service (27 distinct)

| service | count |
|---|---|
| mobile-bff | 278 |
| payment-service | 227 |
| subscriber-service | 212 |
| charging-service | 205 |
| order-service | 199 |
| billing-service | 188 |
| subscriber-db | 172 |
| api-gateway | 159 |
| session-service | 150 |
| auth-service | 121 |
| payment-provider-gw | 113 |
| billing-db | 113 |
| load-balancer | 99 |
| web-bff | 96 |
| dns-resolver | 95 |
| message-queue | 86 |
| report-batch | 78 |
| cache-cluster | 62 |
| invoice-batch | 56 |
| reconciliation-batch | 53 |
| notification-service | 50 |
| kyc-provider-gw | 38 |
| object-store | 34 |
| catalog-service | 31 |
| sms-gateway | 30 |
| batch-scheduler | 30 |
| ntp-service | 25 |

### host (56 distinct)

| host | count |
|---|---|
| ao-027-order | 101 |
| ao-005-mobile | 99 |
| ao-028-order | 98 |
| ao-004-mobile | 95 |
| ao-015-subscriber | 87 |
| ao-024-payment | 86 |
| ao-006-mobile | 84 |
| ao-021-charging | 83 |
| ao-051-report | 78 |
| ao-033-subscriber | 75 |
| ao-018-billing | 74 |
| ao-025-payment | 71 |
| ao-022-charging | 71 |
| ao-026-payment | 70 |
| ao-017-subscriber | 69 |
| ao-045-dns | 64 |
| ao-020-billing | 64 |
| ao-003-api | 64 |
| ao-014-session | 58 |
| ao-049-invoice | 56 |
| ao-016-subscriber | 56 |
| ao-050-reconciliation | 53 |
| ao-031-subscriber | 51 |
| ao-023-charging | 51 |
| ao-008-web | 51 |
| ao-030-notification | 50 |
| ao-019-billing | 50 |
| ao-039-message | 50 |
| ao-012-session | 48 |
| ao-002-api | 48 |
| ao-009-auth | 47 |
| ao-001-api | 47 |
| ao-032-subscriber | 46 |
| ao-007-web | 45 |
| ao-013-session | 44 |
| ao-043-load | 43 |
| ao-054-payment | 40 |
| ao-035-billing | 40 |
| ao-010-auth | 39 |
| ao-056-kyc | 38 |
| ao-052-payment | 37 |
| ao-036-billing | 37 |
| ao-053-payment | 36 |
| ao-034-billing | 36 |
| ao-040-message | 36 |
| ao-011-auth | 35 |
| ao-041-object | 34 |
| ao-042-load | 33 |
| ao-037-cache | 33 |
| ao-046-dns | 31 |
| ao-029-catalog | 31 |
| ao-055-sms | 30 |
| ao-048-batch | 30 |
| ao-038-cache | 29 |
| ao-047-ntp | 25 |
| ao-044-load | 23 |

### veri_merkezi (2 distinct)

| veri_merkezi | count |
|---|---|
| dc1 | 1539 |
| dc2 | 1461 |

### kabin (3 distinct)

| kabin | count |
|---|---|
| rack-A | 1131 |
| rack-B | 969 |
| rack-C | 900 |

### ortam (1 distinct)

| ortam | count |
|---|---|
| prod | 3000 |

## Time histogram

- bucket mean=24.8, median=22, max=79 at 2026-09-10 01:45:00, min=8
```
01:30:00    9 #######
01:31:00   18 ##############
01:32:00   15 ###########
01:33:00   16 ############
01:34:00   13 ##########
01:35:00   23 #################
01:36:00   18 ##############
01:37:00   19 ##############
01:38:00   18 ##############
01:39:00   13 ##########
01:40:00   12 #########
01:41:00   11 ########
01:42:00   31 ########################
01:43:00   47 ####################################
01:44:00   40 ##############################
01:45:00   79 ############################################################
01:46:00   66 ##################################################
01:47:00   69 ####################################################
01:48:00   68 ####################################################
01:49:00   70 #####################################################
01:50:00   48 ####################################
01:51:00   37 ############################
01:52:00   31 ########################
01:53:00   37 ############################
01:54:00   22 #################
01:55:00    9 #######
01:56:00    9 #######
01:57:00   19 ##############
01:58:00   16 ############
01:59:00    9 #######
02:00:00   18 ##############
02:01:00   16 ############
02:02:00   24 ##################
02:03:00   12 #########
02:04:00   19 ##############
02:05:00   23 #################
02:06:00   18 ##############
02:07:00   27 #####################
02:08:00   28 #####################
02:09:00   30 #######################
02:10:00   26 ####################
02:11:00   37 ############################
02:12:00   25 ###################
02:13:00   34 ##########################
02:14:00   29 ######################
02:15:00   28 #####################
02:16:00   28 #####################
02:17:00   34 ##########################
02:18:00   36 ###########################
02:19:00   31 ########################
02:20:00   29 ######################
02:21:00   27 #####################
02:22:00   26 ####################
02:23:00   23 #################
02:24:00   22 #################
02:25:00   27 #####################
02:26:00   22 #################
02:27:00   18 ##############
02:28:00   15 ###########
02:29:00   12 #########
02:30:00   21 ################
02:31:00   12 #########
02:32:00   22 #################
02:33:00   28 #####################
02:34:00   23 #################
02:35:00   13 ##########
02:36:00   19 ##############
02:37:00   16 ############
02:38:00   22 #################
02:39:00   19 ##############
02:40:00   18 ##############
02:41:00   37 ############################
02:42:00   47 ####################################
02:43:00   42 ################################
02:44:00   27 #####################
02:45:00   47 ####################################
02:46:00   22 #################
02:47:00   28 #####################
02:48:00   35 ###########################
02:49:00   25 ###################
02:50:00   28 #####################
02:51:00   34 ##########################
02:52:00   23 #################
02:53:00   22 #################
02:54:00   38 #############################
02:55:00   32 ########################
02:56:00   23 #################
02:57:00   30 #######################
02:58:00   14 ###########
02:59:00   22 #################
03:00:00   24 ##################
03:01:00   12 #########
03:02:00   13 ##########
03:03:00   22 #################
03:04:00   18 ##############
03:05:00   16 ############
03:06:00   16 ############
03:07:00   14 ###########
03:08:00   16 ############
03:09:00   18 ##############
03:10:00   18 ##############
03:11:00   27 #####################
03:12:00   29 ######################
03:13:00   27 #####################
03:14:00   15 ###########
03:15:00   25 ###################
03:16:00   18 ##############
03:17:00   26 ####################
03:18:00   20 ###############
03:19:00   21 ################
03:20:00   20 ###############
03:21:00   20 ###############
03:22:00   14 ###########
03:23:00   20 ###############
03:24:00   25 ###################
03:25:00   16 ############
03:26:00   16 ############
03:27:00   14 ###########
03:28:00   10 ########
03:29:00   17 #############
03:30:00    8 ######
```

## Top 25 burst buckets

| bucket | count | top services | top types |
|---|---|---|---|
| 01:45:00 | 79 | subscriber-service(12), api-gateway(9), order-service(8), mobile-bff(8) | http_5xx(17), timeout(17), latency_high(12), thread_pool(8) |
| 01:49:00 | 70 | subscriber-service(15), mobile-bff(9), api-gateway(8), charging-service(6) | latency_high(16), timeout(14), http_5xx(12), thread_pool(12) |
| 01:47:00 | 69 | api-gateway(11), order-service(10), billing-service(8), subscriber-service(8) | latency_high(18), http_5xx(13), timeout(12), thread_pool(8) |
| 01:48:00 | 68 | api-gateway(10), mobile-bff(10), subscriber-service(9), charging-service(7) | timeout(17), thread_pool(16), latency_high(12), http_5xx(8) |
| 01:46:00 | 66 | api-gateway(10), subscriber-service(9), mobile-bff(8), order-service(7) | http_5xx(17), thread_pool(15), latency_high(13), timeout(12) |
| 01:50:00 | 48 | api-gateway(8), subscriber-service(5), order-service(5), mobile-bff(4) | timeout(11), latency_high(11), thread_pool(9), http_5xx(5) |
| 01:43:00 | 47 | auth-service(6), api-gateway(6), report-batch(5), subscriber-service(5) | pkt_loss(10), network_flap(7), network_down(5), latency_high(5) |
| 02:45:00 | 47 | mobile-bff(9), order-service(5), payment-service(5), auth-service(5) | latency_high(8), cert_expiry(7), timeout(7), txn_fail(6) |
| 02:42:00 | 47 | payment-provider-gw(10), payment-service(6), mobile-bff(6), auth-service(5) | timeout(7), ntp_drift(6), latency_high(6), ext_slow(5) |
| 02:43:00 | 42 | payment-service(7), mobile-bff(6), session-service(5), payment-provider-gw(5) | timeout(7), txn_fail(7), backup_warn(6), mem_high(3) |
| 01:44:00 | 40 | message-queue(5), dns-resolver(5), session-service(4), charging-service(4) | timeout(6), pkt_loss(5), mem_high(5), network_flap(4) |
| 02:54:00 | 38 | mobile-bff(9), payment-service(5), order-service(4), auth-service(3) | timeout(7), latency_high(6), txn_fail(5), http_5xx(5) |
| 02:41:00 | 37 | payment-provider-gw(8), mobile-bff(6), order-service(4), payment-service(4) | mem_high(5), ext_unreach(4), timeout(4), txn_fail(4) |
| 01:53:00 | 37 | session-service(6), mobile-bff(5), api-gateway(5), auth-service(3) | timeout(6), mem_high(6), latency_high(5), disk_warn(3) |
| 02:11:00 | 37 | billing-service(6), session-service(5), charging-service(4), payment-service(4) | txn_fail(6), latency_high(6), network_flap(4), http_5xx(4) |
| 01:51:00 | 37 | mobile-bff(7), api-gateway(6), subscriber-service(6), subscriber-db(3) | http_5xx(13), timeout(6), cpu_high(3), latency_high(3) |
| 02:18:00 | 36 | payment-service(5), charging-service(5), billing-service(4), order-service(3) | network_flap(8), txn_fail(5), latency_high(5), cpu_high(3) |
| 02:48:00 | 35 | mobile-bff(9), payment-service(8), order-service(4), auth-service(4) | txn_fail(10), timeout(7), latency_high(4), cert_expiry(4) |
| 02:51:00 | 34 | payment-service(6), order-service(5), mobile-bff(4), web-bff(3) | timeout(9), http_5xx(5), latency_high(4), ntp_drift(3) |
| 02:17:00 | 34 | charging-service(7), billing-service(6), payment-service(4), message-queue(3) | latency_high(6), timeout(4), txn_fail(4), http_5xx(4) |
| 02:13:00 | 34 | billing-service(5), charging-service(5), payment-service(4), session-service(3) | txn_fail(5), latency_high(4), network_flap(4), mem_high(4) |
| 02:55:00 | 32 | payment-service(4), api-gateway(4), order-service(4), mobile-bff(4) | txn_fail(6), ntp_drift(5), timeout(4), cert_expiry(3) |
| 01:52:00 | 31 | mobile-bff(5), subscriber-service(4), api-gateway(3), dns-resolver(3) | http_5xx(7), timeout(6), thread_pool(5), latency_high(4) |
| 01:42:00 | 31 | subscriber-db(5), auth-service(4), charging-service(3), order-service(3) | network_flap(13), pkt_loss(5), network_down(3), disk_warn(3) |
| 02:19:00 | 31 | payment-service(4), invoice-batch(3), charging-service(3), load-balancer(3) | latency_high(8), log_rotate(4), txn_fail(3), disk_warn(3) |

## Per-service burst profile

| service | alarms | max_sev | max/bucket | peak_at | span | top types |
|---|---|---|---|---|---|---|
| subscriber-service | 212 | 5 | 15 | 01:49:00 | 0 days 01:58:53 | latency_high, cpu_high, http_5xx |
| api-gateway | 159 | 5 | 11 | 01:47:00 | 0 days 01:56:36 | latency_high, timeout, ntp_drift |
| mobile-bff | 278 | 5 | 10 | 01:48:00 | 0 days 01:58:53 | timeout, latency_high, http_5xx |
| order-service | 199 | 5 | 10 | 01:47:00 | 0 days 01:58:32 | timeout, txn_fail, latency_high |
| payment-provider-gw | 113 | 5 | 10 | 02:42:00 | 0 days 01:56:58 | mem_high, network_flap, ext_slow |
| billing-db | 113 | 5 | 8 | 02:07:00 | 0 days 01:57:03 | disk_full, disk_warn, cert_expiry |
| billing-service | 188 | 5 | 8 | 01:47:00 | 0 days 01:57:14 | http_5xx, db_conn_pool, txn_fail |
| payment-service | 227 | 5 | 8 | 02:44:00 | 0 days 01:55:39 | timeout, txn_fail, latency_high |
| charging-service | 205 | 5 | 7 | 01:48:00 | 0 days 01:56:49 | latency_high, timeout, cpu_high |
| session-service | 150 | 5 | 7 | 01:35:00 | 0 days 01:59:50 | mem_high, gc_pressure, network_flap |
| auth-service | 121 | 5 | 6 | 01:43:00 | 0 days 01:56:04 | latency_high, timeout, ntp_drift |
| subscriber-db | 172 | 5 | 6 | 03:12:00 | 0 days 01:58:50 | latency_high, cpu_high, db_conn_pool |
| dns-resolver | 95 | 5 | 5 | 01:44:00 | 0 days 01:59:19 | cert_expiry, latency_high, backup_warn |
| message-queue | 86 | 5 | 5 | 01:44:00 | 0 days 01:56:36 | cpu_high, log_rotate, cert_expiry |
| report-batch | 78 | 5 | 5 | 01:43:00 | 0 days 01:57:14 | latency_high, cpu_high, network_flap |
| batch-scheduler | 30 | 4 | 4 | 03:06:00 | 0 days 01:49:43 | cert_expiry, network_flap, batch_overlap |
| reconciliation-batch | 53 | 4 | 4 | 03:13:00 | 0 days 01:52:27 | cpu_high, batch_slow, db_conn_pool |
| web-bff | 96 | 4 | 4 | 01:45:00 | 0 days 01:57:21 | latency_high, timeout, mem_high |
| cache-cluster | 62 | 4 | 3 | 02:08:00 | 0 days 01:52:01 | latency_high, ntp_drift, network_flap |
| invoice-batch | 56 | 5 | 3 | 02:11:00 | 0 days 01:42:33 | http_5xx, db_write_fail, backup_warn |
| load-balancer | 99 | 4 | 3 | 02:19:00 | 0 days 01:59:00 | cert_expiry, backup_warn, log_rotate |
| notification-service | 50 | 4 | 3 | 01:46:00 | 0 days 01:50:13 | latency_high, backup_warn, log_rotate |
| catalog-service | 31 | 4 | 2 | 01:38:00 | 0 days 01:52:46 | mem_high, log_rotate, latency_high |
| kyc-provider-gw | 38 | 3 | 2 | 02:18:00 | 0 days 01:53:16 | cpu_high, disk_warn, mem_high |
| ntp-service | 25 | 4 | 2 | 02:13:00 | 0 days 01:56:13 | log_rotate, mem_high, network_flap |
| object-store | 34 | 4 | 2 | 01:54:00 | 0 days 01:46:55 | network_flap, mem_high, cpu_high |
| sms-gateway | 30 | 4 | 2 | 02:13:00 | 0 days 01:57:43 | disk_warn, log_rotate, cpu_high |

## Message templates per alarm_type

| alarm_type | count | distinct_templates | dominant_template | sample messages |
|---|---|---|---|---|
| latency_high | 402 | 1 | Yanit suresi p99 esigi asti, <N> ms | Yanit suresi p99 esigi asti, 88 ms || Yanit suresi p99 esigi asti, 44 ms |
| timeout | 271 | 12 | payment-provider-gw servisine yapilan cagri zaman asimina ugradi (<N> ms) | charging-service servisine yapilan cagri zaman asimina ugradi (71 ms) || auth-service servisine yapilan cagri zaman asimina ugradi (70 ms) |
| mem_high | 240 | 1 | Bellek kullanimi yuzde <N> seviyesinde | Bellek kullanimi yuzde 38 seviyesinde || Bellek kullanimi yuzde 52 seviyesinde |
| cpu_high | 230 | 1 | CPU kullanimi yuzde <N> | CPU kullanimi yuzde 66 || CPU kullanimi yuzde 55 |
| cert_expiry | 220 | 1 | Sertifika <N> gun icinde suresi dolacak | Sertifika 26 gun icinde suresi dolacak || Sertifika 49 gun icinde suresi dolacak |
| network_flap | 202 | 4 | Arayuz eth1 link durumu <N> kez degisti | Arayuz ens192 link durumu 50 kez degisti || Arayuz eth0 link durumu 59 kez degisti |
| http_5xx | 198 | 1 | HTTP 5xx hata orani esigi asti, oran yuzde <N> | HTTP 5xx hata orani esigi asti, oran yuzde 84 || HTTP 5xx hata orani esigi asti, oran yuzde 96 |
| log_rotate | 196 | 1 | Log rotasyonu beklenenden uzun surdu, <N> saniye | Log rotasyonu beklenenden uzun surdu, 76 saniye || Log rotasyonu beklenenden uzun surdu, 88 saniye |
| ntp_drift | 193 | 1 | Saat sapmasi <N> ms | Saat sapmasi 22 ms || Saat sapmasi 28 ms |
| disk_warn | 189 | 1 | Disk kullanimi uyari seviyesinde, yuzde <N> dolu | Disk kullanimi uyari seviyesinde, yuzde 29 dolu || Disk kullanimi uyari seviyesinde, yuzde 71 dolu |
| backup_warn | 177 | 1 | Yedekleme isi <N> dakika gecikmeli tamamlandi | Yedekleme isi 81 dakika gecikmeli tamamlandi || Yedekleme isi 67 dakika gecikmeli tamamlandi |
| txn_fail | 148 | 1 | Islem basarisiz, hata orani yuzde <N> | Islem basarisiz, hata orani yuzde 92 || Islem basarisiz, hata orani yuzde 74 |
| thread_pool | 79 | 1 | Is parcacigi havuzu doluluk orani yuzde <N> | Is parcacigi havuzu doluluk orani yuzde 75 || Is parcacigi havuzu doluluk orani yuzde 80 |
| db_conn_pool | 72 | 1 | Baglanti havuzu tukendi, bekleyen istek sayisi <N> | Baglanti havuzu tukendi, bekleyen istek sayisi 85 || Baglanti havuzu tukendi, bekleyen istek sayisi 80 |
| db_write_fail | 34 | 1 | Veritabani yazma islemi basarisiz, tablespace genisletilemedi | Veritabani yazma islemi basarisiz, tablespace genisletilemedi || Veritabani yazma islemi basarisiz, tablespace genisletilemedi |
| conn_refused | 28 | 9 | dns-resolver baglantisi reddedildi, hedef erisilemiyor | subscriber-service baglantisi reddedildi, hedef erisilemiyor || auth-service baglantisi reddedildi, hedef erisilemiyor |
| pkt_loss | 22 | 1 | Paket kaybi tespit edildi, oran yuzde <N> | Paket kaybi tespit edildi, oran yuzde 84 || Paket kaybi tespit edildi, oran yuzde 72 |
| gc_pressure | 18 | 1 | GC duraklama suresi <N> ms, esik asildi | GC duraklama suresi 76 ms, esik asildi || GC duraklama suresi 76 ms, esik asildi |
| disk_full | 17 | 1 | Disk kullanimi kritik seviyede, yuzde <N> dolu | Disk kullanimi kritik seviyede, yuzde 100 dolu || Disk kullanimi kritik seviyede, yuzde 100 dolu |
| ext_slow | 13 | 1 | Dis servis payment-provider-gw yanit suresi <N> ms | Dis servis payment-provider-gw yanit suresi 503 ms || Dis servis payment-provider-gw yanit suresi 504 ms |
| batch_slow | 12 | 1 | Toplu is calisma suresi <N> dakikaya ulasti | Toplu is calisma suresi 73 dakikaya ulasti || Toplu is calisma suresi 80 dakikaya ulasti |
| network_down | 12 | 4 | Arayuz eth1 baglantisi koptu, link durumu DOWN | Arayuz ens192 baglantisi koptu, link durumu DOWN || Arayuz bond0 baglantisi koptu, link durumu DOWN |
| oom_risk | 12 | 1 | Heap kullanimi kritik, OutOfMemory riski | Heap kullanimi kritik, OutOfMemory riski || Heap kullanimi kritik, OutOfMemory riski |
| ext_unreach | 11 | 1 | Dis servis payment-provider-gw erisilemiyor, HTTP <N> | Dis servis payment-provider-gw erisilemiyor, HTTP 504 || Dis servis payment-provider-gw erisilemiyor, HTTP 504 |
| batch_overlap | 4 | 1 | Toplu is penceresi cakismasi tespit edildi | Toplu is penceresi cakismasi tespit edildi || Toplu is penceresi cakismasi tespit edildi |

## alarm_type x severity

| alarm_type | sev1 | sev2 | sev3 | sev4 | sev5 |
|---|---|---|---|---|---|
| backup_warn | 52 | 71 | 40 | 14 | 0 |
| batch_overlap | 0 | 0 | 0 | 4 | 0 |
| batch_slow | 0 | 0 | 8 | 4 | 0 |
| cert_expiry | 93 | 73 | 41 | 13 | 0 |
| conn_refused | 0 | 0 | 7 | 12 | 9 |
| cpu_high | 63 | 79 | 57 | 31 | 0 |
| db_conn_pool | 0 | 0 | 27 | 40 | 5 |
| db_write_fail | 0 | 0 | 0 | 20 | 14 |
| disk_full | 0 | 0 | 0 | 0 | 17 |
| disk_warn | 70 | 71 | 40 | 8 | 0 |
| ext_slow | 0 | 0 | 0 | 0 | 13 |
| ext_unreach | 0 | 0 | 0 | 0 | 11 |
| gc_pressure | 0 | 0 | 9 | 9 | 0 |
| http_5xx | 0 | 0 | 56 | 102 | 40 |
| latency_high | 76 | 79 | 147 | 91 | 9 |
| log_rotate | 65 | 71 | 49 | 11 | 0 |
| mem_high | 74 | 102 | 51 | 13 | 0 |
| network_down | 0 | 0 | 0 | 3 | 9 |
| network_flap | 61 | 73 | 35 | 20 | 13 |
| ntp_drift | 60 | 90 | 31 | 12 | 0 |
| oom_risk | 0 | 0 | 0 | 3 | 9 |
| pkt_loss | 0 | 0 | 0 | 6 | 16 |
| thread_pool | 0 | 0 | 53 | 26 | 0 |
| timeout | 0 | 0 | 135 | 105 | 31 |
| txn_fail | 0 | 0 | 14 | 82 | 52 |

## Dependency graph summary

- edges: 32; kaynak services: 15; hedef services: 20
- services with alarms but absent from dep graph as kaynak: ['batch-scheduler', 'billing-db', 'cache-cluster', 'dns-resolver', 'kyc-provider-gw', 'load-balancer', 'message-queue', 'ntp-service', 'object-store', 'payment-provider-gw', 'sms-gateway', 'subscriber-db']
- services with alarms but absent as hedef: ['invoice-batch', 'mobile-bff', 'notification-service', 'ntp-service', 'reconciliation-batch', 'report-batch', 'web-bff']
| service | depended_on_by (in-deg) | depends_on (out-deg) |
|---|---|---|
| api-gateway | 2 | 3 |
| auth-service | 1 | 2 |
| batch-scheduler | 3 | 0 |
| billing-db | 2 | 0 |
| billing-service | 1 | 2 |
| cache-cluster | 2 | 0 |
| catalog-service | 1 | 1 |
| charging-service | 1 | 1 |
| dns-resolver | 2 | 0 |
| invoice-batch | 0 | 2 |
| kyc-provider-gw | 1 | 0 |
| load-balancer | 1 | 0 |
| message-queue | 2 | 0 |
| mobile-bff | 0 | 3 |
| notification-service | 0 | 2 |
| ntp-service | 0 | 0 |
| object-store | 1 | 0 |
| order-service | 1 | 4 |
| payment-provider-gw | 1 | 0 |
| payment-service | 1 | 2 |
| reconciliation-batch | 0 | 2 |
| report-batch | 0 | 2 |
| session-service | 3 | 1 |
| sms-gateway | 1 | 0 |
| subscriber-db | 3 | 0 |
| subscriber-service | 2 | 3 |
| web-bff | 0 | 2 |

```
       kaynak_servis        hedef_servis bagimlilik_tipi kritiklik
         api-gateway        auth-service         senkron    kritik
         api-gateway       load-balancer         senkron    kritik
          mobile-bff         api-gateway         senkron    kritik
             web-bff         api-gateway         senkron    kritik
          mobile-bff     session-service         senkron    kritik
             web-bff     session-service         senkron    kritik
        auth-service     session-service         senkron    kritik
     session-service       cache-cluster         senkron    yuksek
  subscriber-service       subscriber-db         senkron    kritik
  subscriber-service       cache-cluster         senkron    yuksek
     billing-service          billing-db         senkron    kritik
     billing-service    charging-service         senkron    kritik
    charging-service  subscriber-service         senkron    kritik
     payment-service payment-provider-gw         senkron    kritik
     payment-service     billing-service         senkron    kritik
       order-service     payment-service         senkron    kritik
       order-service     catalog-service         senkron      orta
       order-service  subscriber-service         senkron    kritik
          mobile-bff       order-service         senkron    yuksek
notification-service         sms-gateway        asenkron      orta
notification-service       message-queue        asenkron    yuksek
       order-service       message-queue        asenkron    yuksek
       invoice-batch          billing-db         senkron    kritik
       invoice-batch     batch-scheduler        asenkron      orta
reconciliation-batch     batch-scheduler        asenkron      orta
reconciliation-batch       subscriber-db         senkron    kritik
        report-batch     batch-scheduler        asenkron      orta
        report-batch       subscriber-db         senkron    kritik
        auth-service     kyc-provider-gw        asenkron     dusuk
     catalog-service        object-store         senkron      orta
         api-gateway        dns-resolver         senkron    yuksek
  subscriber-service        dns-resolver         senkron    yuksek
```

## Host inventory summary

| dc | rack | hosts | top services on hosts |
|---|---|---|---|
| dc1 | rack-A | 9 | api-gateway, auth-service, subscriber-service, charging-service, order-service |
| dc1 | rack-B | 10 | api-gateway, web-bff, session-service, billing-service, payment-service |
| dc1 | rack-C | 9 | mobile-bff, auth-service, subscriber-service, charging-service, catalog-service |
| dc2 | rack-A | 9 | mobile-bff, session-service, billing-service, payment-service, notification-service |
| dc2 | rack-B | 9 | mobile-bff, auth-service, subscriber-service, charging-service, order-service |
| dc2 | rack-C | 10 | api-gateway, web-bff, session-service, billing-service, payment-service |

```
                 host               servis veri_merkezi  kabin ortam is_kritikligi
           ao-001-api          api-gateway          dc1 rack-B  prod        kritik
           ao-002-api          api-gateway          dc2 rack-C  prod        kritik
           ao-003-api          api-gateway          dc1 rack-A  prod        kritik
        ao-004-mobile           mobile-bff          dc2 rack-B  prod        kritik
        ao-005-mobile           mobile-bff          dc1 rack-C  prod        kritik
        ao-006-mobile           mobile-bff          dc2 rack-A  prod        kritik
           ao-007-web              web-bff          dc1 rack-B  prod        yuksek
           ao-008-web              web-bff          dc2 rack-C  prod        yuksek
          ao-009-auth         auth-service          dc1 rack-A  prod        kritik
          ao-010-auth         auth-service          dc2 rack-B  prod        kritik
          ao-011-auth         auth-service          dc1 rack-C  prod        kritik
       ao-012-session      session-service          dc2 rack-A  prod        kritik
       ao-013-session      session-service          dc1 rack-B  prod        kritik
       ao-014-session      session-service          dc2 rack-C  prod        kritik
    ao-015-subscriber   subscriber-service          dc1 rack-A  prod        kritik
    ao-016-subscriber   subscriber-service          dc2 rack-B  prod        kritik
    ao-017-subscriber   subscriber-service          dc1 rack-C  prod        kritik
       ao-018-billing      billing-service          dc2 rack-A  prod        kritik
       ao-019-billing      billing-service          dc1 rack-B  prod        kritik
       ao-020-billing      billing-service          dc2 rack-C  prod        kritik
      ao-021-charging     charging-service          dc1 rack-A  prod        kritik
      ao-022-charging     charging-service          dc2 rack-B  prod        kritik
      ao-023-charging     charging-service          dc1 rack-C  prod        kritik
       ao-024-payment      payment-service          dc2 rack-A  prod        kritik
       ao-025-payment      payment-service          dc1 rack-B  prod        kritik
       ao-026-payment      payment-service          dc2 rack-C  prod        kritik
         ao-027-order        order-service          dc1 rack-A  prod        yuksek
         ao-028-order        order-service          dc2 rack-B  prod        yuksek
       ao-029-catalog      catalog-service          dc1 rack-C  prod          orta
  ao-030-notification notification-service          dc2 rack-A  prod          orta
    ao-031-subscriber        subscriber-db          dc1 rack-B  prod        kritik
    ao-032-subscriber        subscriber-db          dc2 rack-C  prod        kritik
    ao-033-subscriber        subscriber-db          dc1 rack-A  prod        kritik
       ao-034-billing           billing-db          dc2 rack-B  prod        kritik
       ao-035-billing           billing-db          dc1 rack-C  prod        kritik
       ao-036-billing           billing-db          dc2 rack-A  prod        kritik
         ao-037-cache        cache-cluster          dc1 rack-B  prod        yuksek
         ao-038-cache        cache-cluster          dc2 rack-C  prod        yuksek
       ao-039-message        message-queue          dc1 rack-A  prod        yuksek
       ao-040-message        message-queue          dc2 rack-B  prod        yuksek
        ao-041-object         object-store          dc1 rack-C  prod          orta
          ao-042-load        load-balancer          dc2 rack-A  prod        kritik
          ao-043-load        load-balancer          dc1 rack-B  prod        kritik
          ao-044-load        load-balancer          dc2 rack-C  prod        kritik
           ao-045-dns         dns-resolver          dc1 rack-A  prod        yuksek
           ao-046-dns         dns-resolver          dc2 rack-B  prod        yuksek
           ao-047-ntp          ntp-service          dc1 rack-C  prod         dusuk
         ao-048-batch      batch-scheduler          dc2 rack-A  prod          orta
       ao-049-invoice        invoice-batch          dc1 rack-B  prod          orta
ao-050-reconciliation reconciliation-batch          dc2 rack-C  prod         dusuk
        ao-051-report         report-batch          dc1 rack-A  prod         dusuk
       ao-052-payment  payment-provider-gw          dc2 rack-B  prod        kritik
       ao-053-payment  payment-provider-gw          dc1 rack-C  prod        kritik
       ao-054-payment  payment-provider-gw          dc2 rack-A  prod        kritik
           ao-055-sms          sms-gateway          dc1 rack-B  prod          orta
           ao-056-kyc      kyc-provider-gw          dc2 rack-C  prod         dusuk
```

## Host coverage cross-check

- hosts in alarms: 56; in inventory: 56
- alarms hosts missing from inventory: []
- inventory hosts with zero alarms: []
- alarm-tag vs inventory dc mismatches: 0

## Rack x 5-minute locality

| 5min | dc | rack | alarms |
|---|---|---|---|
| 01:45 | dc1 | rack-A | 132 |
| 01:40 | dc1 | rack-A | 84 |
| 01:45 | dc2 | rack-B | 53 |
| 01:45 | dc2 | rack-C | 49 |
| 01:50 | dc1 | rack-A | 47 |
| 01:45 | dc1 | rack-C | 44 |
| 02:40 | dc2 | rack-B | 39 |
| 01:45 | dc2 | rack-A | 37 |
| 02:10 | dc1 | rack-B | 37 |
| 02:45 | dc2 | rack-A | 37 |
| 01:45 | dc1 | rack-B | 37 |
| 02:15 | dc1 | rack-B | 35 |
| 01:50 | dc2 | rack-B | 32 |
| 02:50 | dc2 | rack-A | 31 |
| 02:15 | dc1 | rack-A | 30 |
| 02:40 | dc2 | rack-A | 30 |
| 01:50 | dc2 | rack-C | 30 |
| 02:40 | dc1 | rack-C | 30 |
| 02:45 | dc2 | rack-B | 28 |
| 02:50 | dc2 | rack-B | 28 |