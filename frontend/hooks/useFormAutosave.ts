'use client';

import { useEffect, useRef, useCallback } from 'react';

interface UseFormAutosaveOptions<T> {
  key: string;
  data: T;
  debounceMs?: number;
}

interface AutosaveState<T> {
  data: T;
  savedAt: string;
}

export function useFormAutosave<T>({ key, data, debounceMs = 1000 }: UseFormAutosaveOptions<T>) {
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const storageKey = `form-autosave:${key}`;

  // Save data to localStorage with debounce
  useEffect(() => {
    if (timerRef.current) clearTimeout(timerRef.current);

    timerRef.current = setTimeout(() => {
      try {
        const state: AutosaveState<T> = {
          data,
          savedAt: new Date().toISOString(),
        };
        localStorage.setItem(storageKey, JSON.stringify(state));
      } catch {
        // Ignore storage errors (e.g., private browsing)
      }
    }, debounceMs);

    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [data, storageKey, debounceMs]);

  const getDraft = useCallback((): AutosaveState<T> | null => {
    try {
      const raw = localStorage.getItem(storageKey);
      if (!raw) return null;
      return JSON.parse(raw) as AutosaveState<T>;
    } catch {
      return null;
    }
  }, [storageKey]);

  const clearDraft = useCallback(() => {
    try {
      localStorage.removeItem(storageKey);
    } catch {
      // Ignore
    }
  }, [storageKey]);

  return { getDraft, clearDraft };
}
