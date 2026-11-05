(function(){
  // WebMCP: expõe ao agente do navegador as mesmas ferramentas do servidor /mcp.
  // Sem suporte no navegador, nada acontece. Tudo só leitura.
  var mc=document.modelContext||navigator.modelContext;
  if(!mc||!mc.registerTool)return;
  var dados=JSON.parse(document.getElementById('dados').textContent);
  function resp(obj){return {content:[{type:'text',text:JSON.stringify(obj)}]}}
  var ferramentas=[
    {name:'ler_perfil',description:'Perfil, resumo e contato de Mateus Fabro',
     inputSchema:{type:'object',properties:{}},execute:async function(){return resp({perfil:dados.perfil,numeros:dados.numeros})}},
    {name:'listar_projetos',description:'Projetos de Mateus Fabro (produtos próprios e trabalho)',
     inputSchema:{type:'object',properties:{}},execute:async function(){return resp(dados.projetos)}},
    {name:'listar_retificacoes',description:'Erros que ele cometeu, com data, número e a regra que ficou',
     inputSchema:{type:'object',properties:{}},execute:async function(){return resp(dados.retificacoes)}},
    {name:'verificar_disponibilidade',description:'Se está aberto a projetos ou vagas, e como falar com ele',
     inputSchema:{type:'object',properties:{}},execute:async function(){return resp(dados.disponibilidade)}}
  ];
  ferramentas.forEach(function(f){try{mc.registerTool(f)}catch(err){}});
})();
