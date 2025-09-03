-- نظام متكامل للبيانات التونسية مع التحقق من الجودة
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "postgis";

-- جدول المستخدمين مع التحقق الشامل
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cin VARCHAR(8) UNIQUE NOT NULL CHECK (cin ~ '^[0-9]{8}$'),
    first_name VARCHAR(50) NOT NULL CHECK (length(first_name) >= 2),
    last_name VARCHAR(50) NOT NULL CHECK (length(last_name) >= 2),
    email VARCHAR(100) UNIQUE NOT NULL CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    phone VARCHAR(15) UNIQUE NOT NULL CHECK (phone ~ '^\+216[0-9]{8}$'),
    governorate VARCHAR(30) NOT NULL REFERENCES tunisian_governorates(name),
    delegation VARCHAR(50) NOT NULL,
    birth_date DATE NOT NULL CHECK (birth_date <= CURRENT_DATE - INTERVAL '18 years' AND birth_date >= CURRENT_DATE - INTERVAL '70 years'),
    education_level VARCHAR(50) NOT NULL CHECK (education_level IN ('ابتدائي', 'ثانوي', 'شهادة تقنية', 'ليسانس', 'ماجستير', 'دكتوراه')),
    languages JSONB NOT NULL DEFAULT '["العربية"]' CHECK (jsonb_array_length(languages) >= 1),
    skills JSONB NOT NULL DEFAULT '[]',
    work_experience JSONB NOT NULL DEFAULT '[]',
    verification_status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (verification_status IN ('pending', 'verified', 'rejected', 'under_review')),
    risk_score INTEGER NOT NULL DEFAULT 0 CHECK (risk_score >= 0 AND risk_score <= 100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_login TIMESTAMPTZ,
    profile_completion_percentage INTEGER NOT NULL DEFAULT 0 CHECK (profile_completion_percentage >= 0 AND profile_completion_percentage <= 100),

    -- فهارس متقدمة للبحث السريع
    CONSTRAINT valid_cin CHECK (cin ~ '^[0-9]{8}$')
);

-- جدول المحافظات التونسية
CREATE TABLE tunisian_governorates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(30) UNIQUE NOT NULL,
    code VARCHAR(5) UNIQUE NOT NULL,
    population INTEGER,
    area_km2 DECIMAL(10, 2),
    geographic_center GEOMETRY(POINT, 4326)
);

-- جدول الشركات مع نظام التقييم المتقدم
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    rne_number VARCHAR(20) UNIQUE CHECK (rne_number ~ '^[A-Z0-9]{1,20}$'),
    name VARCHAR(200) NOT NULL,
    legal_form VARCHAR(50) NOT NULL CHECK (legal_form IN ('SARL', 'SA', 'SUARL', 'SNC', 'SCS', 'EURL', 'GIE')),
    address TEXT NOT NULL,
    governorate VARCHAR(30) NOT NULL REFERENCES tunisian_governorates(name),
    activity_code VARCHAR(10) CHECK (activity_code ~ '^[0-9]{4,5}[A-Z]?$'),
    cnss_number VARCHAR(20) CHECK (cnss_number ~ '^[0-9]{1,20}$'),
    cnss_registered BOOLEAN NOT NULL DEFAULT FALSE,
    cnss_employees_count INTEGER CHECK (cnss_employees_count >= 0),
    verification_status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (verification_status IN ('pending', 'verified', 'rejected', 'suspended')),
    risk_score INTEGER NOT NULL DEFAULT 50 CHECK (risk_score >= 0 AND risk_score <= 100),
    fraud_reports_count INTEGER NOT NULL DEFAULT 0 CHECK (fraud_reports_count >= 0),
    trust_score INTEGER NOT NULL DEFAULT 50 CHECK (trust_score >= 0 AND trust_score <= 100),
    last_verified TIMESTAMPTZ,
    verified_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- فهارس متقدمة
    EXCLUDE USING gist (rne_number WITH =) WHERE (verification_status = 'verified')
);

-- نظام التتبع والمراجعة الشامل
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_name VARCHAR(50) NOT NULL,
    record_id UUID NOT NULL,
    action VARCHAR(20) NOT NULL CHECK (action IN ('INSERT', 'UPDATE', 'DELETE')),
    old_data JSONB,
    new_data JSONB,
    changed_fields TEXT[],
    performed_by UUID REFERENCES users(id),
    performed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    user_ip INET,
    user_agent TEXT
);

-- نظام الإسكرو المتقدم مع التتبع الكامل
CREATE TABLE escrow_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    company_id UUID NOT NULL REFERENCES companies(id),
    amount DECIMAL(12, 3) NOT NULL CHECK (amount > 0),
    currency VARCHAR(3) NOT NULL DEFAULT 'TND' CHECK (currency IN ('TND', 'EUR', 'USD')),
    service_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'created' CHECK (status IN ('created', 'funded', 'held', 'released', 'refunded', 'disputed')),
    d17_transaction_ref VARCHAR(100) UNIQUE,
    release_conditions JSONB NOT NULL DEFAULT '{}',
    conditions_met BOOLEAN NOT NULL DEFAULT FALSE,
    expected_release_date DATE NOT NULL,
    actual_release_date DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- ضمان التكاملية
    CHECK (expected_release_date > created_at::DATE),
    CHECK (actual_release_date IS NULL OR actual_release_date >= created_at::DATE)
);
