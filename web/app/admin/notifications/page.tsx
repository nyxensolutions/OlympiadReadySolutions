"use client";

import { useState } from "react";
import { useAuth } from "@clerk/nextjs";

export default function AdminNotificationsPage() {
  const { getToken } = useAuth();
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [category, setCategory] = useState("none");
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [message, setMessage] = useState("");

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title || !body) {
      setMessage("Title and Body are required.");
      setStatus("error");
      return;
    }

    setStatus("loading");
    setMessage("");

    try {
      const token = await getToken();
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/admin/notifications/broadcast`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ 
          title, 
          body,
          categoryId: category !== "none" ? category : undefined 
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.message || "Failed to send broadcast");
      }

      setStatus("success");
      setMessage(data.message || "Broadcast sent successfully!");
      setTitle("");
      setBody("");
    } catch (err: any) {
      setStatus("error");
      setMessage(err.message || "An error occurred.");
    }
  };

  return (
    <div className="max-w-2xl mx-auto py-10 px-4 sm:px-6 lg:px-8">
      <h1 className="text-3xl font-extrabold text-gray-900 mb-8">Broadcast Push Notification</h1>
      
      <div className="bg-white shadow sm:rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">Send Notification to All Users</h3>
          <div className="mt-2 max-w-xl text-sm text-gray-500">
            <p>This will send an immediate push notification to every mobile device registered with OlympiadReady.</p>
          </div>
          
          <form className="mt-5" onSubmit={handleSend}>
            <div className="mb-4">
              <label htmlFor="title" className="block text-sm font-medium text-gray-700">
                Notification Title
              </label>
              <input
                type="text"
                name="title"
                id="title"
                className="mt-1 shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md p-2 border"
                placeholder="New Mock Test Available!"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                disabled={status === "loading"}
              />
            </div>

            <div className="mb-4">
              <label htmlFor="body" className="block text-sm font-medium text-gray-700">
                Notification Body
              </label>
              <textarea
                id="body"
                name="body"
                rows={4}
                className="mt-1 shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md p-2 border"
                placeholder="Class 6 Math Mock Test 4 is now live. Try it out!"
                value={body}
                onChange={(e) => setBody(e.target.value)}
                disabled={status === "loading"}
              />
            </div>

            <div className="mb-6">
              <label htmlFor="category" className="block text-sm font-medium text-gray-700">
                Action Buttons (Optional)
              </label>
              <select
                id="category"
                name="category"
                className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md border"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                disabled={status === "loading"}
              >
                <option value="none">None (Standard Notification)</option>
                <option value="test_alert">"Take Test" & "Dismiss"</option>
                <option value="general_alert">"Open App" & "Dismiss"</option>
              </select>
            </div>

            {message && (
              <div className={`mb-4 p-4 rounded-md ${status === "success" ? "bg-green-50 text-green-800" : "bg-red-50 text-red-800"}`}>
                <p className="text-sm font-medium">{message}</p>
              </div>
            )}

            <button
              type="submit"
              disabled={status === "loading"}
              className={`inline-flex items-center px-4 py-2 border border-transparent font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 ${
                status === "loading" ? "opacity-50 cursor-not-allowed" : ""
              }`}
            >
              {status === "loading" ? "Sending..." : "Send Broadcast"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
