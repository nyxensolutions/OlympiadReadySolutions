"use client";

import { useEffect, useState, useRef } from "react";
import { Bell, Check, Loader2 } from "lucide-react";
import { useAuth } from "@clerk/nextjs";

type Notification = {
  notificationId: string;
  title: string;
  message: string;
  isRead: boolean;
  createdAt: string;
};

export function NotificationsDropdown() {
  const { getToken, isLoaded, isSignedIn } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const unreadCount = notifications.filter(n => !n.isRead).length;

  useEffect(() => {
    if (!isLoaded || !isSignedIn) return;
    
    async function fetchNotifs() {
      try {
        const token = await getToken();
        if (!token) return;
        const res = await fetch("/api/notifications", {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (res.ok) {
          const data = await res.json();
          setNotifications(data);
        }
      } catch (err) {
        console.error("Failed to fetch notifications");
      } finally {
        setLoading(false);
      }
    }
    
    fetchNotifs();
  }, [isLoaded, isSignedIn, getToken]);

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [isOpen]);

  const handleMarkAsRead = async () => {
    if (unreadCount === 0) return;
    try {
      const token = await getToken();
      await fetch("/api/notifications/mark-read", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` }
      });
      setNotifications(prev => prev.map(n => ({ ...n, isRead: true })));
    } catch (e) {
      console.error(e);
    }
  };

  const toggleDropdown = () => {
    const nextState = !isOpen;
    setIsOpen(nextState);
    if (nextState) {
      handleMarkAsRead();
    }
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <button 
        onClick={toggleDropdown}
        className="relative flex h-10 w-10 items-center justify-center rounded-full bg-slate-100 text-slate-600 transition hover:bg-slate-200"
      >
        <Bell className="h-5 w-5" />
        {unreadCount > 0 && (
          <span className="absolute right-0 top-0 flex h-4 w-4 items-center justify-center rounded-full bg-rose-500 text-[10px] font-bold text-white shadow ring-2 ring-white">
            {unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-80 rounded-2xl border border-slate-200 bg-white shadow-xl z-50 overflow-hidden animate-in fade-in slide-in-from-top-2 duration-200">
          <div className="flex items-center justify-between border-b border-slate-100 bg-slate-50 px-4 py-3">
            <h3 className="font-bold text-slate-800">Notifications</h3>
          </div>
          
          <div className="max-h-96 overflow-y-auto">
            {loading ? (
              <div className="flex items-center justify-center p-8">
                <Loader2 className="h-6 w-6 animate-spin text-brand-600" />
              </div>
            ) : notifications.length === 0 ? (
              <div className="p-8 text-center text-sm text-slate-500">
                You have no notifications yet.
              </div>
            ) : (
              <div className="divide-y divide-slate-50">
                {notifications.map(n => (
                  <div key={n.notificationId} className={`p-4 transition ${n.isRead ? "bg-white" : "bg-brand-50/30"}`}>
                    <div className="flex gap-3">
                      <div className={`mt-0.5 h-2 w-2 rounded-full shrink-0 ${n.isRead ? "bg-transparent" : "bg-brand-500"}`} />
                      <div>
                        <h4 className="text-sm font-semibold text-slate-800">{n.title}</h4>
                        <p className="mt-1 text-xs text-slate-600 leading-relaxed">{n.message}</p>
                        <p className="mt-2 text-[10px] text-slate-400">
                          {new Date(n.createdAt).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
