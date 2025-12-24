"use client"

import { useState, useRef, useEffect, FormEvent } from "react"

const CHAT_API_URL =
  process.env.NEXT_PUBLIC_CHAT_API || "http://localhost:8000/api/chat"


type ChatMessage = {
  id: number
  role: "user" | "assistant"
  content: string
}

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 1,
      role: "assistant",
      content:
        "สวัสดีค่ะ หนูคือ EVANA Chatbot Demo 💙 ช่วยแนะนำทริปท่องเที่ยวภาคเหนือสำหรับรถ EV ให้ได้นะคะ ลองพิมพ์จังหวัดหรือสไตล์ทริปที่คุณสนใจได้เลยค่ะ",
    },
  ])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const bottomRef = useRef<HTMLDivElement | null>(null)

  // เลื่อน scroll ลงล่างทุกครั้งที่มีข้อความใหม่
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userText = input.trim()
    setInput("")

    // เพิ่มข้อความของผู้ใช้ลงในหน้า
    setMessages((prev) => [
      ...prev,
      { id: prev.length + 1, role: "user", content: userText },
    ])

    setIsLoading(true)

    try {
      // 🔗 ตรงนี้คือจุดยิงไปหา backend (แก้ endpoint ได้ตามจริง)
      const res = await fetch(CHAT_API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userText }),
      })

      if (!res.ok) {
        throw new Error("Request failed")
      }

      const data = await res.json()

      const botReply: string =
        data?.reply ??
        "ตอนนี้หนูยังเชื่อมต่อกับโมเดลไม่ได้ค่ะ ลองตรวจสอบ backend อีกครั้งนะคะ 💙"

      setMessages((prev) => [
        ...prev,
        { id: prev.length + 2, role: "assistant", content: botReply },
      ])
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: prev.length + 2,
          role: "assistant",
          content:
            "มีบางอย่างผิดปกติในการเชื่อมต่อเซิร์ฟเวอร์ค่ะ 😢 ลองเช็กว่า backend ทำงานอยู่หรือยัง แล้วลองใหม่อีกครั้งนะคะ",
        },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-sky-50 via-white to-slate-50">
      <div className="max-w-5xl mx-auto px-4 pt-8 pb-24">
        {/* หัวกล่องแชต */}
        <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
          <div>
            <h1 className="text-2xl sm:text-3xl font-semibold tracking-tight text-slate-900">
              EVANA Chatbot
            </h1>
            <p className="mt-1 text-sm text-slate-500">
              แชตกับผู้ช่วยทริปท่องเที่ยวภาคเหนือสำหรับรถ EV ได้แบบเรียลไทม์
            </p>
          </div>

          <div className="flex items-center gap-2 rounded-full bg-white/80 px-3 py-1 shadow-sm ring-1 ring-sky-100">
            <span className="inline-flex h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-xs font-medium text-slate-500">
              พร้อมให้บริการ
            </span>
          </div>
        </div>

        {/* กล่องแชตหลัก */}
        <div className="rounded-3xl border border-sky-100 bg-white/90 shadow-xl shadow-sky-100/60 backdrop-blur">
          {/* แถบด้านบน */}
          <div className="flex items-center justify-between gap-3 border-b border-slate-100 bg-gradient-to-r from-sky-500 via-sky-400 to-cyan-400 px-6 py-4 rounded-t-3xl">
            <div className="flex items-center gap-3">
              <div className="grid h-10 w-10 place-items-center rounded-2xl bg-white/10 text-white shadow-lg shadow-sky-900/20">
                <span className="text-lg font-semibold">EV</span>
              </div>
              <div>
                <p className="text-sm font-semibold text-white">EVANA Assistant</p>
                <p className="text-xs text-sky-100">
                  แนะนำเส้นทาง • ที่เที่ยว • สถานีชาร์จ • คาเฟ่ • ที่พัก
                </p>
              </div>
            </div>
          </div>

          {/* พื้นที่ข้อความแชต */}
          <div className="h-[60vh] sm:h-[65vh] overflow-y-auto px-4 sm:px-6 py-4 space-y-3 bg-slate-50/60">
            {messages.map((m) => (
              <ChatBubble key={m.id} role={m.role} content={m.content} />
            ))}

            {isLoading && (
              <div className="flex gap-2 items-end">
                <div className="grid h-8 w-8 place-items-center rounded-2xl bg-sky-500 text-white text-xs font-semibold shadow-md shadow-sky-500/30">
                  EV
                </div>
                <div className="rounded-2xl rounded-tl-sm bg-white px-4 py-2 shadow-sm shadow-sky-100 text-xs text-slate-500 flex items-center gap-2">
                  <span className="flex gap-1">
                    <span className="h-1.5 w-1.5 rounded-full bg-sky-300 animate-bounce" />
                    <span className="h-1.5 w-1.5 rounded-full bg-sky-400 animate-bounce delay-75" />
                    <span className="h-1.5 w-1.5 rounded-full bg-sky-500 animate-bounce delay-150" />
                  </span>
                  <span>กำลังคิดคำตอบให้คุณ...</span>
                </div>
              </div>
            )}

            <div ref={bottomRef} />
          </div>

          {/* ช่องพิมพ์ข้อความ */}
          <form
            onSubmit={handleSubmit}
            className="border-t border-slate-100 bg-white/90 px-4 sm:px-6 py-3 rounded-b-3xl"
          >
            <div className="flex items-end gap-2 sm:gap-3">
              <div className="flex-1">
                <textarea
                  rows={1}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="พิมพ์ถามเส้นทาง เช่น “เล่าเส้นทางจากตัวเมืองลำปางไปยังวัดพระธาตุลำปางหลวงให้หน่อย”"
                  className="w-full resize-none rounded-2xl border border-slate-200 bg-slate-50/70 px-3 py-2 text-sm text-slate-800 shadow-sm outline-none ring-sky-200/70 focus:border-sky-400 focus:bg-white focus:ring-2 transition"
                />
                <p className="mt-1 text-[11px] text-slate-400">
                  กด Enter เพื่อส่ง • Shift+Enter เพื่อขึ้นบรรทัดใหม่
                </p>
              </div>

              <button
                type="submit"
                disabled={!input.trim() || isLoading}
                className="inline-flex items-center justify-center rounded-2xl bg-gradient-to-r from-sky-500 to-cyan-500 px-4 py-2 text-sm font-medium text-white shadow-md shadow-sky-500/30 transition hover:-translate-y-0.5 hover:shadow-lg hover:shadow-sky-500/40 disabled:opacity-50 disabled:hover:translate-y-0 disabled:hover:shadow-none"
              >
                {isLoading ? "กำลังส่ง..." : "ส่งข้อความ"}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}

/* ====== Chat Bubble Component ====== */

function ChatBubble({ role, content }: { role: "user" | "assistant"; content: string }) {
  const isUser = role === "user"

  if (isUser) {
    // บับเบิลฝั่งผู้ใช้ (ขวา)
    return (
      <div className="flex justify-end">
        <div className="max-w-[80%] space-y-1 text-right">
          <div className="inline-flex items-center justify-end gap-2">
            <span className="text-[11px] text-slate-400">คุณ</span>
            <div className="grid h-8 w-8 place-items-center rounded-2xl bg-slate-800 text-[11px] font-semibold text-white shadow-md shadow-slate-800/30">
              YOU
            </div>
          </div>
          <div className="inline-block rounded-2xl rounded-tr-sm bg-sky-500 px-4 py-2 text-sm text-white shadow-sm shadow-sky-300/60">
            {content}
          </div>
        </div>
      </div>
    )
  }

  // บับเบิลฝั่งบอต (ซ้าย)
  return (
    <div className="flex gap-2">
      <div className="grid h-8 w-8 place-items-center rounded-2xl bg-sky-500 text-[11px] font-semibold text-white shadow-md shadow-sky-500/40">
        EV
      </div>
      <div className="max-w-[80%] space-y-1">
        <span className="text-[11px] text-slate-400">EVANA</span>
        <div className="inline-block rounded-2xl rounded-tl-sm bg-white px-4 py-2 text-sm text-slate-800 shadow-sm shadow-sky-100">
          {content}
        </div>
      </div>
    </div>
  )
}
