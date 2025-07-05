<template>
    <aside class="w-64 bg-gray-100 p-4 overflow-y-auto">
        <h2 class="font-bold mb-4">Your Chats</h2>
        <ul class="space-y-2">
            <li v-for="chat in chats" :key="chat.chat_id" @click="openChat(chat.chat_id)"
                class="cursor-pointer hover:bg-gray-200 px-2 py-1 rounded">
                {{ chat.title }}
            </li>
        </ul>
    </aside>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const chats = ref([])
const router = useRouter()

async function fetchChats() {
    const token = localStorage.getItem('token')
    const res = await fetch(`http://localhost:8001/chat?skip=0&limit=50`, {
        headers: { Authorization: `Bearer ${token}` }
    })
    chats.value = await res.json()
}

function openChat(chatId) {
    router.push({ name: 'Chat', query: { id: chatId } })
}

onMounted(fetchChats)
</script>
