<template>
    <div class="flex flex-col justify-center items-center h-screen space-y-6 max-w-sm mx-auto px-4">
        <h1 class="text-3xl font-bold">Login to OtakuBhai</h1>

        <form @submit.prevent="handleSubmit" class="w-full space-y-4">
            <div>
                <label for="email" class="block mb-1 font-medium">Email</label>
                <input id="email" type="email" v-model="email" required placeholder="you@example.com"
                    class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>

            <div>
                <label for="password" class="block mb-1 font-medium">Password</label>
                <input id="password" type="password" v-model="password" required placeholder="Your password"
                    class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>

            <button type="submit" class="w-full bg-indigo-600 text-white py-2 rounded hover:bg-indigo-700 transition">
                Login
            </button>
        </form>
        <div v-if="errorMsg" class="text-red-600 text-sm font-medium text-center">
            {{ errorMsg }}
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { loginUser } from '../api/api.js'

const email = ref('')
const password = ref('')
const router = useRouter()
const errorMsg = ref('')

async function handleSubmit() {
    try {
        const result = await loginUser(email.value, password.value)
        localStorage.setItem('token', result.access_token)
        router.push('/chat')
    } catch (err) {
        errorMsg.value = 'Invalid credentials. Please try again.'
        console.error(err)
    }
}
</script>


<style scoped></style>
