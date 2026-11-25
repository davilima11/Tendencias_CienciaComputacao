const botao = document.querySelector("#enviar");
const campo = document.querySelector("#nome");
const resposta = document.querySelector("#resposta");

botao.addEventListener("click", () => {
  const nome = campo.value;
  resposta.innerHTML = "Olá, " + nome + "!";
});
