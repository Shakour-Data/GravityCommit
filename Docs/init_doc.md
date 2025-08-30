

### طراحی پکیج خودکار کامیت در پایتون (بدون کد)

#### 1. مراحل کلی عملکرد پکیج
```mermaid
graph TD
    A[نصب پکیج توسط کاربر] --> B[اجرای دستور setup برای پروژه]
    B --> C[ایجاد فایل تنظیمات در ریشه پروژه]
    C --> D[نصب سرویس سیستم‌عامل]
    D --> E[فعال‌سازی خودکار با باز شدن پروژه]
    E --> F[بررسی تغییرات در بازه زمانی]
    F --> G{تغییرات وجود دارد؟}
    G -->|بله| H[تولید پیام حرفه‌ای]
    G -->|خیر| F
    H --> I[انجام کامیت]
    I --> F
```

#### 2. کامپوننت‌های اصلی پکیج
```mermaid
graph LR
    A[مدیریت پیکربندی] --> B[ذخیره تنظیمات کاربر]
    C[تولیدکننده پیام] --> D[تحلیل تغییرات فایل‌ها]
    E[عملیات گیت] --> F[مدیریت کامیت‌ها]
    G[زمان‌بند] --> H[کنترل بازه زمانی]
    I[مدیریت سرویس] --> J[نصب/حذف سرویس سیستمی]
    K[تشخیص باز بودن پروژه] --> L[مانیتورینگ فرآیندهای ویرایشگر]
```

#### 3. دیاگرام کلاس‌ها (UML)
```mermaid
classDiagram
    class ConfigManager {
        +set_interval(interval)
        +get_interval()
        +remove_config()
    }
    
    class CommitGenerator {
        +generate_commit()
        +analyze_changes()
        +create_message()
    }
    
    class GitOperations {
        +stage_changes()
        +commit(message)
        +check_status()
    }
    
    class Scheduler {
        +start()
        +stop()
        +set_interval()
    }
    
    class DaemonManager {
        +install_service()
        +uninstall_service()
        +is_running()
    }
    
    class ProjectMonitor {
        +is_project_open()
        +get_editor_processes()
    }
    
    ConfigManager --> CommitGenerator
    CommitGenerator --> GitOperations
    Scheduler --> GitOperations
    DaemonManager --> Scheduler
    ProjectMonitor --> Scheduler
```

#### 4. فرآیند نصب و راه‌اندازی
```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant ConfigManager
    participant DaemonManager
    participant System
    
    User->>CLI: autocommit setup /path/to/project --interval 15
    CLI->>ConfigManager: ایجاد فایل تنظیمات
    ConfigManager-->>CLI: تنظیمات ذخیره شد
    CLI->>DaemonManager: درخواست نصب سرویس
    DaemonManager->>System: نصب سرویس سیستمی
    System-->>DaemonManager: سرویس نصب شد
    DaemonManager-->>CLI: موفقیت‌آمیز
    CLI-->>User: پیام تأیید
```

#### 5. فرآیند اجرای خودکار کامیت
```mermaid
sequenceDiagram
    participant Daemon
    participant ProjectMonitor
    participant GitOperations
    participant CommitGenerator
    
    loop هر 10 دقیقه
        Daemon->>ProjectMonitor: پروژه باز است؟
        alt پروژه باز است
            ProjectMonitor-->>Daemon: بله
            Daemon->>GitOperations: بررسی تغییرات
            GitOperations-->>Daemon: لیست تغییرات
            Daemon->>CommitGenerator: تولید پیام
            CommitGenerator-->>Daemon: پیام حرفه‌ای
            Daemon->>GitOperations: انجام کامیت
            GitOperations-->>Daemon: کامیت موفق
        else پروژه بسته است
            ProjectMonitor-->>Daemon: خیر
        end
    end
```

#### 6. معماری پکیج
```mermaid
graph TB
    subgraph لایه کاربر
        A[دستورات CLI]
    end
    
    subgraph لایه منطق کسب‌وکار
        B[مدیریت پیکربندی]
        C[تولید پیام کامیت]
        D[عملیات گیت]
        E[زمان‌بندی]
    end
    
    subgraph لایه سرویس
        F[مدیریت سرویس لینوکس]
        G[مدیریت سرویس ویندوز]
    end
    
    subgraph لایه سیستمی
        H[systemd]
        I[Windows Service]
        J[پایش فرآیندها]
    end
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    E --> G
    F --> H
    G --> I
    E --> J
```

#### 7. دیاگرام حالت‌های سیستم
```mermaid
stateDiagram-v2
    [*] --> نصب_نشده
    نصب_نشده --> در_حال_نصب: اجرای دستور setup
    در_حال_نصب --> آماده_به_کار: نصب موفق
    آماده_به_کار --> فعال: باز شدن پروژه
    فعال --> غیرفعال: بسته شدن پروژه
    غیرفعال --> فعال: باز شدن مجدد پروژه
    فعال --> کامیت_در_حال_انجام: رسیدن زمان کامیت
    کامیت_در_حال_انجام --> فعال: اتمام کامیت
    آماده_به_کار --> حذف_شده: اجرای دستور remove
    حذف_شده --> [*]
```

#### 8. جریان داده‌ها
```mermaid
graph LR
    A[تنظیمات کاربر] --> B(فایل .autocommit)
    B --> C[مدیریت پیکربندی]
    C --> D[زمان‌بند]
    D --> E[پایش تغییرات]
    E --> F[تحلیل فایل‌ها]
    F --> G[تولید پیام]
    G --> H[انجام کامیت]
    H --> I[لاگ‌های سیستمی]
```

#### 9. ماتریس قابلیت‌ها بر اساس پلتفرم
| قابلیت                  | لینوکس                 | ویندوز               |
|-------------------------|------------------------|----------------------|
| نصب سرویس               | systemd                | Windows Service      |
| تشخیص باز بودن پروژه    | بررسی فرآیندها         | بررسی فرآیندها       |
| زمان‌بندی               | schedule + sleep       | schedule + sleep     |
| مدیریت پیکربندی         | فایل متنی در پروژه     | فایل متنی در پروژه   |
| لاگ‌ینگ                 | syslog                 | Event Log            |
| دسترسی به سیستم         | نیاز به sudo           | نیاز به دسترسی ادمین |

#### 10. فرآیند تولید پیام حرفه‌ای
```mermaid
graph TD
    A[دریافت تغییرات] --> B[تفکیک نوع تغییر]
    B --> C{نوع تغییر}
    C -->|اضافه شدن| D[الگوهای افزودن]
    C -->|تغییر یافته| E[الگوهای ویرایش]
    C -->|حذف شده| F[الگوهای حذف]
    D --> G[تشخیص نوع فایل]
    E --> G
    F --> G
    G --> H[انتخاب الگوی مناسب]
    H --> I[تولید پیام نهایی]
```

#### 11. مدیریت چرخه حیات سرویس
```mermaid
graph LR
    A[نصب سرویس] --> B[شروع خودکار با بوت]
    B --> C[مانیتورینگ پروژه]
    C --> D{پروژه باز؟}
    D -->|بله| E[فعال‌سازی زمان‌بند]
    D -->|خیر| F[توقف موقت]
    E --> G[انجام کامیت‌ها]
    F --> C
    G --> H[توقف سرویس]
    H --> I[حذف سرویس]
```

#### 12. دیاگرام استقرار
```mermaid
graph TB
    subgraph محیط توسعه
        A[پروژه کاربر]
        B[فایل .autocommit]
    end
    
    subgraph لایه میانی
        C[پکیج autocommit]
        D[پکیج‌های وابسته]
    end
    
    subgraph لایه سیستمی
        E[systemd/Windows Service]
        F[پایش فرآیندها]
    end
    
    subgraph لایه گیت
        G[مخزن محلی]
        H[کامیت‌های خودکار]
    end
    
    A --> C
    B --> C
    C --> D
    C --> E
    E --> F
    F --> A
    C --> G
    G --> H
```

