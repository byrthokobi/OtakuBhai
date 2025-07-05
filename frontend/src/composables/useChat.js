import { ref, nextTick } from "vue";

export function useChat() {
  const messages = ref([]);
  const currentChatId = ref(null);
  const loading = ref(false);
  const chatBox = ref(null);
  const error = ref(null);

  async function sendMessage(userMsg) {
    if (!userMsg.trim()) return;

    loading.value = true;
    error.value = null;

    try {
      // 1. Add user message
      messages.value.push({ sender: "user", text: userMsg });
      await nextTick();
      chatBox.value.scrollTop = chatBox.value.scrollHeight;

      // 2. Stream bot response
      const token = localStorage.getItem("token");
      const streamRes = await fetch("http://localhost:8001/chat/stream", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_message: userMsg,
          chat_id: currentChatId.value, // Include existing chat ID if any
        }),
      });

      if (!streamRes.ok) {
        throw new Error(`HTTP error! status: ${streamRes.status}`);
      }

      const reader = streamRes.body.getReader();
      const decoder = new TextDecoder();
      let botMsg = "";
      let buffer = "";

      // Create initial bot message
      messages.value.push({ sender: "bot", text: botMsg });
      const botMsgIndex = messages.value.length - 1;

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        // Process complete JSON objects only
        try {
          const parsed = JSON.parse(buffer);
          const delta = parsed.choices?.[0]?.delta?.content;

          if (delta) {
            botMsg += delta;
            // Directly update the message object
            messages.value[botMsgIndex].text = botMsg;
            buffer = ""; // Clear buffer after successful parse
          }

          await nextTick();
          chatBox.value.scrollTop = chatBox.value.scrollHeight;
        } catch {
          // Incomplete JSON - wait for next chunk
          continue;
        }
      }

      // 3. Persist conversation
      const saveUrl = currentChatId.value
        ? `http://localhost:8001/chat/${currentChatId.value}`
        : "http://localhost:8001/chat";

      const saveRes = await fetch(saveUrl, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          messages: [
            { sender: "user", text: userMsg },
            { sender: "bot", text: botMsg },
          ],
        }),
      });

      const data = await saveRes.json();
      if (!currentChatId.value) {
        currentChatId.value = data.chat_id;
      }
    } catch (err) {
      error.value = err.message;
      console.error("Chat error:", err);
    } finally {
      loading.value = false;
    }
  }

  async function loadChat(chatId) {
    try {
      loading.value = true;
      const token = localStorage.getItem("token");
      const res = await fetch(`http://localhost:8001/chat/${chatId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      messages.value = data.messages;
      currentChatId.value = chatId;
      await nextTick();
      chatBox.value.scrollTop = chatBox.value.scrollHeight;
    } catch (err) {
      error.value = `Failed to load chat: ${err.message}`;
    } finally {
      loading.value = false;
    }
  }
  function newChat() {
    messages.value = [];
    currentChatId.value = null;
  }

  return {
    messages,
    currentChatId,
    loading,
    error,
    chatBox,
    sendMessage,
    newChat,
    loadChat,
  };
}
