<script setup>
import { ref, nextTick } from 'vue'
import Navbar from '../components/Navbar.vue'
import ChatList from '../components/ChatList.vue'

const userInput = ref('')
const messages = ref([])
const chatBox = ref(null)
const loading = ref(false)

async function sendMessage() {
    const userMsg = userInput.value.trim()
    if (!userMsg) return

    messages.value.push({ sender: 'user', text: userMsg })
    userInput.value = ''
    loading.value = true

    const token = localStorage.getItem('token')

    try {
        const response = await fetch('http://localhost:8001/chat/stream', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ user_message: userMsg }),
        })

        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)
        if (!response.body) throw new Error('No response body')

        const reader = response.body.getReader()
        const decoder = new TextDecoder('utf-8')
        let botMsg = ''

        // Create initial bot message object
        messages.value.push({ sender: 'bot', text: botMsg })
        const botMessageIndex = messages.value.length - 1

        let buffer = ''

        while (true) {
            const { value, done } = await reader.read()
            if (done) break

            buffer += decoder.decode(value, { stream: true })

            // Split by newline but keep incomplete chunks
            const lines = buffer.split('\n')
            buffer = lines.pop() || ''  // Save incomplete chunk for next iteration

            for (const line of lines) {
                if (!line.trim()) continue

                try {
                    const parsed = JSON.parse(line)
                    const delta = parsed.choices?.[0]?.delta?.content

                    if (delta) {
                        botMsg += delta
                        messages.value[botMessageIndex].text = botMsg

                        await nextTick()
                        chatBox.value.scrollTop = chatBox.value.scrollHeight
                    }
                } catch (e) {
                    console.warn('Failed to parse line:', line, e)
                }
            }
        }

        // Process any remaining buffer
        if (buffer.trim()) {
            try {
                const parsed = JSON.parse(buffer)
                const delta = parsed.choices?.[0]?.delta?.content
                if (delta) {
                    botMsg += delta
                    messages.value[botMessageIndex].text = botMsg
                }
            } catch (e) {
                console.warn('Failed to parse final buffer:', buffer, e)
            }
        }

        // after the `while(true)` loop ends:
        const saveResponse = await fetch('http://localhost:8001/chat', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ user_message: userMsg }),
        })
        // you can capture the returned chat_id if needed:
        const { chat_id } = await saveResponse.json()
    } catch (error) {
        console.error('Fetch error:', error)
        messages.value.push({
            sender: 'bot',
            text: '⚠️ Error fetching response. Please try again.'
        })
    } finally {
        loading.value = false
    }
}
</script>

<template>
    <Navbar />
    <div class="flex h-screen">
        <ChatList />
        <main class="flex-1 flex flex-col p-4">
            <div class="flex flex-col h-screen max-w-2xl mx-auto p-4">
                <div class="flex-1 overflow-y-auto space-y-4 mb-4" ref="chatBox">
                    <div v-for="(msg, idx) in messages" :key="idx"
                        :class="msg.sender === 'user' ? 'text-right' : 'text-left'">
                        <p class="inline-block bg-gray-100 text-gray-800 p-2 rounded" v-html="msg.text"></p>
                    </div>
                </div>

                <form @submit.prevent="sendMessage" class="flex">
                    <input v-model="userInput" type="text" class="flex-1 px-4 py-2 border rounded-l focus:outline-none"
                        placeholder="Ask something about anime or manga..." :disabled="loading" required />
                    <button class="bg-indigo-600 text-white px-4 py-2 rounded-r hover:bg-indigo-700 disabled:opacity-50"
                        :disabled="loading">
                        {{ loading ? 'Sending...' : 'Send' }}
                    </button>
                </form>
            </div>
        </main>
    </div>
</template>

<style scoped>
/* No styles yet */
</style>
