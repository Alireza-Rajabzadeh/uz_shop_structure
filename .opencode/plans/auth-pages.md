# Auth Pages - Login & Register

## Files to create

### 1. `client_panel/lib/auth-service.ts`

```typescript
import { apiClient, setTokens, clearTokens } from "@/lib/apiClient";
import type { ApiEnvelope } from "@/lib/types";

export interface LoginPayload {
  phone: string;
  password: string;
}

export interface RegisterPayload {
  first_name: string;
  last_name: string;
  phone: string;
  password: string;
  password_confirmation: string;
  email?: string;
  date_of_birth?: string;
  gender?: "male" | "female" | "other";
}

export interface CustomerProfile {
  id: number;
  customer_code: string;
  first_name: string;
  last_name: string;
  email: string | null;
  phone: string;
  status_title: string;
  date_of_birth: string | null;
  gender: string | null;
  email_verified_at: string | null;
  phone_verified_at: string | null;
  created_at: string;
}

export interface AuthResult {
  access: string;
  refresh: string;
  customer: CustomerProfile;
}

export async function login(payload: LoginPayload): Promise<AuthResult> {
  const res = await apiClient<AuthResult>("/customer/login", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  if (!res.success || !res.data) {
    throw new Error(res.message || "خطا در ورود");
  }
  setTokens(res.data.access, res.data.refresh);
  return res.data;
}

export async function register(payload: RegisterPayload): Promise<AuthResult> {
  const res = await apiClient<AuthResult>("/customer/register", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  if (!res.success || !res.data) {
    const msg = res.errors
      ? Object.values(res.errors).flat().join("\n")
      : res.message || "خطا در ثبت‌نام";
    throw new Error(msg);
  }
  setTokens(res.data.access, res.data.refresh);
  return res.data;
}

export async function getProfile(): Promise<CustomerProfile> {
  const res = await apiClient<CustomerProfile>("/customer/me", {
    method: "GET",
  });
  if (!res.success || !res.data) {
    throw new Error(res.message || "خطا در دریافت پروفایل");
  }
  return res.data;
}

export function logout(): void {
  clearTokens();
  localStorage.removeItem("customer_profile");
}
```

### 2. `client_panel/hooks/useAuth.tsx`

```typescript
"use client";
import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from "react";
import { useRouter } from "next/navigation";
import {
  login as authLogin,
  register as authRegister,
  getProfile,
  logout as authLogout,
  type LoginPayload,
  type RegisterPayload,
  type CustomerProfile,
} from "@/lib/auth-service";
import { getTokens } from "@/lib/apiClient";

interface AuthContextValue {
  user: CustomerProfile | null;
  loading: boolean;
  login: (payload: LoginPayload) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<CustomerProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  // Restore session on mount
  useEffect(() => {
    const tokens = getTokens();
    if (!tokens.access) {
      setLoading(false);
      return;
    }

    const cached = localStorage.getItem("customer_profile");
    if (cached) {
      try {
        setUser(JSON.parse(cached));
      } catch {
        // ignore
      }
    }

    getProfile()
      .then((profile) => {
        setUser(profile);
        localStorage.setItem("customer_profile", JSON.stringify(profile));
      })
      .catch(() => {
        // Token invalid
      })
      .finally(() => setLoading(false));
  }, []);

  const login = useCallback(async (payload: LoginPayload) => {
    const result = await authLogin(payload);
    setUser(result.customer);
    localStorage.setItem("customer_profile", JSON.stringify(result.customer));
  }, []);

  const register = useCallback(async (payload: RegisterPayload) => {
    const result = await authRegister(payload);
    setUser(result.customer);
    localStorage.setItem("customer_profile", JSON.stringify(result.customer));
  }, []);

  const logout = useCallback(() => {
    authLogout();
    setUser(null);
    router.push("/login");
  }, [router]);

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
```

### 3. `client_panel/app/(auth)/layout.tsx`

```typescript
export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-background via-background-secondary to-background p-4">
      <div className="w-full max-w-sm">
        {children}
      </div>
    </div>
  );
}
```

### 4. `client_panel/app/(auth)/login/page.tsx`

```typescript
"use client";
import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import Form from "@/components/form/Form";
import InputField from "@/components/form/input/InputField";
import Button from "@/components/ui/Button";
import { Eye, EyeOff } from "lucide-react";

export default function LoginPage() {
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const router = useRouter();

  const handleSubmit = async () => {
    setError("");
    if (!phone.trim()) { setError("شماره موبایل را وارد کنید"); return; }
    if (!password) { setError("رمز عبور را وارد کنید"); return; }
    setLoading(true);
    try {
      await login({ phone: phone.trim(), password });
      router.push("/");
    } catch (e) {
      setError(e instanceof Error ? e.message : "خطا در ورود");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="rounded-2xl border border-border/50 bg-surface p-6 shadow-lg">
      <div className="mb-6 text-center">
        <h1 className="text-xl font-bold text-text-primary">ورود</h1>
        <p className="mt-1 text-sm text-text-secondary">به حساب کاربری خود وارد شوید</p>
      </div>

      <Form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
            شماره موبایل
          </label>
          <InputField
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="۰۹۹۹۰۰۰۰۰۰۱"
            dir="ltr"
            error={!!error && !phone.trim()}
          />
        </div>

        <div>
          <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
            رمز عبور
          </label>
          <div className="relative">
            <InputField
              type={showPassword ? "text" : "password"}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              dir="ltr"
              error={!!error && !password}
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
            >
              {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          </div>
        </div>

        {error && (
          <p className="text-sm text-danger">{error}</p>
        )}

        <Button type="submit" variant="primary" className="w-full" loading={loading}>
          ورود
        </Button>
      </Form>

      <p className="mt-4 text-center text-sm text-text-secondary">
        حساب کاربری ندارید؟{" "}
        <Link href="/register" className="text-primary hover:underline">
          ثبت‌نام
        </Link>
      </p>
    </div>
  );
}
```

### 5. `client_panel/app/(auth)/register/page.tsx`

```typescript
"use client";
import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import Form from "@/components/form/Form";
import InputField from "@/components/form/input/InputField";
import Button from "@/components/ui/Button";
import { Eye, EyeOff } from "lucide-react";

export default function RegisterPage() {
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [passwordConfirmation, setPasswordConfirmation] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const router = useRouter();

  const handleSubmit = async () => {
    setError("");
    if (!firstName.trim() || !lastName.trim()) { setError("نام و نام خانوادگی را وارد کنید"); return; }
    if (!phone.trim()) { setError("شماره موبایل را وارد کنید"); return; }
    if (password.length < 6) { setError("رمز عبور باید حداقل ۶ کاراکتر باشد"); return; }
    if (password !== passwordConfirmation) { setError("رمز عبور و تکرار آن مطابقت ندارند"); return; }
    setLoading(true);
    try {
      await register({
        first_name: firstName.trim(),
        last_name: lastName.trim(),
        phone: phone.trim(),
        password,
        password_confirmation: passwordConfirmation,
      });
      router.push("/");
    } catch (e) {
      setError(e instanceof Error ? e.message : "خطا در ثبت‌نام");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="rounded-2xl border border-border/50 bg-surface p-6 shadow-lg">
      <div className="mb-6 text-center">
        <h1 className="text-xl font-bold text-text-primary">ثبت‌نام</h1>
        <p className="mt-1 text-sm text-text-secondary">ایجاد حساب کاربری جدید</p>
      </div>

      <Form onSubmit={handleSubmit} className="space-y-4">
        <div className="flex gap-3">
          <div className="flex-1">
            <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
              نام
            </label>
            <InputField value={firstName} onChange={(e) => setFirstName(e.target.value)} placeholder="علی" />
          </div>
          <div className="flex-1">
            <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
              نام خانوادگی
            </label>
            <InputField value={lastName} onChange={(e) => setLastName(e.target.value)} placeholder="رضایی" />
          </div>
        </div>

        <div>
          <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
            شماره موبایل
          </label>
          <InputField
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="۰۹۹۹۰۰۰۰۰۰۱"
            dir="ltr"
          />
        </div>

        <div>
          <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
            رمز عبور
          </label>
          <div className="relative">
            <InputField
              type={showPassword ? "text" : "password"}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="حداقل ۶ کاراکتر"
              dir="ltr"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
            >
              {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          </div>
        </div>

        <div>
          <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
            تکرار رمز عبور
          </label>
          <InputField
            type={showPassword ? "text" : "password"}
            value={passwordConfirmation}
            onChange={(e) => setPasswordConfirmation(e.target.value)}
            placeholder="رمز عبور را دوباره وارد کنید"
            dir="ltr"
          />
        </div>

        {error && (
          <p className="text-sm text-danger">{error}</p>
        )}

        <Button type="submit" variant="primary" className="w-full" loading={loading}>
          ثبت‌نام
        </Button>
      </Form>

      <p className="mt-4 text-center text-sm text-text-secondary">
        قبلاً ثبت‌نام کرده‌اید؟{" "}
        <Link href="/login" className="text-primary hover:underline">
          ورود
        </Link>
      </p>
    </div>
  );
}
```

### 6. Modify `client_panel/app/layout.tsx`

Add `import { AuthProvider } from "@/hooks/useAuth";` and wrap:
```tsx
<ThemeProvider>
  <AuthProvider>
    <Layout>{children}</Layout>
  </AuthProvider>
</ThemeProvider>
```

## Summary of all changes

| Action | File |
|--------|------|
| CREATE | `lib/auth-service.ts` |
| CREATE | `hooks/useAuth.tsx` |
| CREATE | `app/(auth)/layout.tsx` |
| CREATE | `app/(auth)/login/page.tsx` |
| CREATE | `app/(auth)/register/page.tsx` |
| MODIFY | `app/layout.tsx` — wrap with AuthProvider |
