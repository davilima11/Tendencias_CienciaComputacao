const carrinho = [
  { nome: "Caderno", preco: 15 },
  { nome: "Caneta", preco: 3 },
  { nome: "Mochila", preco: 120 },
];

const baratos = carrinho.filter((item) => item.preco < 20);
const nomes = carrinho.map((item) => item.nome);

let total = 0;
for (const item of carrinho) {
  total += item.preco;
}

console.log("Itens:", nomes);
console.log("Itens baratos:", baratos.length);
console.log("Total: R$", total);
