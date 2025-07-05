<template>
    <nav class="bg-gray-800 text-white px-4 py-2 flex justify-between items-center">
        <div class="text-xl font-semibold">OtakuBhai</div>
        <button @click="logout" class="bg-red-600 hover:bg-red-700 px-3 py-1 rounded">
            Logout
        </button>
    </nav>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
function logout() {
    localStorage.removeItem('token')
    router.push({ name: 'Login' })
}
</script>
