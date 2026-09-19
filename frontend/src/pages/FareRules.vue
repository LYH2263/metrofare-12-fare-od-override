<script setup>
import { onMounted, ref } from 'vue'
import { delJSON, getJSON, postJSON } from '../api'

const items = ref([])
const flats = ref([])
const stations = ref([])
const start = ref('')
const end = ref('')
const price = ref('')
const error = ref('')
const trialStart = ref('')
const trialEnd = ref('')
const trial = ref(null)

const reloadFlats = async () => { flats.value = (await getJSON('/api/flat-fares')).items }

onMounted(async () => {
  items.value = (await getJSON('/api/fare-rules')).items
  stations.value = (await getJSON('/api/stations')).items
  await reloadFlats()
  if (stations.value.length >= 2) {
    start.value = stations.value[0].code
    end.value = stations.value[1].code
    trialStart.value = stations.value[0].code
    trialEnd.value = stations.value[1].code
  }
})

const add = async () => {
  error.value = ''
  try {
    await postJSON('/api/flat-fares', { start: start.value, end: end.value, price: Number(price.value) })
    price.value = ''
    await reloadFlats()
  } catch (e) {
    error.value = '登记失败：该起终点对可能已存在，或输入无效'
  }
}

const remove = async (id) => {
  error.value = ''
  try {
    await delJSON(`/api/flat-fares/${id}`)
    await reloadFlats()
  } catch (e) {
    error.value = '删除失败'
  }
}

// 只读试算：persist=false，不落库
const runTrial = async () => {
  trial.value = await postJSON('/api/quote', { start: trialStart.value, end: trialEnd.value, persist: false })
}
</script>

<template>
  <div class="page"><h1>票价阶梯(按站数)</h1>
    <table><thead><tr><th>最多站数</th><th>票价</th></tr></thead>
      <tbody><tr v-for="r in items" :key="r.id"><td>{{ r.max_hops ?? '以上' }}</td><td>{{ r.price }}</td></tr></tbody></table>

    <h1>点对点一口价</h1>
    <div class="panel">
      <select v-model="start"><option v-for="s in stations" :key="s.code" :value="s.code">{{ s.name }}</option></select>
      →
      <select v-model="end"><option v-for="s in stations" :key="s.code" :value="s.code">{{ s.name }}</option></select>
      <input v-model="price" type="number" min="0" step="0.5" placeholder="一口价" style="width:7rem" />
      <button @click="add">登记</button>
      <p v-if="error" class="muted">{{ error }}</p>
    </div>
    <table v-if="flats.length"><thead><tr><th>起点</th><th>终点</th><th>一口价</th><th></th></tr></thead>
      <tbody><tr v-for="f in flats" :key="f.id">
        <td>{{ f.start_code }}</td><td>{{ f.end_code }}</td><td>{{ f.price }}</td>
        <td><button @click="remove(f.id)">删除</button></td>
      </tr></tbody></table>
    <p v-else class="muted">暂无一口价，全部按站数套分段表。</p>

    <h1>试算(只读)</h1>
    <div class="panel">
      <select v-model="trialStart"><option v-for="s in stations" :key="s.code" :value="s.code">{{ s.name }}</option></select>
      →
      <select v-model="trialEnd"><option v-for="s in stations" :key="s.code" :value="s.code">{{ s.name }}</option></select>
      <button @click="runTrial">试算</button>
    </div>
    <div v-if="trial" class="panel">
      <template v-if="trial.reachable">
        <p>途经 {{ trial.path.join(' → ') }} · {{ trial.hops }} 站</p>
        <p v-if="trial.via_flat">一口价 <span class="hero-num">¥{{ trial.fare }}</span>
          <span class="muted">（分段参考价 ¥{{ trial.segment_fare }}）</span></p>
        <p v-else>分段票价 <span class="hero-num">¥{{ trial.fare }}</span></p>
      </template>
      <p v-else class="muted">不可达</p>
    </div>
  </div>
</template>
