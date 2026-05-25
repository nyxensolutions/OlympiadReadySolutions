"use client";

import { useEffect, useState } from "react";
import { useParams, useSearchParams } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { Printer, Loader2, ArrowLeft } from "lucide-react";
import Link from "next/link";
import Image from "next/image";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5080";

type InvoiceData = {
  id: string;
  type: string;
  subject: string;
  grade: number;
  amount: number;
  date: string;
  orderId?: string;
  paymentId?: string;
  planName?: string;
  startDate?: string;
  endDate?: string;
};

function formatDate(dateStr: string | null | undefined): string {
  if (!dateStr) return "";
  const d = new Date(dateStr);
  if (isNaN(d.getTime())) return dateStr;
  const day = String(d.getDate()).padStart(2, "0");
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const year = d.getFullYear();
  return `${day}/${month}/${year}`;
}

export default function InvoicePage() {
  const { id } = useParams();
  const searchParams = useSearchParams();
  const type = searchParams.get("type"); // "subscription" or "pdf"

  const { getToken, isLoaded } = useAuth();
  const [data, setData] = useState<InvoiceData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!isLoaded || !id || !type) return;

    (async () => {
      try {
        const token = await getToken();
        const res = await fetch(`${API_URL}/api/billing/history`, {
          headers: token ? { Authorization: `Bearer ${token}` } : {}
        });
        
        if (!res.ok) throw new Error("Failed to load invoice");
        
        const history = await res.json();
        let item = null;

        if (type === "subscription") {
          item = history.subscriptions.find((s: any) => s.id === id);
          if (item) {
            setData({
              id: item.id,
              type: "Subject Subscription",
              subject: item.subject,
              grade: item.grade,
              amount: item.amountInPaise ? item.amountInPaise / 100 : 0,
              date: item.startDate,
              orderId: item.razorpayOrderId,
              paymentId: item.razorpayPaymentId,
              planName: item.planName,
              startDate: item.startDate,
              endDate: item.endDate
            });
          }
        } else if (type === "pdf") {
          item = history.pdfPurchases.find((p: any) => p.id === id);
          if (item) {
            setData({
              id: item.id,
              type: "PDF Download",
              subject: item.subject,
              grade: item.grade,
              amount: item.isFree ? 0 : item.amountInPaise / 100,
              date: item.purchasedAt,
              orderId: item.razorpayOrderId,
              paymentId: item.razorpayPaymentId
            });
          }
        }

        if (!item) {
          setError("Invoice not found.");
        }
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    })();
  }, [getToken, isLoaded, id, type]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50">
        <Loader2 className="h-8 w-8 animate-spin text-brand-600" />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center bg-slate-50 gap-4">
        <p className="text-lg font-semibold text-rose-600">{error || "Invoice not found"}</p>
        <Link href="/dashboard" className="text-brand-600 hover:underline">Return to Dashboard</Link>
      </div>
    );
  }

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="min-h-screen bg-slate-50/50 print:bg-white font-sans text-slate-900">
      <div className="mx-auto max-w-3xl p-6 md:py-12 print:p-0 print:py-0">
        
        {/* Controls - Hidden when printing */}
        <div className="mb-8 flex items-center justify-between print:hidden">
          <Link href="/dashboard#purchases" className="inline-flex items-center gap-2 text-sm font-medium text-slate-600 hover:text-slate-900">
            <ArrowLeft className="h-4 w-4" /> Back to Dashboard
          </Link>
          <button
            onClick={handlePrint}
            className="inline-flex items-center gap-2 rounded-lg bg-brand-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-brand-700 transition"
          >
            <Printer className="h-4 w-4" /> Download PDF / Print
          </button>
        </div>

        {/* Invoice Document */}
        <div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm print:border-none print:p-0 print:shadow-none">
          {/* Header */}
          <div className="flex items-start justify-between border-b border-slate-100 pb-8">
            <div className="flex items-center gap-3">
              <div className="relative h-12 w-12 shrink-0">
                <Image src="/logo.png" alt="OlympiadReady" fill className="object-contain" />
              </div>
              <div>
                <h1 className="text-2xl font-bold tracking-tight text-slate-900">OlympiadReady</h1>
                <p className="text-sm text-slate-500">olympiadready.com</p>
              </div>
            </div>
            <div className="text-right">
              <h2 className="text-3xl font-light text-slate-300">INVOICE</h2>
              <p className="mt-2 text-sm font-medium text-slate-900">#{data.id.substring(0, 8).toUpperCase()}</p>
              <p className="text-sm text-slate-500">Date: {formatDate(data.date)}</p>
            </div>
          </div>

          {/* Details */}
          <div className="mt-8 flex flex-col sm:flex-row sm:justify-between gap-6">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">Billed To</p>
              <p className="text-sm font-medium text-slate-900">Registered User</p>
            </div>
            {data.orderId && data.orderId !== "FREE" && (
              <div className="sm:text-right">
                <p className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">Payment Details</p>
                <p className="text-sm text-slate-600">Order ID: {data.orderId}</p>
                {data.paymentId && <p className="text-sm text-slate-600">Payment ID: {data.paymentId}</p>}
              </div>
            )}
          </div>

          {/* Items */}
          <div className="mt-12">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-slate-200 text-slate-500">
                  <th className="pb-3 font-semibold uppercase tracking-wider">Description</th>
                  <th className="pb-3 text-right font-semibold uppercase tracking-wider">Amount</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                <tr>
                  <td className="py-4">
                    <p className="font-semibold text-slate-900">{data.type} - Class {data.grade} {data.subject}</p>
                    {data.type === "Subject Subscription" ? (
                      <div className="mt-1 text-xs text-slate-500 space-y-1">
                        {(() => {
                          const start = data.startDate ? new Date(data.startDate) : null;
                          const end = data.endDate ? new Date(data.endDate) : null;
                          let planCycle = "Monthly";
                          if (start && end) {
                            const diffDays = Math.ceil(Math.abs(end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24));
                            if (diffDays > 300) planCycle = "Yearly";
                          }
                          return (
                            <>
                              <p><span className="font-semibold text-slate-700">Plan:</span> {planCycle} Subject Unlock</p>
                              <p><span className="font-semibold text-slate-700">Validity:</span> {formatDate(data.startDate)} to {formatDate(data.endDate)}</p>
                            </>
                          );
                        })()}
                      </div>
                    ) : (
                      data.planName && (
                        <p className="mt-1 text-xs text-slate-500">Plan: {data.planName}</p>
                      )
                    )}
                  </td>
                  <td className="py-4 text-right font-medium text-slate-900">
                    ₹{data.amount.toFixed(2)}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* Total */}
          <div className="mt-8 flex justify-end border-t border-slate-200 pt-6">
            <div className="w-full max-w-sm">
              <div className="flex justify-between text-base font-bold text-slate-900">
                <span>Total Amount Paid</span>
                <span>₹{data.amount.toFixed(2)}</span>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="mt-16 text-center text-xs text-slate-500 print:mt-32">
            <p>Thank you for choosing OlympiadReady!</p>
            <p className="mt-1">If you have any questions concerning this invoice, please contact support.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
