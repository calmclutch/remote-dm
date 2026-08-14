"use client";

import { useEffect, useState } from "react";

const contacts = [
  {
    id: "1",
    name: "¿Hash Brown?",
    username: "@hashbrown",
    status: "Online",
    preview: "outgoing test",
    time: "13:14",
    unread: 2,
  },
  {
    id: "2",
    name: "Alex",
    username: "@alex",
    status: "Offline",
    preview: "See you later.",
    time: "Yesterday",
    unread: 0,
  },
  {
    id: "3",
    name: "Sam",
    username: "@sam",
    status: "Online",
    preview: "Got it 👍",
    time: "Monday",
    unread: 0,
  },
];

const messages = [
  {
    id: 1,
    direction: "incoming",
    content: "hi there",
    time: "18:26",
  },
  {
    id: 2,
    direction: "outgoing",
    content: "Hey! What's up?",
    time: "18:27",
  },
  {
    id: 3,
    direction: "incoming",
    content: "Just testing RemoteDM.",
    time: "18:28",
  },
  {
    id: 4,
    direction: "outgoing",
    content: "It works 🔥",
    time: "18:28",
  },
];

export default function Home() {
  const [selectedContact, setSelectedContact] = useState(contacts[0]);
  const [message, setMessage] = useState("");
  const [darkMode, setDarkMode] = useState(true);

  useEffect(() => {
    const savedTheme = localStorage.getItem("remotedm-theme");

    if (savedTheme === "light") {
      setDarkMode(false);
    }
  }, []);

  function toggleTheme() {
    const newDarkMode = !darkMode;

    setDarkMode(newDarkMode);
    localStorage.setItem(
      "remotedm-theme",
      newDarkMode ? "dark" : "light"
    );
  }

  const theme = {
    page: darkMode
      ? "bg-[#080b12] text-white"
      : "bg-slate-100 text-slate-900",

    sidebar: darkMode
      ? "border-white/10 bg-[#0d111a]"
      : "border-slate-200 bg-white",

    border: darkMode
      ? "border-white/10"
      : "border-slate-200",

    muted: darkMode
      ? "text-white/40"
      : "text-slate-500",

    veryMuted: darkMode
      ? "text-white/25"
      : "text-slate-400",

    hover: darkMode
      ? "hover:bg-white/[0.04]"
      : "hover:bg-slate-50",

    selected: darkMode
      ? "bg-white/[0.08]"
      : "bg-slate-100",

    input: darkMode
      ? "border-white/10 bg-white/[0.04]"
      : "border-slate-200 bg-slate-50",

    chat: darkMode
      ? "bg-[#090c13]"
      : "bg-slate-50",

    composer: darkMode
      ? "border-white/10 bg-[#0b0f17]"
      : "border-slate-200 bg-white",

    incomingMessage: darkMode
      ? "bg-white/[0.07] text-white/90"
      : "bg-white text-slate-800 shadow-sm",
  };

  return (
    <main
      className={`min-h-screen transition-colors duration-200 ${theme.page}`}
    >
      <div className="flex h-screen overflow-hidden">

        {/* Sidebar */}
        <aside
          className={`hidden w-[340px] shrink-0 border-r md:flex md:flex-col ${theme.sidebar}`}
        >
          {/* Logo */}
          <div
            className={`flex h-20 items-center border-b px-6 ${theme.border}`}
          >
            <div className="mr-3 flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-500 text-lg font-bold text-white shadow-lg shadow-indigo-500/20">
              R
            </div>

            <div>
              <h1 className="text-lg font-semibold tracking-tight">
                RemoteDM
              </h1>

              <p className={`text-xs ${theme.muted}`}>
                Private messaging
              </p>
            </div>
          </div>

          {/* Search */}
          <div className="px-5 py-5">
            <div
              className={`flex items-center rounded-xl border px-4 py-3 ${theme.input}`}
            >
              <span className={`mr-3 ${theme.muted}`}>
                ⌕
              </span>

              <input
                className={`w-full bg-transparent text-sm outline-none ${
                  darkMode
                    ? "text-white placeholder:text-white/30"
                    : "text-slate-900 placeholder:text-slate-400"
                }`}
                placeholder="Search conversations"
              />
            </div>
          </div>

          {/* Conversations */}
          <div className="flex-1 overflow-y-auto px-3">
            <p
              className={`px-3 pb-3 text-[11px] font-semibold uppercase tracking-[0.16em] ${theme.veryMuted}`}
            >
              Conversations
            </p>

            {contacts.map((contact) => (
              <button
                key={contact.id}
                onClick={() => setSelectedContact(contact)}
                className={`mb-1 flex w-full items-center rounded-xl p-3 text-left transition ${
                  selectedContact.id === contact.id
                    ? theme.selected
                    : theme.hover
                }`}
              >
                <div className="relative mr-3">
                  <div className="flex h-11 w-11 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-violet-600 text-sm font-semibold text-white">
                    {contact.name.charAt(0)}
                  </div>

                  {contact.status === "Online" && (
                    <span
                      className={`absolute bottom-0 right-0 h-3 w-3 rounded-full border-2 ${
                        darkMode
                          ? "border-[#0d111a]"
                          : "border-white"
                      } bg-emerald-400`}
                    />
                  )}
                </div>

                <div className="min-w-0 flex-1">
                  <div className="flex items-center justify-between">
                    <span className="truncate text-sm font-medium">
                      {contact.name}
                    </span>

                    <span className={`ml-2 text-[10px] ${theme.veryMuted}`}>
                      {contact.time}
                    </span>
                  </div>

                  <div className="mt-1 flex items-center justify-between">
                    <span className={`truncate text-xs ${theme.muted}`}>
                      {contact.preview}
                    </span>

                    {contact.unread > 0 && (
                      <span className="ml-2 flex h-5 min-w-5 items-center justify-center rounded-full bg-indigo-500 px-1.5 text-[10px] font-bold text-white">
                        {contact.unread}
                      </span>
                    )}
                  </div>
                </div>
              </button>
            ))}
          </div>

          {/* Account */}
          <div className={`border-t p-4 ${theme.border}`}>
            <div
              className={`flex items-center rounded-xl p-3 ${
                darkMode ? "bg-white/[0.04]" : "bg-slate-50"
              }`}
            >
              <div
                className={`mr-3 flex h-9 w-9 items-center justify-center rounded-full text-xs font-semibold ${
                  darkMode ? "bg-white/10" : "bg-slate-200"
                }`}
              >
                HB
              </div>

              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium">
                  RemoteDM Owner
                </p>

                <p className="text-xs text-emerald-500">
                  Connected
                </p>
              </div>

              <button
                className={`transition ${
                  darkMode
                    ? "text-white/40 hover:text-white"
                    : "text-slate-400 hover:text-slate-900"
                }`}
              >
                ⋮
              </button>
            </div>
          </div>
        </aside>

        {/* Main chat */}
        <section className={`flex min-w-0 flex-1 flex-col ${theme.chat}`}>

          {/* Header */}
          <header
            className={`flex h-20 shrink-0 items-center border-b px-5 md:px-8 ${theme.border}`}
          >
            <div className="mr-3 flex h-11 w-11 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-violet-600 font-semibold text-white">
              {selectedContact.name.charAt(0)}
            </div>

            <div className="min-w-0 flex-1">
              <h2 className="truncate font-semibold">
                {selectedContact.name}
              </h2>

              <p className={`text-xs ${theme.muted}`}>
                {selectedContact.status}
              </p>
            </div>

            {/* Theme button */}
            <button
              onClick={toggleTheme}
              title={
                darkMode
                  ? "Switch to light mode"
                  : "Switch to dark mode"
              }
              className={`mr-2 flex h-10 w-10 items-center justify-center rounded-xl text-lg transition ${
                darkMode
                  ? "text-yellow-300 hover:bg-white/[0.06]"
                  : "text-indigo-600 hover:bg-slate-200"
              }`}
            >
              {darkMode ? "☀" : "☾"}
            </button>

            <button
              className={`mr-2 rounded-xl p-3 transition ${
                darkMode
                  ? "text-white/50 hover:bg-white/[0.06] hover:text-white"
                  : "text-slate-400 hover:bg-slate-200 hover:text-slate-900"
              }`}
            >
              ⌕
            </button>

            <button
              className={`rounded-xl p-3 transition ${
                darkMode
                  ? "text-white/50 hover:bg-white/[0.06] hover:text-white"
                  : "text-slate-400 hover:bg-slate-200 hover:text-slate-900"
              }`}
            >
              ⋮
            </button>
          </header>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-5 py-8 md:px-10">
            <div className="mx-auto flex max-w-3xl flex-col gap-3">

              <div className="my-3 flex items-center gap-4">
                <div
                  className={`h-px flex-1 ${
                    darkMode ? "bg-white/10" : "bg-slate-200"
                  }`}
                />

                <span
                  className={`text-[10px] uppercase tracking-widest ${theme.veryMuted}`}
                >
                  Today
                </span>

                <div
                  className={`h-px flex-1 ${
                    darkMode ? "bg-white/10" : "bg-slate-200"
                  }`}
                />
              </div>

              {messages.map((item) => {
                const outgoing = item.direction === "outgoing";

                return (
                  <div
                    key={item.id}
                    className={`flex ${
                      outgoing ? "justify-end" : "justify-start"
                    }`}
                  >
                    <div
                      className={`flex max-w-[75%] flex-col ${
                        outgoing ? "items-end" : "items-start"
                      }`}
                    >
                      <div
                        className={`rounded-2xl px-4 py-3 text-sm leading-6 ${
                          outgoing
                            ? "rounded-br-md bg-indigo-500 text-white"
                            : `rounded-bl-md ${theme.incomingMessage}`
                        }`}
                      >
                        {item.content}
                      </div>

                      <span
                        className={`mt-1 px-1 text-[10px] ${theme.veryMuted}`}
                      >
                        {item.time}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Composer */}
          <div className={`border-t p-4 md:p-5 ${theme.composer}`}>
            <form
              onSubmit={(event) => {
                event.preventDefault();

                if (!message.trim()) {
                  return;
                }

                setMessage("");
              }}
              className="mx-auto flex max-w-3xl items-end gap-3"
            >
              <button
                type="button"
                className={`mb-1 flex h-11 w-11 shrink-0 items-center justify-center rounded-xl text-xl transition ${
                  darkMode
                    ? "text-white/40 hover:bg-white/[0.06] hover:text-white"
                    : "text-slate-400 hover:bg-slate-100 hover:text-slate-900"
                }`}
              >
                +
              </button>

              <div
                className={`flex min-h-12 flex-1 items-center rounded-2xl border px-4 transition focus-within:border-indigo-500/50 ${
                  darkMode
                    ? "border-white/10 bg-white/[0.04] focus-within:bg-white/[0.06]"
                    : "border-slate-200 bg-slate-50 focus-within:bg-white"
                }`}
              >
                <input
                  value={message}
                  onChange={(event) => setMessage(event.target.value)}
                  placeholder={`Message ${selectedContact.name}`}
                  className={`w-full bg-transparent py-3 text-sm outline-none ${
                    darkMode
                      ? "text-white placeholder:text-white/25"
                      : "text-slate-900 placeholder:text-slate-400"
                  }`}
                />
              </div>

              <button
                type="submit"
                className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-indigo-500 font-semibold text-white shadow-lg shadow-indigo-500/20 transition hover:bg-indigo-400 active:scale-95"
              >
                ↑
              </button>
            </form>
          </div>
        </section>
      </div>
    </main>
  );
}